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

import logging
from typing import Any, List, Optional, Tuple, TypedDict, cast

from pydbus import SystemBus  # type: ignore
from qtile_extras.widget import GenPollText

logger = logging.getLogger("qtile.upower")
logger.setLevel(logging.INFO)

UPOWER_SERVICE = "org.freedesktop.UPower"

FALLBACK_ICON = "󰂑"
FALLBACK_COLOR = "#666666"
CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"
EMPTY_ICON = "󰁺"


class BatteryInfo(TypedDict):
    percentage: int
    state: str
    charging: bool
    discharging: bool
    full: bool
    critical: bool


BATTERY_STATES = {
    1: "charging",
    2: "discharging",
    3: "empty",
    4: "fully charged",
    5: "pending charge",
    6: "pending discharge",
}


def find_battery_path() -> Optional[str]:
    """Detect UPower battery device path."""
    try:
        bus = SystemBus()
        upower = bus.get(UPOWER_SERVICE, "/org/freedesktop/UPower")
        for dev in upower.EnumerateDevices():
            if "battery" in dev.lower():
                logger.info(f"Battery device found: {dev}")
                return cast(str, dev)
    except Exception as e:
        logger.warning(f"Battery path detection failed: {e}")
    return None


def query_battery(path: str) -> Optional[BatteryInfo]:
    """Query UPower battery device for relevant fields."""
    try:
        bus = SystemBus()
        battery = bus.get(UPOWER_SERVICE, path)
        percent = int(max(0, min(100, battery.Percentage)))
        state = int(battery.State)
        return BatteryInfo(
            percentage=percent,
            state=BATTERY_STATES.get(state, "unknown"),
            charging=state == 1,
            discharging=state == 2,
            full=state == 4,
            critical=percent <= 5,
        )
    except Exception as e:
        logger.warning(f"Failed to query battery info: {e}")
        return None


class UpowerWidget(GenPollText):  # type: ignore
    """Minimal and beautiful battery status widget using UPower and nerd fonts."""

    ICONS: List[Tuple[int, str, str]] = [
        (95, "󰂂", "limegreen"),
        (80, "󰂁", "palegreen"),
        (60, "󰂀", "lightgoldenrodyellow"),
        (40, "󰁿", "tan"),
        (20, "󰁻", "lightsalmon"),
        (5, "󰁻", "red"),
        (0, EMPTY_ICON, "darkred"),
    ]

    def __init__(
        self,
        update_interval: float = 10.0,
        battery_path: Optional[str] = None,
        icons: Optional[List[Tuple[int, str, str]]] = None,
        **config: Any,
    ) -> None:
        self.battery_path = battery_path or find_battery_path()
        if not self.battery_path:
            logger.warning("No battery device found; using fallback display.")

        self.icons = icons or self.ICONS
        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def _icon_color(self, info: BatteryInfo) -> Tuple[str, str]:
        """Determine which icon and color to use for given battery info."""
        pct = info["percentage"]

        if info["full"]:
            icon, color = FULL_ICON, "lime"
        elif info["critical"]:
            icon, color = EMPTY_ICON, "dimgrey"
        else:
            for threshold, icon_base, color_base in self.icons:
                if pct >= threshold:
                    icon, color = icon_base, color_base
                    break
            else:
                icon, color = FALLBACK_ICON, FALLBACK_COLOR

        if info["charging"]:
            icon = f"{CHARGING_ICON} {icon}"

        return icon, color

    def poll(self) -> str:
        """Poll current battery data and render widget string."""
        if not self.battery_path:
            return f'<span foreground="{FALLBACK_COLOR}">{FALLBACK_ICON} N/A</span>'

        info = query_battery(self.battery_path)
        if not info:
            return f'<span foreground="{FALLBACK_COLOR}">{FALLBACK_ICON} N/A</span>'

        icon, color = self._icon_color(info)
        return f'<span foreground="{color}">{icon} {info["percentage"]:3d}%</span>'

    def get_info(self) -> str:
        """Expose detailed battery information."""
        if not self.battery_path:
            return "Battery: N/A"
        info = query_battery(self.battery_path)
        if not info:
            return "Battery: N/A"
        return (
            f"{info['percentage']}% | State: {info['state']} | "
            f"Charging: {info['charging']} | Critical: {info['critical']}"
        )
