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

    def __init__(self, step: int = 5, **config: Any) -> None:
        self.step = step
        self.device = self._find_device()
        self.has_brillo = bool(shutil.which("brillo"))

        if self.device and not self.has_brillo:
            try:
                self.max_brightness = int((self.device / "max_brightness").read_text())
            except (FileNotFoundError, ValueError):
                self.max_brightness = 100  # fallback default

        super().__init__(func=self._poll, update_interval=0.5, **config)

    def _find_device(self) -> Path | None:
        """Find available backlight device."""
        base = Path("/sys/class/backlight")
        if not base.exists():
            return None

        devices = sorted(base.iterdir(), key=lambda d: d.name)
        for preferred in ["intel_backlight", "amdgpu_bl0", "acpi_video0"]:
            for dev in devices:
                if preferred in dev.name:
                    return dev
        return devices[0] if devices else None

    def _run_cmd(self, cmd: list[str]) -> str:
        """Safely execute a shell command and return its output."""
        try:
            return subprocess.check_output(
                cmd, text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            return ""

    def _get_brightness(self) -> int:
        """Get brightness as a percentage."""
        if self.has_brillo:
            try:
                return int(float(self._run_cmd(["brillo", "-G"])))
            except ValueError:
                return 0

        if self.device:
            try:
                current = int((self.device / "brightness").read_text())
                return (current * 100) // self.max_brightness
            except (OSError, ValueError):
                return 0

        return 0

    def _set_brightness(self, percent: int) -> None:
        """Set brightness to a clamped percentage."""
        percent = max(1, min(100, percent))  # Avoid 0% black screen

        if self.has_brillo:
            self._run_cmd(["brillo", "-S", str(percent)])
        elif self.device:
            try:
                raw = (percent * self.max_brightness) // 100
                (self.device / "brightness").write_text(str(raw))
            except OSError:
                pass

    def _poll(self) -> str:
        """Format brightness value with color and icon."""
        brightness = self._get_brightness()

        if brightness > 80:
            color, icon = self.COLORS["very_high"], self.ICONS["very_high"]
        elif brightness > 60:
            color, icon = self.COLORS["high"], self.ICONS["high"]
        elif brightness > 40:
            color, icon = self.COLORS["medium"], self.ICONS["medium"]
        elif brightness > 20:
            color, icon = self.COLORS["low"], self.ICONS["low"]
        else:
            color, icon = self.COLORS["very_low"], self.ICONS["very_low"]

        return f'<span foreground="{color}">{icon}  {brightness}%</span>'

    @expose_command()
    def increase(self) -> None:
        """Increase brightness."""
        self._set_brightness(self._get_brightness() + self.step)

    @expose_command()
    def decrease(self) -> None:
        """Decrease brightness."""
        self._set_brightness(self._get_brightness() - self.step)
