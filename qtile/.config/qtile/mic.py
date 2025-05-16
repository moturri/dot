import re
import subprocess
from utils import cached, fmt

# Icons
_MUTED_ICON = "󰍭"
_ACTIVE_ICON = "󰍬"

# Volume thresholds and colors
_MIC_VOLUME_STATES = [
    (70, "salmon"),
    (40, "mediumpurple"),
    (15, "springgreen"),
    (0, "palegreen"),
]


def get_mic_state() -> tuple[int, bool]:
    """
    Returns the current microphone volume and mute status.
    Returns (0, True) if data cannot be retrieved.
    """
    try:
        vol_output = subprocess.check_output(
            ["pactl", "get-source-volume", "@DEFAULT_SOURCE@"],
            stderr=subprocess.DEVNULL,
        ).decode()
        mute_output = subprocess.check_output(
            ["pactl", "get-source-mute", "@DEFAULT_SOURCE@"],
            stderr=subprocess.DEVNULL,
        ).decode()

        match = re.search(r"(\d+)%", vol_output)
        volume = int(match.group(1)) if match else 0
        muted = "yes" in mute_output.lower()
        return volume, muted
    except Exception as e:
        print(f"[mic] get_mic_state error: {e}")
        return 0, True


@cached(0.5)
def mic() -> str:
    """
    Returns formatted microphone widget string.
    """
    try:
        volume, muted = get_mic_state()
        icon = _MUTED_ICON if muted else _ACTIVE_ICON
        color = (
            "dimgrey"
            if muted
            else next(
                (col for level, col in _MIC_VOLUME_STATES if volume >= level),
                "palegreen",
            )
        )
        return fmt(icon, volume, color)
    except Exception as e:
        print(f"[mic] Error: {e}")
        return fmt(_MUTED_ICON, 0, "dimgrey")


def mic_up(qtile=None, step=2):
    """
    Increases microphone volume by `step` percent.
    """
    volume, _ = get_mic_state()
    if volume < 100:
        increment = min(step, 100 - volume)
        subprocess.run(
            ["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"+{increment}%"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    mic(force=True)


def mic_down(qtile=None, step=2):
    """
    Decreases microphone volume by `step` percent.
    """
    subprocess.run(
        ["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"-{step}%"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    mic(force=True)


def mic_mute(qtile=None):
    """
    Toggles microphone mute.
    """
    subprocess.run(
        ["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    mic(force=True)
