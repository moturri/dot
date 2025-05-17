import re
import subprocess
from utils import cached, fmt

# Regex pattern for parsing wpctl output
VOLUME_PATTERN = re.compile(r"Volume:\s+(\d+(?:\.\d+)?)")

# Icons
MUTED_ICON = "󰍭"  # Mic muted
ACTIVE_ICON = "󰍬"  # Mic active

# Color thresholds
MIC_VOLUME_STATES = [
    (70, "salmon"),
    (40, "mediumpurple"),
    (15, "springgreen"),
    (0, "palegreen"),
]

# PipeWire default source (microphone)
DEFAULT_SOURCE = "@DEFAULT_AUDIO_SOURCE@"


def get_mic_state() -> tuple[int, bool]:
    """
    Returns current microphone volume (0–100) and mute status using wpctl.
    """
    try:
        output = (
            subprocess.check_output(
                ["wpctl", "get-volume", DEFAULT_SOURCE], stderr=subprocess.DEVNULL
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
        print(f"[mic] get_mic_state error: {e}")
        return 0, True


@cached(0.5)
def mic() -> str:
    """
    Returns formatted microphone widget string (icon + volume + color).
    """
    try:
        volume, muted = get_mic_state()
        icon = MUTED_ICON if muted else ACTIVE_ICON
        color = (
            "dimgrey"
            if muted
            else next(
                (
                    col
                    for level, col in sorted(MIC_VOLUME_STATES, reverse=True)
                    if volume >= level
                ),
                MIC_VOLUME_STATES[-1][1],
            )
        )
        return fmt(icon, volume, color)
    except Exception as e:
        print(f"[mic] Error: {e}")
        return fmt(MUTED_ICON, 0, "dimgrey")


def mic_up(qtile=None, step=2):
    """
    Increases mic volume by `step` percent, capped at 100%.
    """
    if step <= 0:
        return
    try:
        volume, _ = get_mic_state()
        new_volume = min(100, volume + step)
        subprocess.run(
            ["wpctl", "set-volume", DEFAULT_SOURCE, f"{new_volume / 100:.2f}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[mic_up] Error: {e}")
    mic(force=True)


def mic_down(qtile=None, step=2):
    """
    Decreases mic volume by `step` percent, not below 0%.
    """
    if step <= 0:
        return
    try:
        volume, _ = get_mic_state()
        new_volume = max(0, volume - step)
        subprocess.run(
            ["wpctl", "set-volume", DEFAULT_SOURCE, f"{new_volume / 100:.2f}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[mic_down] Error: {e}")
    mic(force=True)


def mic_mute(qtile=None):
    """
    Toggles microphone mute.
    """
    try:
        subprocess.run(
            ["wpctl", "set-mute", DEFAULT_SOURCE, "toggle"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[mic_mute] Error: {e}")
    mic(force=True)


def mic_set(level: int):
    """
    Sets microphone volume to a specific level (0–100%).
    """
    level = max(0, min(level, 100))
    try:
        subprocess.run(
            ["wpctl", "set-volume", DEFAULT_SOURCE, f"{level / 100:.2f}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:
        print(f"[mic_set] Error: {e}")
    mic(force=True)

