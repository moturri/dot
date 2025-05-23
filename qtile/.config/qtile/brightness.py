from pathlib import Path
from typing import Optional

from utils import cached, fmt, run_command


class Backlight:
    def __init__(self):
        self.device = next((p for p in Path("/sys/class/backlight").iterdir()), None)
        self.max_brightness = self._get_max_brightness()
        self.has_brillo = bool(run_command(["which", "brillo"], True))

    def _get_max_brightness(self) -> int:
        if not self.device:
            return 0
        try:
            return int((self.device / "max_brightness").read_text())
        except (OSError, ValueError):
            return 0

    def get_brightness(self) -> Optional[int]:
        if not self.device or self.max_brightness <= 0:
            return None
        try:
            current = int((self.device / "brightness").read_text())
            return int((current / self.max_brightness) * 100)
        except (OSError, ValueError):
            return None


backlight = Backlight()

ICONS = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "tan"),
    (20, "󰃞", "lime"),
    (0, "󰃜", "dimgrey"),
]


@cached(0.5)
def bright() -> str:
    percent = backlight.get_brightness()
    if percent is None:
        return '<span foreground="grey">󰳲  --%</span>'
    for level, icon, color in ICONS:
        if percent >= level:
            return fmt(icon, percent, color)
    return fmt(ICONS[-1][1], percent, ICONS[-1][2])


def bright_up(qtile=None, step: int = 5):
    if backlight.has_brillo:
        run_command(["brillo", "-A", str(step)])


def bright_down(qtile=None, step: int = 5):
    if backlight.has_brillo:
        run_command(["brillo", "-U", str(step)])

