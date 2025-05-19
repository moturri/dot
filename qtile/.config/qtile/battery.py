import logging
import os
import re

from utils import cached, fmt, run_command

# Setup logger
logger = logging.getLogger(__name__)

# Battery icon map: (percent threshold, icon, (discharging_color, charging_color))
BATTERY_STATES = [
    (80, "", ("lime", "lime")),
    (60, "", ("palegreen", "palegreen")),
    (40, "", ("orange", "orange")),
    (20, "", ("coral", "coral")),
    (0, "", ("red", "red")),
]

# Default fallback display string
FALLBACK = '<span foreground="grey">󰁾  --%</span>'

# Regex patterns for upower parsing
PERCENTAGE_PATTERN = re.compile(r"percentage:\s+(\d+)%")
STATE_PATTERN = re.compile(r"state:\s+(\w+)")

# Cached sysfs path discovery
BATTERY_SYSFS_PATH = "/sys/class/power_supply"
BATTERY_SYSFS_DIR = None

try:
    for dev in os.listdir(BATTERY_SYSFS_PATH):
        if "BAT" in dev or "battery" in dev.lower():
            BATTERY_SYSFS_DIR = os.path.join(BATTERY_SYSFS_PATH, dev)
            break
except (FileNotFoundError, PermissionError) as e:
    logger.warning(f"[battery] Unable to read sysfs battery path: {e}")
    BATTERY_SYSFS_DIR = None


# Fallback battery device path for upower
BATTERY_PATH = None


def get_battery_path():
    """Find battery path via upower, cached once."""
    global BATTERY_PATH
    if BATTERY_PATH is None:
        try:
            devices = run_command(["upower", "-e"], get_output=True)
            BATTERY_PATH = next(
                (d for d in devices.splitlines() if "battery" in d), None
            )
        except Exception as e:
            logger.error(f"[battery] Error finding battery path: {e}")
            BATTERY_PATH = None
    return BATTERY_PATH


def get_battery_info_sysfs():
    """Read battery percentage and charging state from sysfs."""
    if not BATTERY_SYSFS_DIR:
        return None
    try:
        with open(os.path.join(BATTERY_SYSFS_DIR, "status"), "r") as f:
            status = f.read().strip()

        with open(os.path.join(BATTERY_SYSFS_DIR, "capacity"), "r") as f:
            percent = int(f.read().strip())

        is_charging = status.lower() in {"charging", "full"}
        return percent, is_charging
    except (FileNotFoundError, PermissionError, ValueError) as e:
        logger.warning(f"[battery] sysfs read error: {e}")
        return None


def get_battery_info_upower():
    """Fetch and parse battery info using upower."""
    battery_path = get_battery_path()
    if not battery_path:
        return None
    try:
        output = run_command(["upower", "-i", battery_path], get_output=True)
        if not output:
            return None
        return parse_upower(output)
    except Exception as e:
        logger.error(f"[battery] upower error: {e}")
        return None


def parse_upower(output: str) -> tuple[int, bool]:
    """Extract battery percentage and charging state from upower output."""
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
    Battery widget function for Qtile GenPollText.
    Returns:
        str: Markup-formatted battery status.
    """
    try:
        battery_info = get_battery_info_sysfs() or get_battery_info_upower()
        if not battery_info:
            return FALLBACK

        percent, charging = battery_info
        charging_icon = ""  # Lightning bolt

        for level, icon, (dis_color, chg_color) in BATTERY_STATES:
            if percent >= level:
                color = chg_color if charging else dis_color
                display_icon = f"{charging_icon} {icon}" if charging else icon
                return fmt(display_icon, percent, color)

        return FALLBACK
    except Exception as e:
        logger.error(f"[battery] Unhandled error: {e}")
        return FALLBACK

