import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from pydbus import SystemBus  # type: ignore[import-untyped]
from qtile_extras.widget import GenPollText

logger = logging.getLogger(__name__)

CACHE_TIMEOUT = 5.0
FALLBACK_ICON = "󰂑"
FALLBACK_COLOR = "#666666"
CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"

UPOWER_SERVICE = "org.freedesktop.UPower"

BATTERY_ICONS: List[Tuple[int, str, str]] = [
    (95, "󰂂", "limegreen"),
    (80, "󰂁", "skyblue"),
    (60, "󰂀", "lightgoldenrodyellow"),
    (40, "󰁿", "lightsalmon"),
    (20, "󰁻", "indianred"),
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


def find_battery_path() -> Optional[str]:
    try:
        bus = SystemBus()
        upower = bus.get(UPOWER_SERVICE, "/org/freedesktop/UPower")
        devices = upower.EnumerateDevices()
        for dev in devices:
            if isinstance(dev, str) and "battery" in dev.lower():
                return dev
    except Exception as e:
        logger.warning(f"[upower] Battery path detection failed: {e}")
    return None


def get_battery_info(path: str) -> Optional[Dict[str, Union[int, str, bool]]]:
    try:
        bus = SystemBus()
        battery = bus.get(UPOWER_SERVICE, path)
        percent = max(0, min(100, int(battery.Percentage)))
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
        logger.warning(f"[upower] Failed to query battery info: {e}")
        return None


class UpowerWidget(GenPollText):  # type: ignore[misc]
    def __init__(
        self,
        update_interval: float = 10.0,
        battery_path: Optional[str] = None,
        icons: Optional[List[Tuple[int, str, str]]] = None,
        **config: Any,
    ) -> None:
        self.battery_path: Optional[str] = battery_path or find_battery_path()
        self.icons: List[Tuple[int, str, str]] = icons or BATTERY_ICONS
        self._cache: Optional[Tuple[Dict[str, Union[int, str, bool]], float]] = None
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_battery(
        self, force: bool = False
    ) -> Optional[Dict[str, Union[int, str, bool]]]:
        now = time.time()
        if not force and self._cache:
            data, cached_at = self._cache
            if now - cached_at < CACHE_TIMEOUT:
                return data
        if not self.battery_path:
            return None
        result = get_battery_info(self.battery_path)
        if result is not None:
            self._cache = (result, now)
            return result
        return None

    def _icon_color(self, info: Dict[str, Union[int, str, bool]]) -> Tuple[str, str]:
        pct = int(info["percentage"])
        charging = bool(info["charging"])
        full = bool(info["full"])
        critical = bool(info["critical"])

        if full:
            return FULL_ICON, "#50fa7b"
        if critical:
            return ("󰂃" if charging else "󰁺"), "#ff0000"
        for threshold, icon, color in self.icons:
            if pct >= threshold:
                return (f"{CHARGING_ICON} {icon}" if charging else icon), color
        return FALLBACK_ICON, FALLBACK_COLOR

    def _poll(self) -> str:
        info = self._get_battery()
        if not info:
            return f'<span foreground="{FALLBACK_COLOR}">{FALLBACK_ICON}  N/A</span>'
        icon, color = self._icon_color(info)
        pct = int(info["percentage"])
        return f'<span foreground="{color}">{icon} {pct:3d}%</span>'

    def get_info(self) -> str:
        info = self._get_battery(force=True)
        if not info:
            return "Battery: N/A"
        return (
            f"{info['percentage']}% | "
            f"State: {info['state']} | "
            f"Charging: {info['charging']} | "
            f"Critical: {info['critical']}"
        )

