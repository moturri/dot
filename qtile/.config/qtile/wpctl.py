import subprocess
from typing import Any, List, Optional, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText

CMD_TIMEOUT = 1.0
VOLUME_STEP = 5

VOLUME_ICONS = {
    "output": ["󰕾", "󰖀", "󰕿", "󰝟"],
    "input": ["󰍬", "󰍬", "󰍬", "󰍭"],
}

VOLUME_THRESHOLDS = [70, 40, 0]
VOLUME_COLORS = ["#ff5555", "#bd93f9", "#50fa7b"]
MUTED_COLOR = "#666666"


def run_wpctl(cmd: List[str]) -> Optional[str]:
    try:
        result = subprocess.run(
            cmd, text=True, capture_output=True, timeout=CMD_TIMEOUT
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except subprocess.TimeoutExpired:
        pass
    return None


def parse_volume(output: str) -> Tuple[int, bool]:
    parts = output.split()
    if len(parts) >= 2:
        try:
            vol = round(float(parts[1]) * 100)
            muted = "[MUTED]" in output
            return vol, muted
        except ValueError:
            pass
    return 0, True


def format_icon(kind: str, volume: int, muted: bool) -> Tuple[str, str]:
    if muted:
        return VOLUME_ICONS[kind][-1], MUTED_COLOR
    for i, threshold in enumerate(VOLUME_THRESHOLDS):
        if volume >= threshold:
            return VOLUME_ICONS[kind][i], VOLUME_COLORS[i]
    return VOLUME_ICONS[kind][-1], VOLUME_COLORS[-1]


class AudioWidget(GenPollText):  # type: ignore
    def __init__(
        self, kind: str = "output", device: str = "@DEFAULT_AUDIO_SINK@", **config: Any
    ) -> None:
        self.kind = kind
        self.device = device
        super().__init__(func=self.poll_volume, update_interval=0.5, **config)

    def get_volume_info(self) -> Tuple[int, bool]:
        output = run_wpctl(["wpctl", "get-volume", self.device])
        if output:
            return parse_volume(output)
        return 0, True

    def poll_volume(self) -> str:
        volume, muted = self.get_volume_info()
        icon, color = format_icon(self.kind, volume, muted)
        return f'<span foreground="{color}">{icon}  {volume}%</span>'

    def set_volume(self, value: str) -> None:
        run_wpctl(["wpctl", "set-volume", self.device, value])

    @expose_command()
    def volume_up(self) -> None:
        vol, _ = self.get_volume_info()
        self.set_volume(f"{min(100, vol + VOLUME_STEP)}%")

    @expose_command()
    def volume_down(self) -> None:
        vol, _ = self.get_volume_info()
        self.set_volume(f"{max(0, vol - VOLUME_STEP)}%")

    @expose_command()
    def toggle_mute(self) -> None:
        run_wpctl(["wpctl", "set-mute", self.device, "toggle"])

    @expose_command()
    def refresh(self) -> None:
        self.poll()


class MicWidget(AudioWidget):
    def __init__(self, **config: Any) -> None:
        super().__init__(kind="input", device="@DEFAULT_AUDIO_SOURCE@", **config)

