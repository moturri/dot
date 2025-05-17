import re
import subprocess
from utils import cached, fmt

# Regex pattern for parsing 'wpctl get-volume' output
VOLUME_PATTERN = re.compile(r"Volume:\s+(\d+(?:\.\d+)?)")

# Volume display thresholds
VOLUME_STATES = [
    (70, "󰕾", "salmon"),  # High volume
    (40, "󰖀", "mediumpurple"),  # Medium volume
    (15, "󰕿", "springgreen"),  # Low volume
    (0, "󰕿", "palegreen"),  # Very low
]

# Muted icon & color
MUTED_ICON = "󰝟"
MUTED_COLOR = "dimgrey"

# PipeWire default audio sink
DEFAULT_SINK = "@DEFAULT_AUDIO_SINK@"


def get_volume_state() -> tuple[int, bool]:
    """
    Returns the current volume (0–100) and mute status using wpctl.
    Falls back to (0, True) on error.
    """
    try:
        output = (
            subprocess.check_output(
                ["wpctl", "get-volume", DEFAULT_SINK], stderr=subprocess.DEVNULL
            )
            .decode()
            .strip()
        )

        match = VOLUME_PATTERN.search(output)
        if not match:
            return 0, True

        volume_float = float(match.group(1))
        volume = int(volume_float * 100)
        muted = "[MUTED]" in output

        return volume, muted
    except Exception as e:
        print(f"[volume] get_volume_state error: {e}")
        return 0, True


@cached(0.5)
def vol() -> str:
    """
    Returns formatted string for volume widget (icon + value + color).
    """
    try:
        volume, muted = get_volume_state()

        if muted:
            return fmt(MUTED_ICON, volume, MUTED_COLOR)

        for level, icon, color in sorted(VOLUME_STATES, reverse=True):
            if volume >= level:
                return fmt(icon, volume, color)

        return fmt(VOLUME_STATES[-1][1], volume, VOLUME_STATES[-1][2])
    except Exception as e:
        print(f"[volume] Error: {e}")
        return fmt(MUTED_ICON, 0, MUTED_COLOR)


def vol_up(qtile=None, step=2):
    """
    Increases system volume by `step` percent, capped at 100%.
    """
    if step <= 0:
        return

    try:
        volume, _ = get_volume_state()
        new_volume = min(100, volume + step)
        subprocess.run(
            ["wpctl", "set-volume", DEFAULT_SINK, f"{new_volume / 100:.2f}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[vol_up] Error: {e}")

    vol(force=True)


def vol_down(qtile=None, step=2):
    """
    Decreases system volume by `step` percent, not below 0%.
    """
    if step <= 0:
        return

    try:
        volume, _ = get_volume_state()
        new_volume = max(0, volume - step)
        subprocess.run(
            ["wpctl", "set-volume", DEFAULT_SINK, f"{new_volume / 100:.2f}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[vol_down] Error: {e}")

    vol(force=True)


def vol_mute(qtile=None):
    """
    Toggles mute on the default sink using wpctl.
    """
    try:
        subprocess.run(
            ["wpctl", "set-mute", DEFAULT_SINK, "toggle"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[vol_mute] Error: {e}")

    vol(force=True)


def vol_set(level: int):
    """
    Sets system volume to an exact level (0–100).
    """
    level = max(0, min(level, 100))

    try:
        subprocess.run(
            ["wpctl", "set-volume", DEFAULT_SINK, f"{level / 100:.2f}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[vol_set] Error: {e}")

    vol(force=True)

