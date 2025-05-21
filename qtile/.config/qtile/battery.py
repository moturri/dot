import os
import re
from pathlib import Path

from utils import cached, fmt, run_command

BATTERY_STATES = [
    (80, "", ("lime", "lime")),
    (60, "", ("palegreen", "palegreen")),
    (40, "", ("orange", "orange")),
    (20, "", ("coral", "coral")),
    (0, "", ("red", "red")),
]

FALLBACK = '<span foreground="grey">󰁾  --%</span>'
PERCENTAGE_PATTERN = re.compile(r"percentage:\s+(\d+)%")
STATE_PATTERN = re.compile(r"state:\s+(\w+)")
BATTERY_SYSFS_PATH = Path("/sys/class/power_supply")
BATTERY_SYSFS_DIR = None
BATTERY_PATH = None

# Try to find battery in sysfs
try:
    for dev in os.listdir(BATTERY_SYSFS_PATH):
        if "BAT" in dev or "battery" in dev.lower():
            BATTERY_SYSFS_DIR = BATTERY_SYSFS_PATH / dev
            break
except OSError:
    BATTERY_SYSFS_DIR = None


def get_battery_path():
    global BATTERY_PATH
    if BATTERY_PATH is None:
        devices = run_command(["upower", "-e"], get_output=True)
        if devices:
            BATTERY_PATH = next(
                (d for d in devices.splitlines() if "battery" in d), None
            )
    return BATTERY_PATH


def get_battery_info_sysfs():
    if not BATTERY_SYSFS_DIR:
        return None
    try:
        status = (BATTERY_SYSFS_DIR / "status").read_text().strip()
        percent = int((BATTERY_SYSFS_DIR / "capacity").read_text().strip())
        is_charging = status.lower() in {"charging", "full"}
        return percent, is_charging
    except (FileNotFoundError, ValueError, PermissionError):
        return None


def get_battery_info_upower():
    path = get_battery_path()
    if not path:
        return None
    output = run_command(["upower", "-i", path], get_output=True)
    return parse_upower(output) if output else None


def parse_upower(output: str) -> tuple[int, bool]:
    percent_match = PERCENTAGE_PATTERN.search(output)
    state_match = STATE_PATTERN.search(output)
    if percent_match and state_match:
        percent = int(percent_match.group(1))
        state = state_match.group(1).lower()
        is_charging = state in {"charging", "pending-charge", "fully-charged"}
        return percent, is_charging
    raise ValueError("Invalid battery info")


@cached(30, cache_none=True)
def batt() -> str:
    info = get_battery_info_sysfs() or get_battery_info_upower()
    if not info:
        return FALLBACK
    percent, charging = info
    icon = ""
    for level, sym, (dis_color, chg_color) in BATTERY_STATES:
        if percent >= level:
            color = chg_color if charging else dis_color
            display_icon = f"{icon} {sym}" if charging else sym
            return fmt(display_icon, percent, color)
    return FALLBACK
