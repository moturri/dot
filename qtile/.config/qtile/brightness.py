import subprocess
from pathlib import Path

from utils import cached, fmt, get_file_int

_BRIGHTNESS_PATH = Path("/sys/class/backlight/intel_backlight/brightness")
_MAX_BRIGHTNESS_PATH = Path("/sys/class/backlight/intel_backlight/max_brightness")

_BRIGHTNESS_ICONS = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "darkorchid"),
    (20, "󰃞", "lightgreen"),
    (0, "󰃜", "dimgrey"),
]


@cached(0.5)
def bright():
    current = get_file_int(_BRIGHTNESS_PATH)
    maximum = get_file_int(_MAX_BRIGHTNESS_PATH)

    if current is None or maximum is None:
        return '<span foreground="grey">󰳲  --%</span>'

    v = int((current / maximum) * 100)

    for level, icon, color in _BRIGHTNESS_ICONS:
        if v >= level:
            return fmt(icon, v, color)

    return fmt("󰳲", v, "grey")


def bright_up(qtile=None):
    subprocess.run(["brillo", "-A", "2"])
    bright(force=True)


def bright_down(qtile=None):
    subprocess.run(["brillo", "-U", "2"])
    bright(force=True)
