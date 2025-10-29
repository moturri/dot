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
from libqtile.widget.textbox import TextBox

# Thresholds: (percentage, color, icon)
DEFAULT_ICONS: Tuple[Tuple[int, str, str], ...] = (
    (80, "gold", "󰃠"),
    (60, "orange", "󰃝"),
    (40, "tan", "󰃟"),
    (20, "palegreen", "󰃞"),
    (0, "grey", "󰃜"),
)


def run(cmd: List[str], timeout: float = 0.5) -> Optional[str]:
    """Run a command safely and return stripped stdout, or None on failure."""
    try:
        return subprocess.check_output(
            cmd,
            text=True,
            timeout=timeout,
            env={"LC_ALL": "C.UTF-8", **os.environ},
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError, subprocess.TimeoutExpired):
        return None


def require(command: str) -> None:
    """Ensure the required binary is available."""
    if shutil.which(command) is None:
        raise RuntimeError(f"Missing dependency: {command}")


class BrightctlWidget(TextBox):

    def __init__(
        self,
        step: int = 5,
        min_brightness: int = 1,
        device: Optional[str] = None,
        icons: Tuple[Tuple[int, str, str], ...] = DEFAULT_ICONS,
        **config: Any,
    ):
        require("brightnessctl")
        self.step = max(1, min(step, 100))
        self.min_brightness = max(1, min(min_brightness, 100))
        self.device = device
        self.icons = icons
        super().__init__(text=self._generate_text(), **config)  # type: ignore[no-untyped-call]

    def _run_brightctl(self, *args: str) -> Optional[str]:
        """Run brightnessctl with optional device argument."""
        base_cmd = ["brightnessctl"]
        if self.device:
            base_cmd += ["-d", self.device]
        return run(base_cmd + list(args))

    def _get_brightness(self) -> Optional[int]:
        """Return brightness percentage as integer 0–100."""
        current = self._run_brightctl("get")
        maximum = self._run_brightctl("max")
        try:
            cur = int(current or 0)
            max_ = int(maximum or 1)
            if max_ <= 0:
                return None
            return min(100, (cur * 100) // max_)
        except (ValueError, TypeError):
            return None

    def _set_brightness(self, percent: int) -> None:
        """Clamp brightness and apply immediately."""
        pct = max(self.min_brightness, min(100, percent))
        self._run_brightctl("set", f"{pct}%")
        self.update_display()

    def _generate_text(self) -> str:
        """Generate the displayed widget text."""
        brightness = self._get_brightness()
        if brightness is None:
            return '<span foreground="grey">󰃜 N/A</span>'

        color, icon = next(
            ((c, i) for t, c, i in self.icons if brightness >= t),
            ("grey", "󰃜"),
        )
        return f'<span foreground="{color}">{icon}  {brightness}%</span>'

    def update_display(self) -> None:
        """Manually refresh widget display."""
        self.update(self._generate_text())

    @expose_command()
    def increase(self) -> None:
        """Increase brightness by configured step."""
        b = self._get_brightness()
        if b is not None:
            self._set_brightness(b + self.step)

    @expose_command()
    def decrease(self) -> None:
        """Decrease brightness by configured step."""
        b = self._get_brightness()
        if b is not None:
            self._set_brightness(b - self.step)

    @expose_command()
    def refresh(self) -> None:
        """Manually refresh widget display."""
        self.update_display()
