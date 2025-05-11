from pathlib import Path
from utils import cached, fmt

_BRIGHTNESS_PATH = Path("/sys/class/backlight/intel_backlight/brightness")
_MAX_BRIGHTNESS_PATH = Path("/sys/class/backlight/intel_backlight/max_brightness")
_BAT_CAPACITY_PATH = Path("/sys/class/power_supply/BAT0/capacity")
_AC_ONLINE_PATHS = tuple(
    p / "online" for p in Path("/sys/class/power_supply").glob("AC*")
)

_BRIGHTNESS_ICONS = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "darkorchid"),
    (20, "󰃞", "lightgreen"),
    (0, "󰃜", "dimgrey"),
]

_BATTERY_STATES = [
    (80, "", ("lime", "aqua")),
    (60, "", ("palegreen", "aqua")),
    (40, "", ("orange", "aqua")),
    (20, "", ("coral", "aqua")),
    (0, "", ("red", "aqua")),
]


@cached(0.5)
def bright():
    try:
        current = int(_BRIGHTNESS_PATH.read_text())
        maximum = int(_MAX_BRIGHTNESS_PATH.read_text())
        v = int((current / maximum) * 100)
    except (FileNotFoundError, ValueError, OSError):
        return '<span foreground="grey">󰳲  --%</span>'

    for level, icon, color in _BRIGHTNESS_ICONS:
        if v >= level:
            return fmt(icon, v, color)
    return fmt("󰳲", v, "grey")


def is_charging():
    for ac_path in _AC_ONLINE_PATHS:
        try:
            if ac_path.exists() and ac_path.read_text().strip() == "1":
                return True
        except (OSError, FileNotFoundError):
            continue
    return False


@cached(10)
def batt():
    try:
        if not _BAT_CAPACITY_PATH.exists():
            return '<span foreground="grey">  --%</span>'
        v = int(_BAT_CAPACITY_PATH.read_text().strip())
    except (OSError, ValueError):
        return '<span foreground="grey">  --%</span>'

    chg = is_charging()

    for level, icon, (dis_col, chg_col) in _BATTERY_STATES:
        if v >= level:
            color = chg_col if chg else dis_col
            final_icon = " " + icon if chg else icon
            return fmt(final_icon, v, color)

    return fmt("", v, "red")
