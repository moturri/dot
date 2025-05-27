import subprocess
from pathlib import Path
from typing import Optional

from qtile_extras.widget import GenPollText


def run_command(cmd: list, get_output=False):
    try:
        if get_output:
            return subprocess.check_output(
                cmd, text=True, stderr=subprocess.DEVNULL, timeout=1
            ).strip()
        subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=1,
            check=True,
        )
    except (subprocess.SubprocessError, OSError):
        return "" if get_output else None


def fmt(icon: str, val: int, color: str) -> str:
    return f'<span foreground="{color}">{icon}  {val:>3}%</span>'


ICONS = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "tan"),
    (20, "󰃞", "lime"),
    (0, "󰃜", "dimgrey"),
]


class BrilloWidget(GenPollText):
    def __init__(self, update_interval=0.5, step=5, **config):
        self.step = step
        self.device = next((p for p in Path("/sys/class/backlight").iterdir()), None)
        self.max_brightness = self._get_max_brightness()
        self.has_brillo = bool(run_command(["which", "brillo"], True))
        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def _get_max_brightness(self) -> int:
        if not self.device:
            return 0
        try:
            return int((self.device / "max_brightness").read_text())
        except (OSError, ValueError):
            return 0

    def _get_current(self) -> Optional[int]:
        if not self.device or self.max_brightness <= 0:
            return None
        try:
            current = int((self.device / "brightness").read_text())
            return int((current / self.max_brightness) * 100)
        except (OSError, ValueError):
            return None

    def poll(self) -> str:
        percent = self._get_current()
        if percent is None:
            return '<span foreground="grey">󰳲  --%</span>'
        for level, icon, color in ICONS:
            if percent >= level:
                return fmt(icon, percent, color)
        return fmt(ICONS[-1][1], percent, ICONS[-1][2])

    def cmd_increase(self):
        if self.has_brillo:
            run_command(["brillo", "-A", str(self.step)])

    def cmd_decrease(self):
        if self.has_brillo:
            run_command(["brillo", "-U", str(self.step)])
