import subprocess
import time
from pathlib import Path
from typing import Any, List, Optional, Tuple

# Import expose_command with ignore for mypy since it’s not officially exported
from libqtile.widget.base import expose_command  # type: ignore
from qtile_extras.widget import GenPollText

# Constants
BRIGHTNESS_STEP = 5
CACHE_TIMEOUT = 0.3
CMD_TIMEOUT = 1.0

BRIGHTNESS_ICONS: List[Tuple[int, str, str]] = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "tan"),
    (20, "󰃞", "lime"),
    (0, "󰃜", "dimgrey"),
]

DEVICE_PRIORITY: List[str] = ["intel_backlight", "amdgpu_bl0", "acpi_video0"]


def run_cmd(cmd: List[str]) -> str:
    """Run a command safely and return its output, or empty string on failure."""
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=CMD_TIMEOUT
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return ""


def find_backlight_device(device_name: Optional[str] = None) -> Optional[Path]:
    """Detect available backlight device."""
    base = Path("/sys/class/backlight")
    if not base.exists():
        return None

    try:
        devices = list(base.iterdir())
        if not devices:
            return None

        if device_name:
            for d in devices:
                if device_name in d.name:
                    return d

        for name in DEVICE_PRIORITY:
            for d in devices:
                if name in d.name:
                    return d

        return devices[0]  # fallback to the first one found
    except (OSError, PermissionError):
        return None


class BrilloWidget(GenPollText):  # type: ignore[misc]
    def __init__(
        self,
        update_interval: float = 0.5,
        step: int = BRIGHTNESS_STEP,
        device_name: Optional[str] = None,
        icons: Optional[List[Tuple[int, str, str]]] = None,
        prefer_brillo: bool = True,
        **config: Any,
    ) -> None:
        self.step = step
        self.icons: List[Tuple[int, str, str]] = icons or BRIGHTNESS_ICONS

        self.device: Optional[Path] = find_backlight_device(device_name)
        self.max_brightness: int = self._get_max_brightness()
        self.has_brillo: bool = bool(run_cmd(["which", "brillo"]))
        self.backend: str = self._select_backend(prefer_brillo)

        self._cache: Optional[Tuple[int, float]] = None

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_max_brightness(self) -> int:
        if not self.device:
            return 0
        try:
            return int((self.device / "max_brightness").read_text().strip())
        except (OSError, ValueError):
            return 0

    def _select_backend(self, prefer_brillo: bool) -> str:
        if prefer_brillo and self.has_brillo:
            return "brillo"
        if self.device and self.max_brightness > 0:
            return "sysfs"
        if self.has_brillo:
            return "brillo"
        return "none"

    def _get_brightness_percent(self, force_refresh: bool = False) -> Optional[int]:
        now = time.time()
        if not force_refresh and self._cache:
            percent_cached, cached_time = self._cache
            if now - cached_time < CACHE_TIMEOUT:
                return percent_cached

        percent_value: Optional[int] = None

        if self.backend == "brillo":
            output = run_cmd(["brillo", "-G"])
            try:
                percent_value = int(float(output))
            except (ValueError, TypeError):
                pass
        elif self.backend == "sysfs" and self.device:
            try:
                current = int((self.device / "brightness").read_text().strip())
                if self.max_brightness > 0:
                    percent_value = int((current / self.max_brightness) * 100)
            except (OSError, ValueError):
                pass

        if percent_value is not None:
            self._cache = (percent_value, now)

        return percent_value

    def _set_brightness_percent(self, percent: int) -> bool:
        percent = max(0, min(100, percent))
        success = False

        if self.backend == "brillo":
            run_cmd(["brillo", "-S", str(percent)])
            success = True
        elif self.backend == "sysfs" and self.device:
            try:
                value = int((percent / 100) * self.max_brightness)
                (self.device / "brightness").write_text(str(value))
                success = True
            except (OSError, ValueError):
                pass

        if success:
            self._cache = None
        return success

    def _format_display(self, percent: int) -> str:
        for threshold, icon, color in self.icons:
            if percent >= threshold:
                return f'<span foreground="{color}">{icon}  {percent:3d}%</span>'
        return f'<span foreground="grey">󰳲  {percent:3d}%</span>'

    def _poll(self) -> str:
        if self.backend == "none":
            return '<span foreground="grey">󰳲  N/A</span>'
        percent = self._get_brightness_percent()
        if percent is None:
            return '<span foreground="grey">󰳲  ERR</span>'
        return self._format_display(percent)

    # --- Commands exposed to Qtile ---

    @expose_command()
    def increase(self) -> None:
        current = self._get_brightness_percent(force_refresh=True)
        if current is not None:
            self._set_brightness_percent(current + self.step)

    @expose_command()
    def decrease(self) -> None:
        current = self._get_brightness_percent(force_refresh=True)
        if current is not None:
            self._set_brightness_percent(current - self.step)

    @expose_command()
    def set_percent(self, percent: int) -> None:
        self._set_brightness_percent(percent)

    @expose_command()
    def get_info(self) -> str:
        name = self.device.name if self.device else "None"
        return f"Backend: {self.backend} | Device: {name} | Max Brightness: {self.max_brightness}"
