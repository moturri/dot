import subprocess
import re
from utils import cached, fmt

# Battery level thresholds: (min %, icon, (discharging color, charging color))
_BATTERY_STATES = [
    (80, "", ("lime", "lime")),
    (60, "", ("palegreen", "palegreen")),
    (40, "", ("orange", "orange")),
    (20, "", ("coral", "coral")),
    (0, "", ("red", "red")),
]

# Fallback display if battery info can't be retrieved
_FALLBACK = '<span foreground="grey">  --%</span>'


def get_upower_output() -> str:
    """
    Retrieves UPower output for the first battery device found.
    """
    try:
        devices_output = subprocess.check_output(["upower", "-e"], text=True)
        battery_path = next(
            (line for line in devices_output.splitlines() if "battery" in line), None
        )
        if not battery_path:
            raise RuntimeError("No battery device found")

        return subprocess.check_output(["upower", "-i", battery_path], text=True)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"UPower call failed: {e}")


def parse_upower(output: str) -> tuple[int, bool]:
    """
    Extracts battery percentage and charging state from upower output.
    Returns (percentage, is_charging).
    """
    percent_match = re.search(r"percentage:\s+(\d+)%", output)
    state_match = re.search(r"state:\s+(\w+)", output)

    if not percent_match or not state_match:
        raise ValueError("Could not parse battery status from upower output")

    percent = int(percent_match.group(1))
    charging = state_match.group(1).lower() == "charging"
    return percent, charging


@cached(10)
def batt() -> str:
    """
    Returns a formatted battery widget string with dynamic icon and color.
    """
    try:
        output = get_upower_output()
        percent, charging = parse_upower(output)

        for level, icon, (dis_col, chg_col) in _BATTERY_STATES:
            if percent >= level:
                color = chg_col if charging else dis_col
                icon_display = f" {icon}" if charging else icon
                return fmt(icon_display, percent, color)

    except Exception as e:
        print(f"[battery] Error: {e}")
        return _FALLBACK

    return _FALLBACK
