import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from qtile_extras.widget import GenPollText


def get_battery_info() -> Optional[Dict[str, Any]]:
    """Basic battery info from /sys/class/power_supply."""
    power_supply_path = Path("/sys/class/power_supply")
    batteries = list(power_supply_path.glob("BAT*"))

    for bat in batteries:
        try:
            capacity = int((bat / "capacity").read_text().strip())
            status = (bat / "status").read_text().strip().lower()
            return {
                "percentage": max(0, min(100, capacity)),
                "is_charging": status == "charging",
                "is_full": status == "full",
            }
        except (OSError, ValueError):
            continue

    return None


def format_output(icon: str, percent: int, color: str) -> str:
    return f'<span foreground="{color}">{icon} {percent:3d}%</span>'


class BatteryWidget(GenPollText):
    """Simplified battery widget."""

    def __init__(self, update_interval: int = 30, **config):
        self.update_interval = update_interval

        # Basic icon and color thresholds
        self.icons = [
            (80, "󰂂", "lime"),
            (60, "󰂀", "green"),
            (40, "󰁿", "orange"),
            (20, "󰁻", "coral"),
            (0,  "󰁺", "red"),
        ]
        self.charging_icon = "󱐋"
        self.full_icon = "󰂄"

        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def _get_icon_and_color(self, percentage: int, is_charging: bool, is_full: bool) -> Tuple[str, str]:
        if is_full:
            return self.full_icon, "lime"

        for threshold, icon, color in self.icons:
            if percentage >= threshold:
                icon = f"{self.charging_icon} {icon}" if is_charging else icon
                return icon, color

        return "󰁺", "grey"  # fallback

    def poll(self) -> str:
        info = get_battery_info()
        if not info:
            return '<span foreground="grey">󰂑  N/A</span>'

        percent = info["percentage"]
        icon, color = self._get_icon_and_color(
            percent, info["is_charging"], info["is_full"]
        )
        return format_output(icon, percent, color)
