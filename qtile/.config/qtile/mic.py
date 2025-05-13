import re
import subprocess

from utils import cached, fmt

# Icons
_MUTED_ICON = "󰍭"
_ACTIVE_ICON = "󰍬"

# Volume thresholds and colors
_MIC_VOLUME_STATES = [
    (70, "salmon"),
    (40, "violet"),
    (1, "springgreen"),
    (0, "palegreen"),
]


def get_current_mic_volume() -> int:
    """
    Gets current microphone volume level (0-100).
    Returns 0 if unable to retrieve.
    """
    try:
        output = subprocess.check_output(
            ["pactl", "get-source-volume", "@DEFAULT_SOURCE@"],
            stderr=subprocess.DEVNULL,
        ).decode()
        match = re.search(r"(\d+)%", output)
        return int(match.group(1)) if match else 0
    except Exception as e:
        print(f"[mic] get_current_mic_volume error: {e}")
        return 0


@cached(0.5)
def mic() -> str:
    """
    Returns formatted microphone widget string.
    """
    try:
        vol_output = subprocess.check_output(
            ["pactl", "get-source-volume", "@DEFAULT_SOURCE@"],
            stderr=subprocess.DEVNULL,
        ).decode()
        mute_output = subprocess.check_output(
            ["pactl", "get-source-mute", "@DEFAULT_SOURCE@"], stderr=subprocess.DEVNULL
        ).decode()

        match = re.search(r"(\d+)%", vol_output)
        volume = int(match.group(1)) if match else 0
        muted = "yes" in mute_output.lower()

        icon = _MUTED_ICON if muted else _ACTIVE_ICON
        if muted:
            color = "dimgrey"
        else:
            for level, col in _MIC_VOLUME_STATES:
                if volume >= level:
                    color = col
                    break
            else:
                color = "palegreen"

        return fmt(icon, volume, color)

    except Exception as e:
        print(f"[mic] Error: {e}")
        return fmt(_MUTED_ICON, 0, "dimgrey")


def mic_up(qtile=None):
    current = get_current_mic_volume()
    if current < 100:
        increment = min(2, 100 - current)
        subprocess.run(
            ["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"+{increment}%"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    mic(force=True)


def mic_down(qtile=None):
    subprocess.run(
        ["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "-2%"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    mic(force=True)


def mic_mute(qtile=None):
    subprocess.run(
        ["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    mic(force=True)
