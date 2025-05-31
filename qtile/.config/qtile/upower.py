import logging
import time
from typing import Any, Dict, List, Optional, Tuple, TypedDict

from pydbus import SystemBus  # type: ignore
from qtile_extras.widget import GenPollText

# --- Logger setup ---
logger = logging.getLogger("qtile.upower")
logger.setLevel(logging.INFO)

# --- Constants ---
CACHE_TIMEOUT = 5.0
UPOWER_SERVICE = "org.freedesktop.UPower"

FALLBACK_ICON = "󰂑"
FALLBACK_COLOR = "#666666"
CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"
CRITICAL_ICON = "󰂃"
EMPTY_ICON = "󰁺"

BATTERY_ICONS: List[Tuple[int, str, str]] = [
    (95, "󰂂", "limegreen"),
    (80, "󰂁", "palegreen"),
    (60, "󰂀", "lightgoldenrodyellow"),
    (40, "󰁿", "tan"),
    (20, "󰁻", "lightsalmon"),
    (5, "󰁻", "red"),
    (0, EMPTY_ICON, "darkred"),
]

BATTERY_STATES: Dict[int, str] = {
    1: "charging",
    2: "discharging",
    3: "empty",
    4: "fully charged",
    5: "pending charge",
    6: "pending discharge",
}


# --- Battery Info Type ---
class BatteryInfo(TypedDict):
    percentage: int
    state: str
    charging: bool
    discharging: bool
    full: bool
    critical: bool


# --- Helper Functions ---
def find_battery_path() -> Optional[str]:
    """Detect the UPower device path for the battery."""
    try:
        bus = SystemBus()
        upower = bus.get(UPOWER_SERVICE, "/org/freedesktop/UPower")
        for dev in upower.EnumerateDevices():
            if isinstance(dev, str) and "battery" in dev.lower():
                logger.info(f"Detected battery device: {dev}")
                return dev
    except Exception as e:
        logger.warning(f"Battery path detection failed: {e}")
    return None


def get_battery_info(path: str) -> Optional[BatteryInfo]:
    """Query the battery device for status information."""
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


# --- Widget Class ---
class UpowerWidget(GenPollText):  # type: ignore[misc]
    """
    A Qtile widget that displays battery status using UPower via DBus.
    """

    def __init__(
        self,
        update_interval: float = 10.0,
        battery_path: Optional[str] = None,
        icons: Optional[List[Tuple[int, str, str]]] = None,
        **config: Any,
    ) -> None:
        self.battery_path = battery_path or find_battery_path()
        if self.battery_path is None:
            logger.warning("No battery device found; widget will show fallback.")
        self.icons = icons if icons is not None else BATTERY_ICONS
        self._cache: Optional[Tuple[BatteryInfo, float]] = None
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_battery(self, force: bool = False) -> Optional[BatteryInfo]:
        """Retrieve battery info, optionally bypassing the cache."""
        now = time.time()
        if not force and self._cache is not None:
            data, cached_at = self._cache
            if now - cached_at < CACHE_TIMEOUT:
                return data

        if self.battery_path is None:
            return None

        info = get_battery_info(self.battery_path)
        if info:
            self._cache = (info, now)
        return info

    def _icon_color(self, info: BatteryInfo) -> Tuple[str, str]:
        """Determine the appropriate icon and color based on battery status."""
        pct = info["percentage"]
        charging = info["charging"]
        full = info["full"]
        critical = info["critical"]

        if full:
            return FULL_ICON, "lime"
        if critical:
            return (CRITICAL_ICON if charging else EMPTY_ICON), "dimgrey"

        for threshold, icon, color in self.icons:
            if pct >= threshold:
                return (f"{CHARGING_ICON} {icon}" if charging else icon), color

        return FALLBACK_ICON, FALLBACK_COLOR

    def _poll(self) -> str:
        """Render the widget display text."""
        info = self._get_battery()
        if info is None:
            return f'<span foreground="{FALLBACK_COLOR}">{FALLBACK_ICON}  N/A</span>'
        icon, color = self._icon_color(info)
        pct = info["percentage"]
        return f'<span foreground="{color}">{icon} {pct:3d}%</span>'

    def get_info(self) -> str:
        """Get a detailed string of battery information."""
        info = self._get_battery(force=True)
        if info is None:
            return "Battery: N/A"
        return (
            f"{info['percentage']}% | "
            f"State: {info['state']} | "
            f"Charging: {info['charging']} | "
            f"Critical: {info['critical']}"
        )

