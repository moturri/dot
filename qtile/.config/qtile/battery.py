from pathlib import Path
from typing import Optional, Tuple

from utils import cached, fmt

BATTERY_PATH = next((p for p in Path("/sys/class/power_supply").glob("BAT*")), None)

ICONS = [
    (80, "", "lime"),
    (60, "", "palegreen"),
    (40, "", "orange"),
    (20, "", "coral"),
    (0, "", "red"),
]


def get_battery_info() -> Optional[Tuple[int, bool]]:
    if not BATTERY_PATH:
        return None
    try:
        status = (BATTERY_PATH / "status").read_text().strip().lower()
        percent = max(0, min(100, int((BATTERY_PATH / "capacity").read_text().strip())))
        return percent, status in {"charging", "full"}
    except (OSError, ValueError):
        return None


@cached(10)
def batt() -> str:
    info = get_battery_info()
    if not info:
        return '<span foreground="grey">󰁾  --%</span>'
    percent, charging = info
    for level, icon, color in ICONS:
        if percent >= level:
            display_icon = f"󱐋 {icon}" if charging else icon
            return fmt(display_icon, percent, color)
    return '<span foreground="grey">󰁾  --%</span>'

