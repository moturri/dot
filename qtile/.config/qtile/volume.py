import re
import subprocess

from utils import cached, fmt

# Volume icons and colors based on level
_VOLUME_STATES = [
    (70, "󰕾", "salmon"),
    (40, "󰖀", "orchid"),
    (15, "󰕿", "springgreen"),
    (0, "󰕿", "palegreen"),
]

# Muted icon and color
_MUTED_ICON = "󰝟"
_MUTED_COLOR = "dimgrey"


def get_current_volume() -> int:
    """
    Gets current volume level (0-100). Returns 0 if unable to retrieve.
    """
    try:
        output = subprocess.check_output(
            ["pactl", "get-sink-volume", "@DEFAULT_SINK@"], stderr=subprocess.DEVNULL
        ).decode()
        match = re.search(r"(\d+)%", output)
        return int(match.group(1)) if match else 0
    except Exception as e:
        print(f"[volume] get_current_volume error: {e}")
        return 0


@cached(600)
def vol() -> str:
    """
    Returns formatted volume widget string.
    """
    try:
        volume_output = subprocess.check_output(
            ["pactl", "get-sink-volume", "@DEFAULT_SINK@"], stderr=subprocess.DEVNULL
        ).decode()
        mute_output = subprocess.check_output(
            ["pactl", "get-sink-mute", "@DEFAULT_SINK@"], stderr=subprocess.DEVNULL
        ).decode()

        match = re.search(r"(\d+)%", volume_output)
        volume = int(match.group(1)) if match else 0
        muted = "yes" in mute_output.lower()

        if muted:
            return fmt(_MUTED_ICON, volume, _MUTED_COLOR)

        for level, icon, color in _VOLUME_STATES:
            if volume >= level:
                return fmt(icon, volume, color)

    except Exception as e:
        print(f"[volume] Error: {e}")
        return fmt(_MUTED_ICON, 0, _MUTED_COLOR)

    return fmt(_MUTED_ICON, 0, _MUTED_COLOR)


def vol_up(qtile=None):
    current = get_current_volume()
    if current < 100:
        increment = min(2, 100 - current)
        subprocess.run(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{increment}%"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    vol(force=True)


def vol_down(qtile=None):
    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-2%"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    vol(force=True)


def vol_mute(qtile=None):
    subprocess.run(
        ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    vol(force=True)
