import subprocess
from pathlib import Path
from utils import cached, fmt

# Brightness system paths
_BRIGHTNESS_PATH = Path("/sys/class/backlight/intel_backlight/brightness")
_MAX_BRIGHTNESS_PATH = Path("/sys/class/backlight/intel_backlight/max_brightness")

# Brightness levels: (min %, icon, color)
_BRIGHTNESS_ICONS = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "tan"),
    (20, "󰃞", "lime"),
    (0, "󰃜", "dimgrey"),
]

# Fallback text for when brightness can't be read
_FALLBACK = '<span foreground="grey">󰳲  --%</span>'


@cached(0.5)
def bright():
    """
    Returns formatted brightness string from system brightness files.
    Falls back gracefully if data is unreadable.

    Uses a 0.5-second cache to reduce file I/O operations while
    maintaining responsive updates.
    """
    try:
        current = int(_BRIGHTNESS_PATH.read_text().strip())
        maximum = int(_MAX_BRIGHTNESS_PATH.read_text().strip())

        if maximum <= 0:
            raise ValueError("Invalid max brightness value")

        percent = int((current / maximum) * 100)

        for level, icon, color in _BRIGHTNESS_ICONS:
            if percent >= level:
                return fmt(icon, percent, color)

        # Fallback to lowest icon if none matched
        return fmt(_BRIGHTNESS_ICONS[-1][1], percent, _BRIGHTNESS_ICONS[-1][2])
    except Exception as e:
        print(f"[brightness] Error: {e}")
        return _FALLBACK


def bright_up(qtile=None, step=2):
    """
    Increases brightness using brillo.

    Args:
        qtile: Qtile instance (can be None)
        step: Percentage to increase (default: 2)
    """
    if step <= 0:
        return

    subprocess.run(
        ["brillo", "-A", str(step)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    bright(force=True)  # Force refresh of the cached value


def bright_down(qtile=None, step=2):
    """
    Decreases brightness using brillo.

    Args:
        qtile: Qtile instance (can be None)
        step: Percentage to decrease (default: 2)
    """
    if step <= 0:
        return

    subprocess.run(
        ["brillo", "-U", str(step)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    bright(force=True)  # Force refresh of the cached value
