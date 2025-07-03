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


from typing import Any, Tuple

from libqtile.command.base import expose_command
from qtile_extras.widget import GenPollText

from widget_utils import check_dependency, run_command

ICONS: Tuple[Tuple[int, str, str], ...] = (
    (80, "gold", "󰃠"),
    (60, "orange", "󰃝"),
    (40, "tan", "󰃟"),
    (20, "palegreen", "󰃞"),
    (0, "grey", "󰃜"),
)


class BrightctlWidget(GenPollText):  # type: ignore
    """Minimal, stateless brightness widget using brightnessctl."""

    def __init__(
        self,
        step: int = 5,
        min_brightness: int = 1,
        update_interval: float = 9999.0,
        **config: Any,
    ) -> None:
        check_dependency("brightnessctl")
        self.step = max(1, min(step, 100))
        self.min_brightness = max(1, min(min_brightness, 100))
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_brightness(self) -> int:
        val = run_command(["brightnessctl", "get"])
        max_val = run_command(["brightnessctl", "max"])
        if val is None or max_val is None:
            return 0
        try:
            return (int(val) * 100) // max(int(max_val), 1)
        except (ValueError, TypeError):
            return 0

    def _set_brightness(self, percent: int) -> None:
        clamped = max(self.min_brightness, min(100, percent))
        run_command(["brightnessctl", "set", f"{clamped}%"])
        self.force_update()

    def _icon_and_color(self, brightness: int) -> Tuple[str, str]:
        return next(
            ((color, icon) for t, color, icon in ICONS if brightness >= t),
            ("grey", "󰃜"),
        )

    def _poll(self) -> str:
        b = self._get_brightness()
        color, icon = self._icon_and_color(b)
        return f'<span foreground="{color}">{icon}  {b}%</span>'

    @expose_command()
    def increase(self) -> None:
        self._set_brightness(self._get_brightness() + self.step)

    @expose_command()
    def decrease(self) -> None:
        self._set_brightness(self._get_brightness() - self.step)

    @expose_command()
    def refresh(self) -> None:
        self.force_update()
