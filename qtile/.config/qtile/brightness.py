import logging
from pathlib import Path

from utils import cached, fmt, run_command

logger = logging.getLogger(__name__)

# Constants
BRIGHTNESS_DIR = Path("/sys/class/backlight")
BRIGHTNESS_FALLBACK = '<span foreground="grey">󰳲  --%</span>'
BRIGHTNESS_ICONS = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "tan"),
    (20, "󰃞", "lime"),
    (0, "󰃜", "dimgrey"),
]

# Global device info
BACKLIGHT_DEVICE = None
MAX_BRIGHTNESS = 0
BRIGHTNESS_PATH = None
MAX_BRIGHTNESS_PATH = None

# Detect brillo at load time
HAS_BRILLO = run_command(["which", "brillo"], get_output=True) != ""


def find_backlight_device():
    """Detect the appropriate backlight device and read its max value."""
    global BACKLIGHT_DEVICE, MAX_BRIGHTNESS, BRIGHTNESS_PATH, MAX_BRIGHTNESS_PATH
    try:
        if (BRIGHTNESS_DIR / "intel_backlight").exists():
            BACKLIGHT_DEVICE = "intel_backlight"
        else:
            devices = list(BRIGHTNESS_DIR.iterdir())
            if devices:
                BACKLIGHT_DEVICE = devices[0].name

        if BACKLIGHT_DEVICE:
            BRIGHTNESS_PATH = BRIGHTNESS_DIR / BACKLIGHT_DEVICE / "brightness"
            MAX_BRIGHTNESS_PATH = BRIGHTNESS_DIR / BACKLIGHT_DEVICE / "max_brightness"
            if MAX_BRIGHTNESS_PATH.exists():
                MAX_BRIGHTNESS = int(MAX_BRIGHTNESS_PATH.read_text().strip())
    except Exception as e:
        logger.error(f"[brightness] Init error: {e}")


# Initialize at import time
find_backlight_device()


def read_brightness():
    """Read current brightness percentage from sysfs."""
    try:
        current = int(BRIGHTNESS_PATH.read_text().strip())
        return current
    except Exception as e:
        logger.error(f"[brightness] Read error: {e}")
        return 0


@cached(10, cache_none=True)
def bright():
    """
    Brightness widget display.
    Returns a Qtile markup string showing brightness percentage and icon.
    """
    if MAX_BRIGHTNESS <= 0:
        return BRIGHTNESS_FALLBACK

    try:
        current = read_brightness()
        percent = int((current / MAX_BRIGHTNESS) * 100)

        for level, icon, color in BRIGHTNESS_ICONS:
            if percent >= level:
                return fmt(icon, percent, color)

        # Fallback to lowest level
        return fmt(BRIGHTNESS_ICONS[-1][1], percent, BRIGHTNESS_ICONS[-1][2])
    except Exception as e:
        logger.error(f"[brightness] Format error: {e}")
        return BRIGHTNESS_FALLBACK


def adjust_brightness(amount: int, increase: bool = True):
    """
    Adjust brightness using `brillo`.
    Amount is in percent, not absolute values.
    """
    if amount <= 0 or not HAS_BRILLO:
        return

    cmd = ["brillo", "-A" if increase else "-U", str(amount)]
    try:
        run_command(cmd)
    except Exception as e:
        logger.error(f"[brightness] Adjust error: {e}")

    bright(force=True)


# Qtile mouse callbacks or keybind functions
def bright_up(qtile=None, step=5):
    adjust_brightness(step, increase=True)


def bright_down(qtile=None, step=5):
    adjust_brightness(step, increase=False)
