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


import os
import shutil
import subprocess
from typing import Any, List, Optional, Tuple

from libqtile.command.base import expose_command
from qtile_extras.widget import GenPollText

ICONS: Tuple[Tuple[int, str, str], ...] = (
    (80, "gold", "󰃠"),
    (60, "orange", "󰃝"),
    (40, "tan", "󰃟"),
    (20, "palegreen", "󰃞"),
    (0, "grey", "󰃜"),
)


def run(command: List[str], timeout: float = 0.5) -> Optional[str]:
    try:
        return subprocess.check_output(
            command, text=True, timeout=timeout, env={"LC_ALL": "C.UTF-8", **os.environ}
        ).strip()
    except Exception:
        return None


def require(command: str) -> None:
    if not shutil.which(command):
        raise RuntimeError(f"Missing dependency: {command}")


class BrightctlWidget(GenPollText):
    """Minimal brightness widget for Qtile using brightnessctl."""

    def __init__(
        self,
        step: int = 5,
        min_brightness: int = 1,
        update_interval: float = 9999.0,
        **config: Any,
    ):
        require("brightnessctl")
        self.step = max(1, min(step, 100))
        self.min_brightness = max(1, min(min_brightness, 100))
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_brightness(self) -> int:
        val = run(["brightnessctl", "get"])
        max_val = run(["brightnessctl", "max"])
        try:
            return (int(val) * 100) // max(int(max_val), 1)
        except Exception:
            return 0

    def _set_brightness(self, percent: int) -> None:
        pct = max(self.min_brightness, min(100, percent))
        run(["brightnessctl", "set", f"{pct}%"])
        self.force_update()

    def _poll(self) -> str:
        b = self._get_brightness()
        for t, color, icon in ICONS:
            if b >= t:
                return f'<span foreground="{color}">{icon}  {b}%</span>'
        return f'<span foreground="grey">󰃜  {b}%</span>'

    @expose_command()
    def increase(self) -> None:
        self._set_brightness(self._get_brightness() + self.step)

    @expose_command()
    def decrease(self) -> None:
        self._set_brightness(self._get_brightness() - self.step)

    @expose_command()
    def refresh(self) -> None:
        self.force_update()
