from pathlib import Path
from typing import Optional, Tuple

from qtile_extras.widget import GenPollText

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


def fmt(icon: str, val: int, color: str) -> str:
    return f'<span foreground="{color}">{icon}  {val:>3}%</span>'


class BatteryWidget(GenPollText):
    def __init__(self, update_interval=10, **config):
        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def poll(self) -> str:
        info = get_battery_info()
        if not info:
            return '<span foreground="grey">󰁾  --%</span>'
        percent, charging = info
        for level, icon, color in ICONS:
            if percent >= level:
                display_icon = f"󱐋 {icon}" if charging else icon
                return fmt(display_icon, percent, color)
        return '<span foreground="grey">󰁾  --%</span>'
