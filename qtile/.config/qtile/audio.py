import subprocess
from typing import List, Tuple

from libqtile.widget.base import expose_command
from qtile_extras.widget import GenPollText

# Volume change step (in percent)
VOLUME_STEP = 5


def run(cmd: List[str]) -> str:
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=1
        ).strip()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return ""


def parse_volume(output: str) -> Tuple[int, bool]:
    try:
        parts = output.split()
        if len(parts) < 2:
            return 0, True
        # Assuming wpctl get-volume returns a float volume like 0.30, 0.75, etc.
        volume = int(float(parts[1]) * 100)
        muted = "[MUTED]" in output
        return volume, muted
    except (IndexError, ValueError):
        return 0, True


def format_output(icon: str, volume: int, color: str) -> str:
    return f'<span foreground="{color}">{icon}  {volume:>3}%</span>'


class AudioWidget(GenPollText):
    def __init__(
        self,
        device: str = "@DEFAULT_AUDIO_SINK@",
        update_interval: float = 0.5,
        **config,
    ):
        self.device = device
        self.icons = [
            (70, "󰕾", "salmon"),
            (40, "󰖀", "mediumpurple"),
            (0, "󰕿", "springgreen"),
        ]
        self.muted_icon = "󰝟"
        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def poll(self) -> str:
        output = run(["wpctl", "get-volume", self.device])
        if not output:
            return '<span foreground="grey">󰝟  N/A</span>'

        volume, muted = parse_volume(output)

        if muted:
            return format_output(self.muted_icon, volume, "dimgrey")

        for threshold, icon, color in self.icons:
            if volume >= threshold:
                return format_output(icon, volume, color)

        return format_output(self.icons[-1][1], volume, self.icons[-1][2])

    def _get_volume(self) -> int:
        output = run(["wpctl", "get-volume", self.device])
        volume, _ = parse_volume(output)
        return volume

    def _set_volume(self, value: float):
        value = max(0.0, min(value, 1.0))
        run(["wpctl", "set-volume", self.device, f"{value:.2f}"])

    @expose_command()
    def volume_up(self):
        current = self._get_volume()
        self._set_volume((current + VOLUME_STEP) / 100)

    @expose_command()
    def volume_down(self):
        current = self._get_volume()
        self._set_volume((current - VOLUME_STEP) / 100)

    @expose_command()
    def toggle_mute(self):
        run(["wpctl", "set-mute", self.device, "toggle"])


class MicWidget(GenPollText):
    def __init__(
        self,
        device: str = "@DEFAULT_AUDIO_SOURCE@",
        update_interval: float = 0.5,
        **config,
    ):
        self.device = device
        self.icons = [
            (70, "󰍬", "salmon"),
            (40, "󰍬", "mediumpurple"),
            (0, "󰍬", "springgreen"),
        ]
        self.muted_icon = "󰍭"
        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def poll(self) -> str:
        output = run(["wpctl", "get-volume", self.device])
        if not output:
            return '<span foreground="grey">󰍭 N/A</span>'

        volume, muted = parse_volume(output)

        if muted:
            return format_output(self.muted_icon, volume, "dimgrey")

        for threshold, icon, color in self.icons:
            if volume >= threshold:
                return format_output(icon, volume, color)

        return format_output(self.icons[-1][1], volume, self.icons[-1][2])

    def _get_volume(self) -> int:
        output = run(["wpctl", "get-volume", self.device])
        volume, _ = parse_volume(output)
        return volume

    def _set_volume(self, value: float):
        value = max(0.0, min(value, 1.0))
        run(["wpctl", "set-volume", self.device, f"{value:.2f}"])

    @expose_command()
    def volume_up(self):
        current = self._get_volume()
        self._set_volume((current + VOLUME_STEP) / 100)

    @expose_command()
    def volume_down(self):
        current = self._get_volume()
        self._set_volume((current - VOLUME_STEP) / 100)

    @expose_command()
    def toggle_mute(self):
        run(["wpctl", "set-mute", self.device, "toggle"])
