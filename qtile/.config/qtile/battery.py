from typing import Any, Dict, Optional, Tuple

from pydbus import SystemBus
from qtile_extras.widget import GenPollText

# Constants
FALLBACK_ICON = "󰂑"
FALLBACK_COLOR = "grey"

UP_DEVICE_PATH = "/org/freedesktop/UPower/devices/battery_BAT0"
UP_INTERFACE = "org.freedesktop.UPower.Device"


def get_battery_info() -> Optional[Dict[str, Any]]:
    try:
        bus = SystemBus()
        battery = bus.get("org.freedesktop.UPower", UP_DEVICE_PATH)
        percent = int(battery.Percentage)
        state = battery.State  # Enum: 1=Charging, 2=Discharging, 4=Full

        return {
            "percentage": max(0, min(100, percent)),
            "is_charging": state == 1,
            "is_full": state == 4,
        }

    except Exception as e:
        print(f"Battery info error: {e}")
        return None


def format_output(icon: str, percent: int, color: str) -> str:
    return f'<span foreground="{color}">{icon} {percent:3d}%</span>'


class BatteryWidget(GenPollText):
    def __init__(self, update_interval: int = 10, **config):
        self.update_interval = update_interval

        self.icons = [
            (80, "󰂂", "lime"),
            (60, "󰂀", "palegreen"),
            (40, "󰁿", "orange"),
            (20, "󰁻", "coral"),
            (0, "󰁺", "red"),
        ]
        self.charging_icon = "󱐋"
        self.full_icon = "󰂄"

        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def _get_icon_and_color(
        self, percentage: int, is_charging: bool, is_full: bool
    ) -> Tuple[str, str]:
        if is_full:
            return self.full_icon, "lime"

        for threshold, icon, color in self.icons:
            if percentage >= threshold:
                return (f"{self.charging_icon} {icon}" if is_charging else icon), color

        return FALLBACK_ICON, FALLBACK_COLOR

    def poll(self) -> str:
        info = get_battery_info()
        if not info:
            return format_output(FALLBACK_ICON, 0, FALLBACK_COLOR)

        percent = info["percentage"]
        icon, color = self._get_icon_and_color(
            percent, info["is_charging"], info["is_full"]
        )
        return format_output(icon, percent, color)
