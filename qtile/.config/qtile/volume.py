import re
import subprocess
from utils import cached, fmt

# Volume icons and color thresholds
_VOLUME_STATES = [
    (70, "󰕾", "salmon"),
    (40, "󰖀", "mediumpurple"),
    (15, "󰕿", "springgreen"),
    (0, "󰕿", "palegreen"),
]

# Muted icon/color
_MUTED_ICON = "󰝟"
_MUTED_COLOR = "dimgrey"


def get_volume_state() -> tuple[int, bool]:
    """
    Returns the current volume and mute state of the default sink.
    Falls back to (0, True) on error.
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
        return volume, muted

    except Exception as e:
        print(f"[volume] get_volume_state error: {e}")
        return 0, True


@cached(0.5)
def vol() -> str:
    """
    Returns formatted volume widget string.
    """
    try:
        volume, muted = get_volume_state()

        if muted:
            return fmt(_MUTED_ICON, volume, _MUTED_COLOR)

        for level, icon, color in _VOLUME_STATES:
            if volume >= level:
                return fmt(icon, volume, color)
        return fmt(_VOLUME_STATES[-1][1], volume, _VOLUME_STATES[-1][2])

    except Exception as e:
        print(f"[volume] Error: {e}")
        return fmt(_MUTED_ICON, 0, _MUTED_COLOR)


def vol_up(qtile=None, step=2):
    """
    Increases system volume by `step` percent.
    """
    volume, _ = get_volume_state()
    if volume < 100:
        increment = min(step, 100 - volume)
        subprocess.run(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{increment}%"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    vol(force=True)


def vol_down(qtile=None, step=2):
    """
    Decreases system volume by `step` percent.
    """
    subprocess.run(
        ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"-{step}%"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    vol(force=True)


def vol_mute(qtile=None):
    """
    Toggles mute on the default sink.
    """
    subprocess.run(
        ["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    vol(force=True)

