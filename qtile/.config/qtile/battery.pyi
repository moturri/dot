from typing import Any, Dict, List, Optional, Tuple

BATTERY_ICONS: List[Tuple[int, str, str]]
CACHE_TIMEOUT: float
FALLBACK_ICON: str
FALLBACK_COLOR: str
UPOWER_SERVICE: str
DEVICE_INTERFACE: str
CHARGING_ICON: str
FULL_ICON: str
BATTERY_STATE: Dict[int, str]

def find_battery_path() -> Optional[str]: ...
def get_battery_info(battery_path: str) -> Optional[Dict[str, Any]]: ...

class BatteryWidget:
    def __init__(
        self,
        update_interval: float = ...,
        battery_path: Optional[str] = ...,
        icons: Optional[List[Tuple[int, str, str]]] = ...,
        **config: Any,
    ) -> None: ...
    def _get_battery_info(
        self, force_refresh: bool = ...
    ) -> Optional[Dict[str, Any]]: ...
    def _get_icon_and_color(self, info: Dict[str, Any]) -> Tuple[str, str]: ...
    def _format_display(self, info: Dict[str, Any]) -> str: ...
    def _poll(self) -> str: ...
    def get_info(self) -> str: ...
