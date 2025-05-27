from pathlib import Path
from typing import Callable, Optional, Tuple

from qtile_extras.widget import GenPollText

ICONS = [
    (80, "", "lime"),
    (60, "", "palegreen"),
    (40, "", "orange"),
    (20, "", "coral"),
    (0, "", "red"),
]


def get_battery_info() -> Optional[Tuple[int, bool]]:
    """Returns (percentage, is_charging) or None if battery not found or unreadable."""
    for bat in Path("/sys/class/power_supply").glob("BAT*"):
        try:
            capacity = int((bat / "capacity").read_text().strip())
            status = (bat / "status").read_text().strip().lower()
            percent = max(0, min(100, capacity))
            charging = status in {"charging", "full"}
            return percent, charging
        except (OSError, ValueError):
            continue
    return None


def format_output(icon: str, percent: int, color: str) -> str:
    return f'<span foreground="{color}">{icon}  {percent:>3}%</span>'


class BatteryWidget(GenPollText):
    def __init__(
        self,
        update_interval: int = 10,
        charging_prefix: str = "󱐋",
        alert_threshold: int = 10,
        on_low_battery: Optional[Callable[[int], None]] = None,
        **config,
    ):
        """
        :param update_interval: Seconds between checks
        :param charging_prefix: Icon prefix when charging
        :param alert_threshold: Trigger `on_low_battery` callback if below
        :param on_low_battery: Callable to run on low battery (e.g., notification)
        """
        self.charging_prefix = charging_prefix
        self.alert_threshold = alert_threshold
        self.on_low_battery = on_low_battery
        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def poll(self) -> str:
        info = get_battery_info()
        if info is None:
            return '<span foreground="grey">󰁾  --%</span>'

        percent, charging = info

        # Optional low battery alert callback
        if percent < self.alert_threshold and not charging and self.on_low_battery:
            self.on_low_battery(percent)

        # Choose icon and color
        icon, color = next((i, c) for lvl, i, c in ICONS if percent >= lvl)

        # Prefix charging icon if charging
        if charging and self.charging_prefix:
            icon = f"{self.charging_prefix} {icon}"

        return format_output(icon, percent, color)
