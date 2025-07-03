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


from typing import Any, Optional, Tuple

from libqtile.command.base import expose_command
from qtile_extras.widget import GenPollText
from widget_utils import run_command

CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"
EMPTY_ICON = "󰁺"

BATTERY_ICONS = (
    (95, "󰂂", "limegreen"),
    (80, "󰂁", "palegreen"),
    (60, "󰂀", "khaki"),
    (40, "󰁿", "tan"),
    (20, "󰁻", "lightsalmon"),
    (10, "󰁻", "orange"),
    (5, "󰁻", "red"),
    (0, EMPTY_ICON, "darkred"),
)


class AcpiWidget(GenPollText):  # type: ignore
    """Minimal and efficient ACPI-based battery widget using /sys or acpi fallback."""

    def __init__(
        self,
        update_interval: float = 15.0,
        show_time: bool = False,
        critical_threshold: int = 20,
        battery_path: str = "/sys/class/power_supply/BAT0",
        **config: Any,
    ) -> None:
        self.battery_path = battery_path
        self.show_time = show_time
        self.critical_threshold = max(5, min(25, critical_threshold))
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _poll(self) -> str:
        data = self._get_acpi_data()
        if not data:
            return f'<span foreground="grey">{EMPTY_ICON} N/A</span>'

        pct, state, minutes = data
        icon, color = self._icon_color(pct, state)
        time_str = self._format_time(minutes) if self.show_time and minutes else ""
        return f'<span foreground="{color}">{icon} {pct}%{time_str}</span>'

    def _get_acpi_data(self) -> Optional[Tuple[int, str, Optional[int]]]:
        """Attempt to get battery data from /sys; fallback to `acpi` command."""
        try:
            pct = self._read_int("capacity")
            state = self._read("status").lower()

            minutes = self._calculate_time(state)
            return pct, state, minutes

        except (FileNotFoundError, ValueError, OSError):
            return self._fallback_acpi()

    def _read(self, name: str) -> str:
        with open(f"{self.battery_path}/{name}", "r", encoding="utf-8") as f:
            return f.read().strip()

    def _read_int(self, name: str) -> int:
        return int(self._read(name))

    def _calculate_time(self, state: str) -> Optional[int]:
        """Estimate remaining time from /sys if discharging."""
        if state != "discharging":
            return None

        try:
            charge_now = self._read_int("charge_now")
            charge_full = self._read_int("charge_full")
            current_now = self._read_int("current_now")
            if current_now > 0:
                return int((charge_now / current_now) * 60)
        except FileNotFoundError:
            try:
                energy_now = self._read_int("energy_now")
                energy_full = self._read_int("energy_full")
                power_now = self._read_int("power_now")
                if power_now > 0:
                    return int((energy_now / power_now) * 60)
            except FileNotFoundError:
                return None

        return None

    def _fallback_acpi(self) -> Optional[Tuple[int, str, Optional[int]]]:
        output = run_command(["acpi", "-b"])
        if not output:
            return None

        try:
            parts = output.split(":", 1)[1].strip().split(", ")
            state = parts[0].lower()
            pct = int(parts[1].rstrip("%"))
            minutes = None
            if len(parts) > 2 and ":" in parts[2]:
                h, m = map(int, parts[2].split(":")[:2])
                minutes = h * 60 + m
            return pct, state, minutes
        except (IndexError, ValueError):
            return None

    def _icon_color(self, pct: int, state: str) -> Tuple[str, str]:
        if state == "charging":
            for threshold, icon, color in BATTERY_ICONS:
                if pct >= threshold:
                    return f"{CHARGING_ICON} {icon}", color
            return f"{CHARGING_ICON}{EMPTY_ICON}", "darkgreen"

        if state == "full":
            return FULL_ICON, "lime"

        if pct <= self.critical_threshold:
            return EMPTY_ICON, "red" if pct <= 5 else "orange"

        for threshold, icon, color in BATTERY_ICONS:
            if pct >= threshold:
                return icon, color

        return EMPTY_ICON, "grey"

    def _format_time(self, minutes: int) -> str:
        h, m = divmod(minutes, 60)
        return f" ({h}h {m:02d}m)" if h else f" ({m}m)"

    @expose_command()
    def refresh(self) -> None:
        self.force_update()
