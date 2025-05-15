import subprocess
from pathlib import Path

from utils import cached, fmt

# Paths for brightness values
_BRIGHTNESS_PATH = Path("/sys/class/backlight/intel_backlight/brightness")
_MAX_BRIGHTNESS_PATH = Path("/sys/class/backlight/intel_backlight/max_brightness")

# Icon thresholds: (minimum %, icon, color)
_BRIGHTNESS_ICONS = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "tan"),
    (20, "󰃞", "lime"),
    (0, "󰃜", "dimgrey"),
]


@cached(0.5)
def bright():
    try:
        current = int(_BRIGHTNESS_PATH.read_text().strip())
        maximum = int(_MAX_BRIGHTNESS_PATH.read_text().strip())

        if maximum == 0:
            raise ValueError("Maximum brightness is zero")

        percent = int((current / maximum) * 100)

        for level, icon, color in _BRIGHTNESS_ICONS:
            if percent >= level:
                return fmt(icon, percent, color)

    except Exception as e:
        print(f"[brightness] Error: {e}")
        return '<span foreground="grey">󰳲  --%</span>'

    return '<span foreground="grey">󰳲  --%</span>'


def bright_up(qtile=None):
    subprocess.run(
        ["brillo", "-A", "2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    bright(force=True)


def bright_down(qtile=None):
    subprocess.run(
        ["brillo", "-U", "2"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    bright(force=True)

