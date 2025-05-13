from pathlib import Path

from utils import cached, fmt

# Paths
_BAT_CAPACITY_PATH = Path("/sys/class/power_supply/BAT0/capacity")
_AC_ONLINE_PATHS = tuple(
    p / "online" for p in Path("/sys/class/power_supply").glob("AC*")
)

# Threshold icons: (min%, icon, (color on battery, color on AC))
_BATTERY_STATES = [
    (80, "", ("lime", "aqua")),
    (60, "", ("palegreen", "aqua")),
    (40, "", ("orange", "aqua")),
    (20, "", ("coral", "aqua")),
    (0, "", ("red", "aqua")),
]


def is_charging() -> bool:
    """
    Returns True if any AC adapter is online.
    """
    for ac_path in _AC_ONLINE_PATHS:
        try:
            if ac_path.exists() and ac_path.read_text().strip() == "1":
                return True
        except Exception:
            continue
    return False


@cached(10)
def batt() -> str:
    """
    Returns formatted battery widget string with charging status and color.
    """
    try:
        if not _BAT_CAPACITY_PATH.exists():
            raise FileNotFoundError("Battery capacity file not found")

        percent = int(_BAT_CAPACITY_PATH.read_text().strip())
        charging = is_charging()

        for level, icon, (dis_col, chg_col) in _BATTERY_STATES:
            if percent >= level:
                color = chg_col if charging else dis_col
                display_icon = f" {icon}" if charging else icon
                return fmt(display_icon, percent, color)

    except Exception as e:
        print(f"[battery] Error: {e}")
        return '<span foreground="grey">  --%</span>'

    return '<span foreground="grey">  --%</span>'
