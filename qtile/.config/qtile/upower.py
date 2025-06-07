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

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]

try:
    from pydbus import SystemBus  # type: ignore

    PYDBUS_AVAILABLE = True
except ImportError:
    PYDBUS_AVAILABLE = False

from qtile_extras.widget import GenPollText

logger = logging.getLogger("qtile.upower")
logger.setLevel(logging.INFO)

UPOWER_SERVICE = "org.freedesktop.UPower"
FALLBACK_ICON = "󰂑"
FALLBACK_COLOR = "#666666"
CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"
EMPTY_ICON = "󰁺"
UNKNOWN_ICON = "󰂑"


class BatteryInfo(TypedDict):
    percentage: int
    state: str
    charging: bool
    discharging: bool
    full: bool
    critical: bool
    time_remaining: Optional[int]  # seconds
    health: Optional[float]  # percentage


BATTERY_STATES = {
    0: "unknown",
    1: "charging",
    2: "discharging",
    3: "empty",
    4: "fully charged",
    5: "pending charge",
    6: "pending discharge",
}


def find_battery_path() -> Optional[str]:
    """Detect UPower battery device path with improved error handling."""
    if not PYDBUS_AVAILABLE:
        logger.error("pydbus not available - install with: pip install pydbus")
        return None

    try:
        bus = SystemBus()
        upower = bus.get(UPOWER_SERVICE, "/org/freedesktop/UPower")

        devices = upower.EnumerateDevices()
        for dev in devices:
            dev_str = str(dev).lower()
            # Look for battery devices, prioritize BAT over ADP (adapters)
            if "bat" in dev_str or ("battery" in dev_str and "adp" not in dev_str):
                logger.info(f"Battery device found: {dev}")
                return cast(str, dev)

    except Exception as e:
        logger.warning(f"Battery path detection failed: {e}")

    return None


def query_battery(path: str) -> Optional[BatteryInfo]:
    """Query UPower battery device for comprehensive information."""
    if not PYDBUS_AVAILABLE:
        return None

    try:
        bus = SystemBus()
        battery = bus.get(UPOWER_SERVICE, path)

        # Get basic info with fallbacks
        percent = int(max(0, min(100, getattr(battery, "Percentage", 0))))
        state = int(getattr(battery, "State", 0))

        # Try to get additional info
        time_remaining = None
        health = None

        try:
            # TimeToEmpty or TimeToFull in seconds
            if state == 2:  # discharging
                time_remaining = getattr(battery, "TimeToEmpty", None)
            elif state == 1:  # charging
                time_remaining = getattr(battery, "TimeToFull", None)
        except (AttributeError, TypeError):
            pass

        try:
            # Battery health as percentage
            health = getattr(battery, "Capacity", None)
            if health is not None:
                health = float(health)
        except (AttributeError, TypeError, ValueError):
            pass

        return BatteryInfo(
            percentage=percent,
            state=BATTERY_STATES.get(state, "unknown"),
            charging=state == 1,
            discharging=state == 2,
            full=state == 4,
            critical=percent <= 5,
            time_remaining=time_remaining,
            health=health,
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
        (10, "󰁻", "orange"),
        (5, "󰁻", "red"),
        (0, EMPTY_ICON, "darkred"),
    ]

    def __init__(
        self,
        update_interval: float = 10.0,  # Longer interval for battery
        battery_path: Optional[str] = None,
        icons: Optional[List[Tuple[int, str, str]]] = None,
        show_time: bool = False,
        critical_threshold: int = 10,
        **config: Any,
    ) -> None:
        self.battery_path = battery_path or find_battery_path()
        self.show_time = show_time
        self.critical_threshold = max(5, min(25, critical_threshold))

        if not self.battery_path:
            logger.warning("No battery device found; using fallback display.")

        self.icons = icons or self.ICONS
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _icon_color(self, info: BatteryInfo) -> Tuple[str, str]:
        """Determine which icon and color to use for given battery info."""
        pct = info["percentage"]

        if info["full"]:
            icon, color = FULL_ICON, "lime"
        elif info["critical"] or pct <= self.critical_threshold:
            icon, color = EMPTY_ICON, "red" if pct <= 5 else "orange"
        else:
            # Find appropriate icon/color from thresholds
            icon, color = FALLBACK_ICON, FALLBACK_COLOR
            for threshold, icon_base, color_base in self.icons:
                if pct >= threshold:
                    icon, color = icon_base, color_base
                    break

        # Add charging indicator
        if info["charging"]:
            icon = f"{CHARGING_ICON} {icon}"

        return icon, color

    def _format_time(self, seconds: Optional[int]) -> str:
        """Format time remaining in human readable format."""
        if not seconds or seconds <= 0:
            return ""

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours > 0:
            return f" ({hours}h {minutes:02d}m)"
        else:
            return f" ({minutes}m)"

    def _poll(self) -> str:
        """Poll current battery data and render widget string."""
        if not self.battery_path:
            return f'<span foreground="{FALLBACK_COLOR}">{FALLBACK_ICON} N/A</span>'

        info = query_battery(self.battery_path)
        if not info:
            return f'<span foreground="{FALLBACK_COLOR}">{FALLBACK_ICON} N/A</span>'

        icon, color = self._icon_color(info)

        # Base display
        display = f"{icon} {info['percentage']:3d}%"

        # Add time remaining if requested and available
        if self.show_time and info["time_remaining"]:
            display += self._format_time(info["time_remaining"])

        return f'<span foreground="{color}">{display}</span>'

    @expose_command()
    def get_info(self) -> str:
        """Get detailed battery information."""
        if not self.battery_path:
            return "Battery: N/A"

        info = query_battery(self.battery_path)
        if not info:
            return "Battery: N/A"

        details = [
            f"{info['percentage']}%",
            f"State: {info['state']}",
            f"Charging: {info['charging']}",
            f"Critical: {info['critical']}",
        ]

        if info["time_remaining"]:
            time_str = self._format_time(info["time_remaining"]).strip(" ()")
            details.append(f"Time: {time_str}")

        if info["health"] is not None:
            details.append(f"Health: {info['health']:.1f}%")

        return " | ".join(details)

    @expose_command()
    def toggle_time_display(self) -> None:
        """Toggle showing time remaining in the widget."""
        self.show_time = not self.show_time

    @expose_command()
    def get_health(self) -> str:
        """Get battery health information."""
        if not self.battery_path:
            return "Battery health: N/A"

        info = query_battery(self.battery_path)
        if not info or info["health"] is None:
            return "Battery health: N/A"

        health = info["health"]
        if health >= 80:
            status = "Excellent"
        elif health >= 60:
            status = "Good"
        elif health >= 40:
            status = "Fair"
        else:
            status = "Poor"

        return f"Battery health: {health:.1f}% ({status})"

    @expose_command()
    def is_critical(self) -> bool:
        """Check if battery is in critical state."""
        if not self.battery_path:
            return False

        info = query_battery(self.battery_path)
        return info["critical"] if info else False
