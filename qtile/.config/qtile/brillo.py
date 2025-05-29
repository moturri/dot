import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, List, Optional, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
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
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
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
            device = next((d for d in devices if device_name in d.name), None)
            if device:
                return device

        for name in DEVICE_PRIORITY:
            device = next((d for d in devices if name in d.name), None)
            if device:
                return device

        return devices[0]  # fallback to first available
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
        """
        Widget to manage and display screen brightness using either 'brillo' or sysfs.

        Args:
            update_interval: Time between polling brightness (seconds).
            step: Increment/decrement step size (percentage).
            device_name: Optional specific backlight device name.
            icons: Optional list of tuples (threshold, icon, color).
            prefer_brillo: Whether to prefer 'brillo' backend over sysfs.
            config: Additional Qtile widget configuration.
        """
        self.step = step
        self.icons = icons or BRIGHTNESS_ICONS

        self.device = find_backlight_device(device_name)
        self.max_brightness = self._get_max_brightness()
        self.has_brillo = bool(shutil.which("brillo"))
        self.backend = self._select_backend(prefer_brillo)

        self._cache: Optional[Tuple[int, float]] = None

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_max_brightness(self) -> int:
        """Get maximum brightness value for sysfs device."""
        if not self.device:
            return 0
        try:
            return int((self.device / "max_brightness").read_text().strip())
        except (OSError, ValueError):
            return 0

    def _select_backend(self, prefer_brillo: bool) -> str:
        """Select backend: 'brillo', 'sysfs', or 'none'."""
        if prefer_brillo and self.has_brillo:
            return "brillo"
        if self.device and self.max_brightness > 0:
            return "sysfs"
        if self.has_brillo:
            return "brillo"
        return "none"

    def _get_brightness_percent(self, force_refresh: bool = False) -> Optional[int]:
        """
        Get current brightness percentage.

        Uses cache if valid unless force_refresh is True.
        """
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
                percent_value = None
        elif self.backend == "sysfs" and self.device:
            try:
                current = int((self.device / "brightness").read_text().strip())
                if self.max_brightness > 0:
                    percent_value = int((current / self.max_brightness) * 100)
            except (OSError, ValueError):
                percent_value = None

        if percent_value is not None:
            self._cache = (percent_value, now)

        return percent_value

    def _set_brightness_percent(self, percent: int) -> bool:
        """Set brightness percentage. Returns True if successful."""
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
                success = False

        if success:
            self._cache = None  # reset cache after successful change

        return success

    def _format_display(self, percent: int) -> str:
        """Format brightness display with icon and color based on thresholds."""
        for threshold, icon, color in self.icons:
            if percent >= threshold:
                return f'<span foreground="{color}">{icon}  {percent:3d}%</span>'
        return f'<span foreground="grey">󰳲  {percent:3d}%</span>'

    def _poll(self) -> str:
        """Poll function for GenPollText widget to update display."""
        if self.backend == "none":
            return '<span foreground="grey">󰳲  N/A</span>'
        percent = self._get_brightness_percent()
        if percent is None:
            return '<span foreground="grey">󰳲  ERR</span>'
        return self._format_display(percent)

    # --- Commands exposed to Qtile ---

    @expose_command()
    def increase(self) -> None:
        """Increase brightness by step."""
        current = self._get_brightness_percent(force_refresh=True)
        if current is not None:
            self._set_brightness_percent(current + self.step)

    @expose_command()
    def decrease(self) -> None:
        """Decrease brightness by step."""
        current = self._get_brightness_percent(force_refresh=True)
        if current is not None:
            self._set_brightness_percent(current - self.step)

    @expose_command()
    def set_percent(self, percent: int) -> None:
        """Set brightness to specific percent."""
        self._set_brightness_percent(percent)

    @expose_command()
    def get_info(self) -> str:
        """Return backend, device name, and max brightness info string."""
        name = self.device.name if self.device else "None"
        return f"Backend: {self.backend} | Device: {name} | Max Brightness: {self.max_brightness}"
