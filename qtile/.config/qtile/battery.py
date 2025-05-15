import subprocess
import re

from utils import cached, fmt

# Threshold icons: (min%, icon, (color on battery, color on AC))
_BATTERY_STATES = [
    (80, "", ("lime", "lime")),
    (60, "", ("palegreen", "palegreen")),
    (40, "", ("orange", "orange")),
    (20, "", ("coral", "coral")),
    (0, "", ("red", "red")),
]


def get_upower_output() -> str:
    """
    Gets the output from upower battery device.
    """
    try:
        # Find the battery device (e.g., /org/freedesktop/UPower/devices/battery_BAT0)
        devices_output = subprocess.check_output(["upower", "-e"], text=True)
        battery_path = next(
            (line for line in devices_output.splitlines() if "battery" in line), None
        )
        if not battery_path:
            raise RuntimeError("No battery device found in upower")

        # Get battery info
        battery_output = subprocess.check_output(
            ["upower", "-i", battery_path], text=True
        )
        return battery_output

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get upower info: {e}")


def parse_upower(output: str) -> tuple[int, bool]:
    """
    Parses upower output to extract battery percentage and charging status.
    Returns:
        (percent: int, charging: bool)
    """
    percent_match = re.search(r"percentage:\s+(\d+)%", output)
    state_match = re.search(r"state:\s+(\w+)", output)

    if not percent_match or not state_match:
        raise ValueError("Could not parse battery info from upower output")

    percent = int(percent_match.group(1))
    charging = state_match.group(1).lower() == "charging"

    return percent, charging


@cached(10)
def batt() -> str:
    """
    Returns formatted battery widget string with charging status and color.
    """
    try:
        upower_output = get_upower_output()
        percent, charging = parse_upower(upower_output)

        for level, icon, (dis_col, chg_col) in _BATTERY_STATES:
            if percent >= level:
                color = chg_col if charging else dis_col
                display_icon = f" {icon}" if charging else icon
                return fmt(display_icon, percent, color)

    except Exception as e:
        print(f"[battery] Error: {e}")
        return '<span foreground="grey">  --%</span>'

    return '<span foreground="grey">  --%</span>'

