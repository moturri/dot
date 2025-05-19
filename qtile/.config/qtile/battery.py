import re
import subprocess

from utils import cached, fmt

PERCENTAGE_PATTERN = re.compile(r"percentage:\s+(\d+)%")
STATE_PATTERN = re.compile(r"state:\s+(\w+)")

BATTERY_STATES = [
    (80, "", ("lime", "lime")),
    (60, "", ("palegreen", "palegreen")),
    (40, "", ("orange", "orange")),
    (20, "", ("coral", "coral")),
    (0, "", ("red", "red")),
]

FALLBACK = '<span foreground="grey">󰁾  --%</span>'


def get_battery_info() -> str:
    """
    Runs `upower` and returns the full info for the first battery device found.
    """
    try:
        devices = subprocess.check_output(["upower", "-e"], text=True)
        battery_path = next((d for d in devices.splitlines() if "battery" in d), None)
        if not battery_path:
            raise FileNotFoundError("No battery device found via upower")
        return subprocess.check_output(["upower", "-i", battery_path], text=True)
    except Exception as e:
        print(f"[battery] upower error: {e}")
        return ""  # Returning empty string instead of raising an error


def parse_upower(output: str) -> tuple[int, bool]:
    """
    Parses battery percentage and charging status from upower output.
    Returns: (percentage, is_charging)
    """
    percent_match = PERCENTAGE_PATTERN.search(output)
    state_match = STATE_PATTERN.search(output)

    if not percent_match or not state_match:
        raise ValueError("Battery info could not be parsed")

    percent = int(percent_match.group(1))
    state = state_match.group(1).lower()
    is_charging = state in {"charging", "pending-charge"}

    return percent, is_charging


@cached(10, cache_none=True)
def batt() -> str:
    """
    Returns formatted battery widget string with icon, percentage, and color.
    Caches for 10 seconds to minimize subprocess overhead.
    """
    try:
        info = get_battery_info()
        if not info:
            return FALLBACK

        percent, charging = parse_upower(info)

        # Find the appropriate battery icon and color
        for level, icon, (dis_col, chg_col) in BATTERY_STATES:
            if percent >= level:
                color = chg_col if charging else dis_col
                icon_disp = f"\xa0{icon}" if charging else icon
                return fmt(icon_disp, percent, color)

        return FALLBACK
    except Exception as e:
        print(f"[battery] Error: {e}")
        return FALLBACK
