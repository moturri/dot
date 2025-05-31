import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from pydbus import SystemBus  # type: ignore
from qtile_extras.widget import GenPollText

# --- Logger setup ---
logger = logging.getLogger(__name__)

# --- Constants ---
CACHE_TIMEOUT: float = 5.0
UPOWER_SERVICE: str = "org.freedesktop.UPower"

FALLBACK_ICON: str = "󰂑"
FALLBACK_COLOR: str = "#666666"
CHARGING_ICON: str = "󱐋"
FULL_ICON: str = "󰂄"

BATTERY_ICONS: List[Tuple[int, str, str]] = [
    (95, "󰂂", "limegreen"),
    (80, "󰂁", "palegreen"),
    (60, "󰂀", "lightgoldenrodyellow"),
    (40, "󰁿", "tan"),
    (20, "󰁻", "lightsalmon"),
    (5, "󰁻", "red"),
    (0, "󰁺", "darkred"),
]

BATTERY_STATES: Dict[int, str] = {
    1: "charging",
    2: "discharging",
    3: "empty",
    4: "fully charged",
    5: "pending charge",
    6: "pending discharge",
}


# --- Helper functions ---
def find_battery_path() -> Optional[str]:
    try:
        bus = SystemBus()
        upower = bus.get(UPOWER_SERVICE, "/org/freedesktop/UPower")
        for dev in upower.EnumerateDevices():
            if isinstance(dev, str) and "battery" in dev.lower():
                return dev
    except Exception as e:
        logger.warning(f"[upower.py] Battery path detection failed: {e}")
    return None


def get_battery_info(path: str) -> Optional[Dict[str, Union[int, str, bool]]]:
    try:
        bus = SystemBus()
        battery = bus.get(UPOWER_SERVICE, path)
        percent = int(max(0, min(100, battery.Percentage)))
        state = int(battery.State)
        return {
            "percentage": percent,
            "state": BATTERY_STATES.get(state, "unknown"),
            "charging": state == 1,
            "discharging": state == 2,
            "full": state == 4,
            "critical": percent <= 5,
        }
    except Exception as e:
        logger.warning(f"[upower.py] Failed to query battery info: {e}")
        return None


# --- Widget class ---
class UpowerWidget(GenPollText):  # type: ignore[misc]
    battery_path: Optional[str]
    icons: List[Tuple[int, str, str]]
    _cache: Optional[Tuple[Dict[str, Union[int, str, bool]], float]]

    def __init__(
        self,
        update_interval: float = 10.0,
        battery_path: Optional[str] = None,
        icons: Optional[List[Tuple[int, str, str]]] = None,
        **config: Any,
    ) -> None:
        self.battery_path = battery_path or find_battery_path()
        self.icons = icons if icons is not None else BATTERY_ICONS
        self._cache = None
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_battery(
        self, force: bool = False
    ) -> Optional[Dict[str, Union[int, str, bool]]]:
        now = time.time()
        if not force and self._cache is not None:
            data, cached_at = self._cache
            if now - cached_at < CACHE_TIMEOUT:
                return data

        if self.battery_path is None:
            return None

        info = get_battery_info(self.battery_path)
        if info is not None:
            self._cache = (info, now)
        return info

    def _icon_color(self, info: Dict[str, Union[int, str, bool]]) -> Tuple[str, str]:
        pct = cast(int, info["percentage"])
        charging = cast(bool, info["charging"])
        full = cast(bool, info["full"])
        critical = cast(bool, info["critical"])

        if full:
            return FULL_ICON, "lime"
        if critical:
            return ("󰂃" if charging else "󰁺"), "dimgrey"

        for threshold, icon, color in self.icons:
            if pct >= threshold:
                return (f"{CHARGING_ICON} {icon}" if charging else icon), color

        return FALLBACK_ICON, FALLBACK_COLOR

    def _poll(self) -> str:
        info = self._get_battery()
        if info is None:
            return f'<span foreground="{FALLBACK_COLOR}">{FALLBACK_ICON}  N/A</span>'
        icon, color = self._icon_color(info)
        pct = cast(int, info["percentage"])
        return f'<span foreground="{color}">{icon} {pct:3d}%</span>'

    def get_info(self) -> str:
        info = self._get_battery(force=True)
        if info is None:
            return "Battery: N/A"
        return (
            f"{info['percentage']}% | "
            f"State: {info['state']} | "
            f"Charging: {info['charging']} | "
            f"Critical: {info['critical']}"
        )

