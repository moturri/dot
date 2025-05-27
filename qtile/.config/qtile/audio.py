import subprocess
from typing import List, Optional, Tuple

from qtile_extras.widget import GenPollText

VOLUME_STEP = 5


def run_command(cmd_list: List[str], get_output: bool = False) -> Optional[str]:
    try:
        if get_output:
            return subprocess.check_output(
                cmd_list, text=True, stderr=subprocess.DEVNULL, timeout=1
            ).strip()
        subprocess.run(
            cmd_list,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1,
            check=True,
        )
        return None
    except (subprocess.SubprocessError, OSError):
        return "" if get_output else None


def fmt(icon: str, val: int, color: str) -> str:
    return f'<span foreground="{color}">{icon}  {val:>3}%</span>'


class AudioBaseWidget(GenPollText):
    def __init__(
        self, device_type: str = "sink", update_interval: float = 0.5, **config
    ):
        self.device_id = (
            "@DEFAULT_AUDIO_SOURCE@"
            if device_type == "source"
            else "@DEFAULT_AUDIO_SINK@"
        )
        self.is_mic = device_type == "source"
        self.volume = 0
        self.muted = True
        self.muted_icon = "󰍭" if self.is_mic else "󰝟"

        self.icons: List[Tuple[int, str, str]] = [
            (70, "󰍬" if self.is_mic else "󰕾", "salmon"),
            (40, "󰍬" if self.is_mic else "󰖀", "mediumpurple"),
            (0, "󰍬" if self.is_mic else "󰕿", "springgreen"),
        ]
        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def poll(self) -> str:
        output = run_command(["wpctl", "get-volume", self.device_id], True)
        if output:
            parts = output.split()
            try:
                self.volume = int(float(parts[1]) * 100)
                self.muted = "[MUTED]" in output
            except (IndexError, ValueError):
                pass

        if self.muted:
            return fmt(self.muted_icon, self.volume, "dimgrey")
        for level, icon, color in self.icons:
            if self.volume >= level:
                return fmt(icon, self.volume, color)
        return fmt(self.icons[-1][1], self.volume, self.icons[-1][2])

    def set_volume(self, level: float):
        level = max(0.0, min(level, 1.0))
        run_command(["wpctl", "set-volume", self.device_id, f"{level:.2f}"])

    def cmd_volume_up(self):
        self.set_volume(min((self.volume + VOLUME_STEP) / 100, 1.0))

    def cmd_volume_down(self):
        self.set_volume(max((self.volume - VOLUME_STEP) / 100, 0.0))

    def cmd_toggle_mute(self):
        run_command(["wpctl", "set-mute", self.device_id, "toggle"])


class AudioWidget(AudioBaseWidget):
    def __init__(self, **kwargs):
        super().__init__(device_type="sink", **kwargs)


class MicWidget(AudioBaseWidget):
    def __init__(self, **kwargs):
        super().__init__(device_type="source", **kwargs)
