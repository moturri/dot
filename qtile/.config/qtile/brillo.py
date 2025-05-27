import subprocess
from pathlib import Path
from typing import List, Optional

from libqtile.widget.base import expose_command
from qtile_extras.widget import GenPollText

ICONS = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "tan"),
    (20, "󰃞", "lime"),
    (0, "󰃜", "dimgrey"),
]


def run(cmd: List[str]) -> str:
    """Run a shell command and return output or empty string on failure."""
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=1
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError, TimeoutError):
        return ""


def format_output(icon: str, value: int, color: str) -> str:
    return f'<span foreground="{color}">{icon}  {value:>3}%</span>'


class BrilloWidget(GenPollText):
    def __init__(self, update_interval: float = 0.5, step: int = 5, **config):
        self.step = step
        self.device = self._find_backlight_device()
        self.max_brightness = (
            self._read_int_file(self.device / "max_brightness") if self.device else 0
        )
        self.has_brillo = bool(run(["which", "brillo"]))
        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def _find_backlight_device(self) -> Optional[Path]:
        try:
            for path in Path("/sys/class/backlight").iterdir():
                return path
        except (FileNotFoundError, OSError):
            return None
        return None

    def _read_int_file(self, file: Path) -> Optional[int]:
        try:
            return int(file.read_text().strip())
        except (FileNotFoundError, ValueError, OSError):
            return None

    def _get_current_percent(self) -> Optional[int]:
        if not self.device or self.max_brightness <= 0:
            return None
        current = self._read_int_file(self.device / "brightness")
        if current is None:
            return None
        return int((current / self.max_brightness) * 100)

    def poll(self) -> str:
        percent = self._get_current_percent()
        if percent is None:
            return '<span foreground="grey">󰳲  --%</span>'
        for level, icon, color in ICONS:
            if percent >= level:
                return format_output(icon, percent, color)
        return format_output(ICONS[-1][1], percent, ICONS[-1][2])

    @expose_command()
    def increase(self):
        if self.has_brillo:
            run(["brillo", "-A", str(self.step)])

    @expose_command()
    def decrease(self):
        if self.has_brillo:
            run(["brillo", "-U", str(self.step)])
