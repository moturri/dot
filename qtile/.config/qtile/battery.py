from pathlib import Path

from utils import cached, fmt, get_file_int

# Paths to battery and AC adapter
_BAT_CAPACITY_PATH = Path("/sys/class/power_supply/BAT0/capacity")
_AC_ONLINE_PATHS = tuple(
    p / "online" for p in Path("/sys/class/power_supply").glob("AC*")
)

# Battery states: (threshold, icon, (discharging_color, charging_color))
_BATTERY_STATES = [
    (80, "", ("lime", "aqua")),
    (60, "", ("palegreen", "aqua")),
    (40, "", ("orange", "aqua")),
    (20, "", ("coral", "aqua")),
    (0, "", ("red", "aqua")),
]


def is_charging():
    """Check if the device is currently charging (AC connected)."""
    for ac_path in _AC_ONLINE_PATHS:
        if ac_path.exists():
            status = ac_path.read_text().strip()
            if status == "1":
                return True
    return False


@cached(10)
def batt():
    """Return formatted battery level string with icon and color."""
    v = get_file_int(_BAT_CAPACITY_PATH)
    if v is None:
        return '<span foreground="grey">  --%</span>'

    chg = is_charging()

    for level, icon, (dis_col, chg_col) in _BATTERY_STATES:
        if v >= level:
            color = chg_col if chg else dis_col
            final_icon = " " + icon if chg else icon
            return fmt(final_icon, v, color)

    # Fallback (shouldn't really hit this)
    return fmt("", v, "red")
