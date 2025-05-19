import logging
import subprocess
from pathlib import Path

from utils import cached, fmt

BRIGHTNESS_DIR = Path("/sys/class/backlight/intel_backlight")
BRIGHTNESS_PATH = BRIGHTNESS_DIR / "brightness"
MAX_BRIGHTNESS_PATH = BRIGHTNESS_DIR / "max_brightness"

BRIGHTNESS_ICONS = [
    (80, "󰃠", "gold"),
    (60, "󰃝", "darkorange"),
    (40, "󰃟", "tan"),
    (20, "󰃞", "lime"),
    (0, "󰃜", "dimgrey"),
]

FALLBACK = '<span foreground="grey">󰳲  --%</span>'

try:
    MAX_BRIGHTNESS = int(MAX_BRIGHTNESS_PATH.read_text().strip())
except Exception as e:
    logging.error(f"[brightness] Failed to read max brightness: {e}")
    MAX_BRIGHTNESS = 0


@cached(10, cache_none=True)
def bright():
    """
    Returns formatted brightness string.
    Caches for 10s to avoid frequent I/O.
    """
    if MAX_BRIGHTNESS <= 0:
        return FALLBACK

    try:
        current = int(BRIGHTNESS_PATH.read_text().strip())
        percent = int((current / MAX_BRIGHTNESS) * 100)

        # Choose the appropriate icon and color based on the brightness percentage
        for level, icon, color in BRIGHTNESS_ICONS:
            if percent >= level:
                return fmt(icon, percent, color)

        return fmt(BRIGHTNESS_ICONS[-1][1], percent, BRIGHTNESS_ICONS[-1][2])
    except Exception as e:
        logging.error(f"[brightness] Error reading brightness: {e}")
        return FALLBACK


def adjust_brightness(amount: int, increase: bool = True):
    if amount <= 0:
        return

    if (
        not subprocess.run(
            ["which", "brillo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        ).returncode
        == 0
    ):
        logging.warning(
            "[brightness] Brillo command not found. Brightness adjustment may not work."
        )
        return

    cmd = ["brillo", "-A" if increase else "-U", str(amount)]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        logging.error(f"[brightness] Failed to adjust brightness: {e}")

    bright(force=True)


def bright_up(qtile=None, step=2):
    adjust_brightness(step, increase=True)


def bright_down(qtile=None, step=2):
    adjust_brightness(step, increase=False)
