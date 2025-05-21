from pathlib import Path

from utils import cached, fmt, run_command

BRIGHTNESS_DIR = Path("/sys/class/backlight")
BRIGHTNESS_FALLBACK = '<span foreground="grey">󰳲  --%</span>'
BRIGHTNESS_ICONS = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "tan"),
    (20, "󰃞", "lime"),
    (0, "󰃜", "dimgrey"),
]

BACKLIGHT_DEVICE = None
MAX_BRIGHTNESS = 0
BRIGHTNESS_PATH = None
MAX_BRIGHTNESS_PATH = None

HAS_BRILLO = run_command(["which", "brillo"], get_output=True) != ""


def find_backlight_device():
    global BACKLIGHT_DEVICE, MAX_BRIGHTNESS, BRIGHTNESS_PATH, MAX_BRIGHTNESS_PATH
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


find_backlight_device()


def read_brightness():
    """Read current brightness percentage from sysfs."""
    if not BRIGHTNESS_PATH or not BRIGHTNESS_PATH.exists():
        return 0
    try:
        current = int(BRIGHTNESS_PATH.read_text().strip())
        return current
    except (OSError, ValueError):
        return 0


@cached(10, cache_none=True)
def bright():
    if MAX_BRIGHTNESS <= 0:
        return BRIGHTNESS_FALLBACK
    current = read_brightness()
    percent = int((current / MAX_BRIGHTNESS) * 100)
    for level, icon, color in BRIGHTNESS_ICONS:
        if percent >= level:
            return fmt(icon, percent, color)
    return fmt(BRIGHTNESS_ICONS[-1][1], percent, BRIGHTNESS_ICONS[-1][2])


def adjust_brightness(amount: int, increase: bool = True):
    if amount <= 0 or not HAS_BRILLO:
        return
    cmd = ["brillo", "-A" if increase else "-U", str(amount)]
    run_command(cmd)
    bright(force=True)


def bright_up(qtile=None, step=5):
    adjust_brightness(step, increase=True)


def bright_down(qtile=None, step=5):
    adjust_brightness(step, increase=False)
