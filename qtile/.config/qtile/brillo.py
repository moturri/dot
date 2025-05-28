import subprocess
import time
from pathlib import Path
from typing import List, Optional

from libqtile.widget.base import expose_command
from qtile_extras.widget import GenPollText


def run(cmd: List[str]) -> str:
    """Run a command and return stdout, or empty string on failure."""
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=1
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError, TimeoutError):
        return ""


def format_output(icon: str, value: int, color: str) -> str:
    """Format widget output string with icon and color."""
    return f'<span foreground="{color}">{icon}  {value:3d}%</span>'


class BrilloWidget(GenPollText):
    """Simple and efficient brightness widget supporting sysfs and brillo."""

    def __init__(
        self,
        update_interval: float = 0.5,
        step: int = 5,
        device_name: Optional[str] = None,
        icons: Optional[List[tuple]] = None,
        prefer_brillo: bool = True,
        **config,
    ):
        self.step = step
        self.device_name = device_name
        self.prefer_brillo = prefer_brillo

        # Icon levels
        self.icons = icons or [
            (80, "󰃠", "gold"),
            (60, "󰃝", "darkorange"),
            (40, "󰃟", "tan"),
            (20, "󰃞", "lime"),
            (0, "󰃜", "dimgrey"),
        ]

        self.device = self._find_backlight_device()
        self.max_brightness = self._get_max_brightness()
        self.has_brillo = bool(run(["which", "brillo"]))
        self.backend = self._select_backend()

        self._last_percent = None
        self._last_check = 0.0
        self._cache_duration = 0.3

        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def _find_backlight_device(self) -> Optional[Path]:
        path = Path("/sys/class/backlight")
        if not path.exists():
            return None

        try:
            devices = list(path.iterdir())
            if self.device_name:
                for d in devices:
                    if self.device_name in d.name:
                        return d
            for name in ["intel_backlight", "acpi_video0", "amdgpu_bl0"]:
                for d in devices:
                    if name in d.name:
                        return d
            return devices[0] if devices else None
        except (OSError, PermissionError):
            return None

    def _get_max_brightness(self) -> int:
        try:
            return int((self.device / "max_brightness").read_text().strip())
        except Exception:
            return 0

    def _read_current_brightness(self) -> Optional[int]:
        try:
            return int((self.device / "brightness").read_text().strip())
        except Exception:
            return None

    def _write_brightness(self, value: int) -> bool:
        try:
            (self.device / "brightness").write_text(
                str(min(value, self.max_brightness))
            )
            return True
        except Exception:
            return False

    def _select_backend(self) -> str:
        if self.prefer_brillo and self.has_brillo:
            return "brillo"
        if self.device and self.max_brightness > 0:
            return "sysfs"
        if self.has_brillo:
            return "brillo"
        return "none"

    def _get_current_percent(self, use_cache=True) -> Optional[int]:
        now = time.time()
        if (
            use_cache
            and self._last_percent
            and (now - self._last_check) < self._cache_duration
        ):
            return self._last_percent

        percent = None
        if self.backend == "brillo":
            output = run(["brillo", "-G"])
            try:
                percent = int(float(output))
            except ValueError:
                pass
        elif self.backend == "sysfs":
            current = self._read_current_brightness()
            if current is not None and self.max_brightness > 0:
                percent = int((current / self.max_brightness) * 100)

        if percent is not None:
            self._last_percent = percent
            self._last_check = now

        return percent

    def poll(self) -> str:
        percent = self._get_current_percent()
        if percent is None:
            return '<span foreground="grey">󰳲  N/A</span>'

        for level, icon, color in self.icons:
            if percent >= level:
                return format_output(icon, percent, color)
        return format_output(self.icons[-1][1], percent, self.icons[-1][2])

    def _change_brightness_percent(self, delta: int) -> bool:
        current = self._get_current_percent(use_cache=False)
        if current is None:
            return False

        new_percent = max(0, min(100, current + delta))
        if self.backend == "brillo":
            return bool(run(["brillo", "-A" if delta > 0 else "-U", str(abs(delta))]))
        elif self.backend == "sysfs":
            new_value = int((new_percent / 100) * self.max_brightness)
            if self._write_brightness(new_value):
                self._last_percent = None
                return True
        return False

    @expose_command()
    def increase(self):
        """Increase brightness."""
        if self.backend != "none":
            self._change_brightness_percent(self.step)

    @expose_command()
    def decrease(self):
        """Decrease brightness."""
        if self.backend != "none":
            self._change_brightness_percent(-self.step)

    @expose_command()
    def set_percent(self, percent: int):
        """Set brightness to a specific percentage."""
        percent = max(0, min(100, percent))
        if self.backend == "brillo":
            run(["brillo", "-S", str(percent)])
        elif self.backend == "sysfs":
            value = int((percent / 100) * self.max_brightness)
            if self._write_brightness(value):
                self._last_percent = None

    @expose_command()
    def get_info(self) -> str:
        """Return backend and device info."""
        device = self.device.name if self.device else "None"
        return f"Backend: {self.backend}, Device: {device}, Brillo: {self.has_brillo}"


# Brightness control helpers
def brillo_up(qtile):
    BrilloWidget.increase()


def brillo_down(qtile):
    BrilloWidget.decrease()
