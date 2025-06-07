# Copyright (C) 2025, Elton Moturi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import shutil
import subprocess
from pathlib import Path
from typing import Any

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText


class BrilloWidget(GenPollText):  # type: ignore
    """Minimal brightness control widget using brillo or /sys/class/backlight."""

    COLORS = {
        "very_high": "gold",
        "high": "orange",
        "medium": "tan",
        "low": "palegreen",
        "very_low": "grey",
    }

    ICONS = {
        "very_high": "󰃠",
        "high": "󰃝",
        "medium": "󰃟",
        "low": "󰃞",
        "very_low": "󰃜",
    }

    def __init__(self, step: int = 5, min_brightness: int = 1, **config: Any) -> None:
        self.step = step
        self.min_brightness = max(1, min_brightness)  # Prevent complete darkness
        self.device = self._find_device()
        self.has_brillo = bool(shutil.which("brillo"))
        self.max_brightness = 100  # Default fallback

        if self.device and not self.has_brillo:
            self._init_sysfs_brightness()

        super().__init__(func=self._poll, update_interval=0.5, **config)

    def _init_sysfs_brightness(self) -> None:
        """Initialize sysfs brightness parameters."""
        try:
            max_file = self.device / "max_brightness"
            if max_file.exists():
                self.max_brightness = int(max_file.read_text().strip())
        except (FileNotFoundError, ValueError, OSError):
            self.max_brightness = 100

    def _find_device(self) -> Path | None:
        """Find available backlight device with priority order."""
        base = Path("/sys/class/backlight")
        if not base.exists():
            return None

        try:
            devices = list(base.iterdir())
        except OSError:
            return None

        if not devices:
            return None

        # Priority order for common devices
        priority = ["intel_backlight", "amdgpu_bl", "nvidia_backlight", "acpi_video0"]

        for preferred in priority:
            for dev in devices:
                if preferred in dev.name:
                    return dev

        # Return first available device as fallback
        return sorted(devices, key=lambda d: d.name)[0]

    def _run_cmd(self, cmd: list[str]) -> str:
        """Safely execute command with minimal overhead."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=2, check=False
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except (subprocess.TimeoutExpired, OSError):
            return ""

    def _get_brightness(self) -> int:
        """Get current brightness percentage."""
        if self.has_brillo:
            try:
                output = self._run_cmd(["brillo", "-G"])
                return int(float(output)) if output else 0
            except ValueError:
                return 0

        if self.device:
            try:
                brightness_file = self.device / "brightness"
                if brightness_file.exists():
                    current = int(brightness_file.read_text().strip())
                    return min(100, (current * 100) // self.max_brightness)
            except (OSError, ValueError):
                pass

        return 0

    def _set_brightness(self, percent: int) -> bool:
        """Set brightness with bounds checking. Returns success status."""
        percent = max(self.min_brightness, min(100, percent))

        if self.has_brillo:
            result = self._run_cmd(["brillo", "-S", str(percent)])
            return bool(result or self._run_cmd(["brillo", "-G"]))

        if self.device:
            try:
                brightness_file = self.device / "brightness"
                if brightness_file.exists():
                    raw_value = (percent * self.max_brightness) // 100
                    brightness_file.write_text(str(raw_value))
                    return True
            except OSError:
                pass

        return False

    def _get_brightness_level(self, brightness: int) -> tuple[str, str]:
        """Determine color and icon based on brightness level."""
        if brightness > 80:
            return self.COLORS["very_high"], self.ICONS["very_high"]
        elif brightness > 60:
            return self.COLORS["high"], self.ICONS["high"]
        elif brightness > 40:
            return self.COLORS["medium"], self.ICONS["medium"]
        elif brightness > 20:
            return self.COLORS["low"], self.ICONS["low"]
        else:
            return self.COLORS["very_low"], self.ICONS["very_low"]

    def _poll(self) -> str:
        """Format brightness display with color and icon."""
        brightness = self._get_brightness()
        color, icon = self._get_brightness_level(brightness)

        return f'<span foreground="{color}">{icon}  {brightness}%</span>'

    @expose_command()
    def increase(self) -> None:
        """Increase brightness by step amount."""
        current = self._get_brightness()
        self._set_brightness(current + self.step)

    @expose_command()
    def decrease(self) -> None:
        """Decrease brightness by step amount."""
        current = self._get_brightness()
        self._set_brightness(current - self.step)

    @expose_command()
    def set(self, percent: int) -> None:
        """Set brightness to specific percentage."""
        self._set_brightness(percent)

    @expose_command()
    def toggle_low(self) -> None:
        """Toggle between current brightness and low brightness (useful for battery saving)."""
        current = self._get_brightness()
        if current > 15:
            self._brightness_before_low = current
            self._set_brightness(10)
        else:
            target = getattr(self, "_brightness_before_low", 50)
            self._set_brightness(target)
