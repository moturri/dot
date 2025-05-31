import logging
import shutil
import subprocess
import time
from pathlib import Path
from typing import Any, Final, List, Optional, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText

# Setup logger
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)  # Set to DEBUG for verbose output

# Constants
BRIGHTNESS_STEP: Final[int] = 5
CACHE_TIMEOUT: Final[float] = 0.5
CMD_TIMEOUT: Final[float] = 1.0

DEFAULT_ICONS: Final[List[Tuple[int, str, str]]] = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "tan"),
    (20, "󰃞", "lime"),
    (0, "󰃜", "dimgrey"),
]

DEVICE_PRIORITY: Final[List[str]] = ["intel_backlight", "amdgpu_bl0", "acpi_video0"]


def run_cmd(cmd: List[str]) -> str:
    """
    Execute a shell command and return its output.
    """
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=CMD_TIMEOUT
        ).strip()
    except Exception as e:
        logger.debug(f"[brillo.py] Failed to execute command {cmd}: {e}")
        return ""


def find_backlight_device(device_name: Optional[str] = None) -> Optional[Path]:
    """
    Locate the backlight device path.
    """
    base = Path("/sys/class/backlight")
    if not base.exists():
        return None
    try:
        devices = list(base.iterdir())
        if not devices:
            return None
        if device_name:
            return next((d for d in devices if device_name in d.name), None)
        for name in DEVICE_PRIORITY:
            found = next((d for d in devices if name in d.name), None)
            if found:
                return found
        return devices[0]
    except Exception as e:
        logger.debug(f"[brillo.py] Error finding backlight device: {e}")
        return None


class BrilloWidget(GenPollText):  # type: ignore[misc]
    """
    A Qtile widget to control and display screen brightness.
    """

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
        self.icons = icons or DEFAULT_ICONS
        self.device = find_backlight_device(device_name)
        self.has_brillo = shutil.which("brillo") is not None
        self.max_brightness = self._get_max_brightness() if self.device else 0
        self.backend = self._select_backend(prefer_brillo)
        self._cache: Optional[Tuple[int, float]] = None

        # Pre-sort icons by threshold
        self._icon_map = sorted(self.icons, key=lambda x: x[0], reverse=True)

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_max_brightness(self) -> int:
        """
        Retrieve the maximum brightness value from the device.
        """
        if self.device is None:
            logger.debug("[brillo.py] No backlight device found.")
            return 0
        try:
            return int((self.device / "max_brightness").read_text().strip())
        except Exception as e:
            logger.debug(f"[brillo.py] Error reading max_brightness: {e}")
            return 0

    def _select_backend(self, prefer_brillo: bool) -> str:
        """
        Determine the backend to use for brightness control.
        """
        if prefer_brillo and self.has_brillo:
            return "brillo"
        if self.device and self.max_brightness > 0:
            return "sysfs"
        if self.has_brillo:
            return "brillo"
        return "none"

    def _get_brightness_percent(self, force_refresh: bool = False) -> Optional[int]:
        """
        Get the current brightness percentage.
        """
        now = time.time()
        if not force_refresh and self._cache:
            cached, timestamp = self._cache
            if now - timestamp < CACHE_TIMEOUT:
                return cached

        percent: Optional[int] = None

        if self.backend == "brillo":
            output = run_cmd(["brillo", "-G"])
            try:
                percent = int(float(output))
            except (ValueError, TypeError):
                return None

        elif self.backend == "sysfs" and self.device:
            try:
                current = int((self.device / "brightness").read_text().strip())
                if self.max_brightness > 0:
                    percent = current * 100 // self.max_brightness
            except Exception as e:
                logger.debug(f"[brillo.py] Failed to read brightness from sysfs: {e}")
                return None

        if percent is not None:
            self._cache = (percent, now)

        return percent

    def _set_brightness_percent(self, percent: int) -> bool:
        """
        Set the brightness to a specific percentage.
        """
        percent = max(0, min(100, percent))
        success = False

        if self.backend == "brillo":
            run_cmd(["brillo", "-S", str(percent)])
            success = True

        elif self.backend == "sysfs" and self.device:
            try:
                value = percent * self.max_brightness // 100
                (self.device / "brightness").write_text(str(value))
                success = True
            except Exception as e:
                logger.debug(f"[brillo.py] Failed to write brightness to sysfs: {e}")

        if success:
            self._cache = None

        return success

    def _format_display(self, percent: int) -> str:
        """
        Format the display string with appropriate icon and color.
        """
        for threshold, icon, color in self._icon_map:
            if percent >= threshold:
                return f'<span foreground="{color}">{icon}  {percent:3d}%</span>'
        return f'<span foreground="#888888">󰳲 {percent:3d}%</span>'

    def _poll(self) -> str:
        """
        Poll the current brightness and return the formatted display string.
        """
        if self.backend == "none":
            return '<span foreground="dimgrey">󰳲 N/A</span>'

        percent = self._get_brightness_percent()
        if percent is None:
            return '<span foreground="dimgrey">󰳲 ERR</span>'

        return self._format_display(percent)

    @expose_command()
    def increase(self) -> None:
        """
        Increase the brightness by the defined step.
        """
        current = self._get_brightness_percent(force_refresh=True)
        if current is not None:
            self._set_brightness_percent(current + self.step)

    @expose_command()
    def decrease(self) -> None:
        """
        Decrease the brightness by the defined step.
        """
        current = self._get_brightness_percent(force_refresh=True)
        if current is not None:
            self._set_brightness_percent(current - self.step)

    @expose_command()
    def set_percent(self, percent: int) -> None:
        """
        Set the brightness to a specific percentage.
        """
        self._set_brightness_percent(percent)

    @expose_command()
    def get_info(self) -> str:
        """
        Retrieve information about the brightness backend and device.
        """
        name = self.device.name if self.device else "None"
        return f"Backend: {self.backend} | Device: {name} | Max: {self.max_brightness}"

