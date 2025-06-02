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
    """Minimal brightness control widget."""

    def __init__(self, step: int = 5, **config: Any) -> None:
        self.step = step
        self.device = self._find_device()
        self.has_brillo = bool(shutil.which("brillo"))

        if self.device and not self.has_brillo:
            self.max_brightness = int((self.device / "max_brightness").read_text())

        super().__init__(func=self._poll, update_interval=0.5, **config)

    def _find_device(self) -> Path | None:
        """Find backlight device, prioritizing common ones."""
        base = Path("/sys/class/backlight")
        if not base.exists():
            return None

        devices = list(base.iterdir())
        if not devices:
            return None

        # Check priority devices first
        for priority in ["intel_backlight", "amdgpu_bl0", "acpi_video0"]:
            for device in devices:
                if priority in device.name:
                    return device

        return devices[0]

    def _run_cmd(self, cmd: list[str]) -> str:
        """Execute command and return output."""
        try:
            return subprocess.check_output(
                cmd, text=True, stderr=subprocess.DEVNULL
            ).strip()
        except Exception:
            return ""

    def _get_brightness(self) -> int:
        """Get current brightness percentage."""
        if self.has_brillo:
            output = self._run_cmd(["brillo", "-G"])
            try:
                return int(float(output))
            except ValueError:
                return 0

        if self.device:
            try:
                current = int((self.device / "brightness").read_text())
                return current * 100 // self.max_brightness
            except (OSError, ValueError):
                return 0

        return 0

    def _set_brightness(self, percent: int) -> None:
        """Set brightness to percentage."""
        percent = max(1, min(100, percent))  # Keep minimum at 1% to avoid black screen

        if self.has_brillo:
            self._run_cmd(["brillo", "-S", str(percent)])
        elif self.device:
            try:
                raw_value = percent * self.max_brightness // 100
                (self.device / "brightness").write_text(str(raw_value))
            except OSError:
                pass

    def _poll(self) -> str:
        """Poll brightness and format display."""
        brightness = self._get_brightness()

        # Simple icon/color mapping
        if brightness > 80:
            icon, color = "󰃠", "gold"
        elif brightness > 60:
            icon, color = "󰃝", "orange"
        elif brightness > 40:
            icon, color = "󰃟", "tan"
        elif brightness > 20:
            icon, color = "󰃞", "lime"
        else:
            icon, color = "󰃜", "grey"

        return f'<span foreground="{color}">{icon}  {brightness}%</span>'

    @expose_command()
    def increase(self) -> None:
        """Increase brightness."""
        current = self._get_brightness()
        self._set_brightness(current + self.step)

    @expose_command()
    def decrease(self) -> None:
        """Decrease brightness."""
        current = self._get_brightness()
        self._set_brightness(current - self.step)
