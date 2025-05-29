from typing import Any, List, Optional, Tuple
from pathlib import Path

BRIGHTNESS_STEP: int
CACHE_TIMEOUT: float
CMD_TIMEOUT: float

BRIGHTNESS_ICONS: List[Tuple[int, str, str]]
DEVICE_PRIORITY: List[str]

def run_cmd(cmd: List[str]) -> str: ...
def find_backlight_device(device_name: Optional[str] = None) -> Optional["Path"]: ...

class BrilloWidget:
    def __init__(
        self,
        update_interval: float = ...,
        step: int = ...,
        device_name: Optional[str] = ...,
        icons: Optional[List[Tuple[int, str, str]]] = ...,
        prefer_brillo: bool = ...,
        **config: Any,
    ) -> None: ...
    
    def increase(self) -> None: ...
    def decrease(self) -> None: ...
    def set_percent(self, percent: int) -> None: ...
    def get_info(self) -> str: ...

