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


import os
import shutil
import subprocess
from types import MappingProxyType
from typing import Any, Dict, List, Optional, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText


class BrightctlWidget(GenPollText):  # type: ignore
    """Minimalist brightness widget using brightnessctl with zero idle CPU usage."""

    _LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (80, "gold", "󰃠"),
        (60, "orange", "󰃝"),
        (40, "tan", "󰃟"),
        (20, "palegreen", "󰃞"),
        (0, "grey", "󰃜"),
    )

    _ENV: Dict[str, str] = {**MappingProxyType({"LC_ALL": "C.UTF-8"}), **os.environ}

    __slots__ = (
        "step",
        "min_brightness",
        "_max_brightness",
        "_brightness_before_low",
        "_last_brightness",
        "_last_text",
    )

    def __init__(
        self,
        step: int = 5,
        min_brightness: int = 1,
        update_interval: float = 60.0,
        **config: Any,
    ) -> None:
        if not shutil.which("brightnessctl"):
            raise RuntimeError("brightnessctl not found in PATH")

        self.step = max(1, min(100, step))
        self.min_brightness = max(1, min(100, min_brightness))
        self._brightness_before_low = 50
        self._last_brightness = -1
        self._last_text = ""

        # Read max brightness once
        raw_max = self._cmd(["brightnessctl", "max"])
        try:
            self._max_brightness = max(1, int(raw_max))
        except (ValueError, TypeError):
            self._max_brightness = 100

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _cmd(self, args: List[str], timeout: float = 0.3) -> str:
        """Execute a brightnessctl command with environment and timeout."""
        try:
            return subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=True,
                env=self._ENV,
            ).stdout.strip()
        except (subprocess.SubprocessError, OSError):
            return ""

    def _get_brightness(self) -> int:
        val = self._cmd(["brightnessctl", "get"])
        try:
            percent = (int(val) * 100) // self._max_brightness
            return max(self.min_brightness, min(100, percent))
        except (ValueError, ZeroDivisionError):
            return 0

    def _set_brightness(self, percent: int) -> None:
        self._cmd(
            ["brightnessctl", "set", f"{max(self.min_brightness, min(100, percent))}%"]
        )
        self.force_update()

    def _get_level(self, brightness: int) -> Tuple[str, str]:
        for threshold, color, icon in self._LEVELS:
            if brightness > threshold:
                return color, icon
        return self._LEVELS[-1][1], self._LEVELS[-1][2]

    def _poll(self) -> str:
        current = self._get_brightness()
        if current == self._last_brightness:
            return self._last_text
        self._last_brightness = current
        color, icon = self._get_level(current)
        self._last_text = f'<span foreground="{color}">{icon}  {current}%</span>'
        return self._last_text

    # Public Commands

    @expose_command()
    def increase(self) -> None:
        self._set_brightness(self._get_brightness() + self.step)

    @expose_command()
    def decrease(self) -> None:
        self._set_brightness(self._get_brightness() - self.step)

    @expose_command()
    def set(self, percent: int) -> None:
        self._set_brightness(percent)

    @expose_command()
    def toggle_low(self) -> None:
        current = self._get_brightness()
        if current > 15:
            self._brightness_before_low = current
            self._set_brightness(10)
        else:
            self._set_brightness(self._brightness_before_low)

    @expose_command()
    def set_max(self) -> None:
        self._set_brightness(100)

    @expose_command()
    def set_min(self) -> None:
        self._set_brightness(self.min_brightness)

    @expose_command()
    def refresh(self) -> None:
        self.force_update()

    def get_max_brightness_value(self) -> int:
        return self._max_brightness

    def get_current_raw_brightness(self) -> Optional[int]:
        val = self._cmd(["brightnessctl", "get"])
        try:
            return int(val)
        except ValueError:
            return None


class BrightnessManager:
    """System brightness manager with device detection."""

    _ENV: Dict[str, str] = {**MappingProxyType({"LC_ALL": "C.UTF-8"}), **os.environ}

    @staticmethod
    def get_devices() -> List[str]:
        try:
            result = subprocess.run(
                ["brightnessctl", "--list"],
                capture_output=True,
                text=True,
                timeout=1.0,
                check=True,
                env=BrightnessManager._ENV,
            )

            return [
                line.split("'")[1]
                for line in result.stdout.splitlines()
                if "Device" in line and "'" in line
            ]

        except (subprocess.SubprocessError, OSError):
            return []

    @staticmethod
    def get_device_info(device: Optional[str] = None) -> Dict[str, Any]:
        cmd = ["brightnessctl", "info"]
        if device:
            cmd.extend(["--device", device])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=1.0,
                check=True,
                env=BrightnessManager._ENV,
            )
            return {
                line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip()
                for line in result.stdout.splitlines()
                if ":" in line
            }
        except (subprocess.SubprocessError, OSError):
            return {}

    @staticmethod
    def is_available() -> bool:
        return bool(shutil.which("brightnessctl") and BrightnessManager.get_devices())
