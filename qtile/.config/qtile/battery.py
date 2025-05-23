from pathlib import Path
from typing import Optional, Tuple

from utils import cached, fmt

ICONS = [
    (80, "", "lime"),
    (60, "", "palegreen"),
    (40, "", "orange"),
    (20, "", "coral"),
    (0, "", "red"),
]


def get_battery_info() -> Optional[Tuple[int, bool]]:
    for bat_path in Path("/sys/class/power_supply").glob("BAT*"):
        try:
            status = (bat_path / "status").read_text().strip().lower()
            percent = max(0, min(100, int((bat_path / "capacity").read_text().strip())))
            return percent, status in {"charging", "full"}
        except (OSError, ValueError):
            continue
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
