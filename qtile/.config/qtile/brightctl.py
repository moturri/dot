# MIT License
#
# Copyright (c) 2025 Elton Moturi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import logging
import shutil
import subprocess
from typing import Any, List, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText

logger = logging.getLogger(__name__)

BRIGHTNESS_ICONS: Tuple[Tuple[int, str, str], ...] = (
    (80, "gold", "󰃠"),
    (60, "orange", "󰃝"),
    (40, "tan", "󰃟"),
    (20, "palegreen", "󰃞"),
    (0, "grey", "󰃜"),
)


class BrightctlWidget(GenPollText):  # type: ignore
    """Minimal and efficient brightness widget using brightnessctl."""

    def __init__(
        self,
        step: int = 5,
        min_brightness: int = 1,
        update_interval: float = 9999.0,
        **config: Any,
    ) -> None:
        if not shutil.which("brightnessctl"):
            raise RuntimeError("brightnessctl not found in PATH")

        self.step = max(1, min(step, 100))
        self.min_brightness = max(1, min(min_brightness, 100))
        self._max_brightness = self._get_max_brightness()
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _run(self, args: List[str]) -> str:
        try:
            return subprocess.check_output(args, text=True, timeout=0.5).strip()
        except Exception as e:
            logger.warning("brightnessctl command failed: %s", e)
            return ""

    def _get_max_brightness(self) -> int:
        val = self._run(["brightnessctl", "max"])
        try:
            return max(1, int(val))
        except ValueError:
            logger.error("Invalid max brightness value: %r", val)
            return 100

    def _get_brightness(self) -> int:
        val = self._run(["brightnessctl", "get"])
        try:
            brightness = (int(val) * 100) // self._max_brightness
            logger.debug("Current brightness: %d%%", brightness)
            return brightness
        except (ValueError, ZeroDivisionError):
            logger.warning("Could not read current brightness: %r", val)
            return 0

    def _set_brightness(self, percent: int) -> None:
        clamped = max(self.min_brightness, min(100, percent))
        self._run(["brightnessctl", "set", f"{clamped}%"])
        self.force_update()

    def _icon_and_color(self, brightness: int) -> Tuple[str, str]:
        return next(
            (color, icon)
            for threshold, color, icon in BRIGHTNESS_ICONS
            if brightness >= threshold
        )

    def _poll(self) -> str:
        brightness = self._get_brightness()
        color, icon = self._icon_and_color(brightness)
        return f'<span foreground="{color}">{icon}  {brightness}%</span>'

    @expose_command()
    def increase(self) -> None:
        self._set_brightness(self._get_brightness() + self.step)

    @expose_command()
    def decrease(self) -> None:
        self._set_brightness(self._get_brightness() - self.step)

    @expose_command()
    def refresh(self) -> None:
        self.force_update()
