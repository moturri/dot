import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from pydbus import SystemBus  # type: ignore[import-untyped]
from qtile_extras.widget import GenPollText

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 5.0
FALLBACK_ICON = "󰂑"
FALLBACK_COLOR = "dimgrey"

UPOWER_SERVICE = "org.freedesktop.UPower"
DEVICE_INTERFACE = "org.freedesktop.UPower.Device"

BATTERY_ICONS: List[Tuple[int, str, str]] = [
    (95, "󰂂", "lime"),
    (80, "󰂁", "springgreen"),
    (60, "󰂀", "palegreen"),
    (40, "󰁿", "orange"),
    (20, "󰁻", "coral"),
    (5, "󰁻", "tomato"),
    (0, "󰁺", "red"),
]

CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"

BATTERY_STATE: Dict[int, str] = {
    1: "charging",
    2: "discharging",
    3: "empty",
    4: "full",
    5: "pending_charge",
    6: "pending_discharge",
}


def find_battery_path() -> Optional[str]:
    """Discover the first available battery path from UPower."""
    try:
        bus = SystemBus()
        upower = bus.get(UPOWER_SERVICE, "/org/freedesktop/UPower")
        devices = upower.EnumerateDevices()
        for dev in devices:
            if "battery" in dev.lower():  # case-insensitive match
                return str(dev)
    except Exception as e:
        logger.warning(f"Failed to find battery path: {e}")
    return None


def get_battery_info(battery_path: str) -> Optional[Dict[str, Any]]:
    """Query battery info from UPower D-Bus."""
    try:
        bus = SystemBus()
        battery = bus.get(UPOWER_SERVICE, battery_path)
        percentage = max(0, min(100, int(battery.Percentage)))
        state = battery.State

        return {
            "percentage": percentage,
            "state": BATTERY_STATE.get(state, "unknown"),
            "is_charging": state == 1,
            "is_discharging": state == 2,
            "is_full": state == 4,
            "is_critical": percentage <= 5,
        }
    except Exception as e:
        logger.warning(f"Failed to query battery info: {e}")
        return None


class UpowerWidget(GenPollText):  # type: ignore[misc]
    """Qtile Battery Widget with UPower backend."""

    def __init__(
        self,
        update_interval: float = 10.0,
        battery_path: Optional[str] = None,
        icons: Optional[List[Tuple[int, str, str]]] = None,
        **config: Any,
    ):
        self.battery_path = battery_path or find_battery_path()
        if not self.battery_path:
            logger.warning("No battery path detected; battery widget will show N/A.")

        self.icons = icons or BATTERY_ICONS
        self._cache: Optional[Tuple[Dict[str, Any], float]] = None

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_battery_info(
        self, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Return cached battery info or query fresh data if stale."""
        now = time.time()
        if not force_refresh and self._cache:
            cached_data, cached_at = self._cache
            if now - cached_at < CACHE_TIMEOUT:
                return cached_data

        fresh_data = get_battery_info(self.battery_path) if self.battery_path else None
        if fresh_data is not None:
            self._cache = (fresh_data, now)

        return fresh_data

    def _get_icon_and_color(self, info: Dict[str, Any]) -> Tuple[str, str]:
        """Return icon and color based on battery info."""
        percent = info["percentage"]

        if info["is_full"]:
            return FULL_ICON, "#32cd32"

        if info["is_critical"]:
            icon = "󰂃" if info["is_charging"] else "󰁺"
            return icon, "#ff0000"

        for threshold, icon, color in self.icons:
            if percent >= threshold:
                if info["is_charging"]:
                    return f"{CHARGING_ICON} {icon}", color
                return icon, color

        return FALLBACK_ICON, FALLBACK_COLOR

    def _format_display(self, info: Dict[str, Any]) -> str:
        """Format widget output string."""
        icon, color = self._get_icon_and_color(info)
        return f'<span foreground="{color}">{icon} {info["percentage"]:3d}%</span>'

    def _poll(self) -> str:
        """Return widget display string."""
        info = self._get_battery_info()
        if not info:
            return f'<span foreground="{FALLBACK_COLOR}">{FALLBACK_ICON}  N/A</span>'
        return self._format_display(info)

    def get_info(self) -> str:
        """Return detailed battery info string."""
        info = self._get_battery_info(force_refresh=True)
        if not info:
            return "Battery: Not available"
        return (
            f"Battery: {info['percentage']}% | "
            f"State: {info['state']} | "
            f"Charging: {info['is_charging']} | "
            f"Critical: {info['is_critical']}"
        )
