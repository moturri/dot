import psutil
import subprocess
import logging
import re
from collections import namedtuple
from typing import Optional, Tuple, List

# Setup logging
logging.basicConfig(level=logging.WARNING)

# Named tuple for audio info
AudioInfo = namedtuple("AudioInfo", ["volume", "muted"])

# Cache stores for volume, mic, etc.
CACHE = {"volume": None, "mic": None, "brightness": None, "battery": None}


# Command execution helper function
def run_command(cmd: List[str], timeout: float = 1.0) -> Optional[str]:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.SubprocessError as e:
        logging.warning(f"Command failed: {' '.join(cmd)} | {e}")
        return None


# Audio info parsing
def parse_amixer_output(output: str) -> AudioInfo:
    volume_match = re.search(r"\[([0-9]+)%\]", output)
    mute_match = re.search(r"\[(on|off)\]", output)

    volume = int(volume_match.group(1)) if volume_match else 0
    muted = mute_match.group(1) == "off" if mute_match else True

    return AudioInfo(volume=volume, muted=muted)


# Fetch audio info (volume and mic state)
def get_audio_info() -> Tuple[AudioInfo, AudioInfo]:
    master_output = run_command(["amixer", "get", "Master"])
    capture_output = run_command(["amixer", "get", "Capture"])

    default_info = AudioInfo(volume=0, muted=True)

    volume_info = parse_amixer_output(master_output) if master_output else default_info
    mic_info = parse_amixer_output(capture_output) if capture_output else default_info

    return volume_info, mic_info


# --- Volume Display ---
def vol() -> str:
    # Use cached value if unchanged
    if CACHE["volume"]:
        volume_info = CACHE["volume"]
    else:
        volume_info, _ = get_audio_info()
        CACHE["volume"] = volume_info  # Update cache with latest value

    if volume_info.muted or volume_info.volume == 0:
        return f'<span foreground="dimgrey">󰝟  {volume_info.volume}%</span>'

    THRESHOLDS = [
        (80, "󰕾 ", "salmon"),
        (60, "󰕾 ", "tan"),
        (40, "󰕾 ", "violet"),
        (20, "󰖀 ", "springgreen"),
        (0, "󰕿 ", "palegreen"),
    ]

    for threshold, icon, color in THRESHOLDS:
        if volume_info.volume >= threshold:
            return f'<span foreground="{color}">{icon} {volume_info.volume}%</span>'


# --- Microphone Display ---
def mic() -> str:
    # Use cached value if unchanged
    if CACHE["mic"]:
        _, mic_info = CACHE["mic"]
    else:
        _, mic_info = get_audio_info()
        CACHE["mic"] = (_, mic_info)  # Update cache with latest value

    if mic_info.muted or mic_info.volume == 0:
        return f'<span foreground="dimgrey">   {mic_info.volume}%</span>'

    THRESHOLDS = [
        (80, " ", "salmon"),
        (60, " ", "tan"),
        (40, " ", "violet"),
        (20, " ", "springgreen"),
        (0, " ", "palegreen"),
    ]

    for threshold, icon, color in THRESHOLDS:
        if mic_info.volume >= threshold:
            return f'<span foreground="{color}">{icon} {mic_info.volume}%</span>'


# --- Volume Controls ---
def volume_up(qtile=None):
    run_command(["amixer", "set", "Master", "5%+"])
    # Reset cache to ensure next fetch pulls fresh data
    CACHE["volume"] = None


def volume_down(qtile=None):
    run_command(["amixer", "set", "Master", "5%-"])
    # Reset cache to ensure next fetch pulls fresh data
    CACHE["volume"] = None


def volume_mute(qtile=None):
    run_command(["amixer", "set", "Master", "toggle"])
    # Reset cache to ensure next fetch pulls fresh data
    CACHE["volume"] = None


# --- Microphone Controls ---
def mic_up(qtile=None):
    run_command(["amixer", "set", "Capture", "5%+"])
    # Reset cache to ensure next fetch pulls fresh data
    CACHE["mic"] = None


def mic_down(qtile=None):
    run_command(["amixer", "set", "Capture", "5%-"])
    # Reset cache to ensure next fetch pulls fresh data
    CACHE["mic"] = None


def mic_mute(qtile=None):
    run_command(["amixer", "set", "Capture", "toggle"])
    # Reset cache to ensure next fetch pulls fresh data
    CACHE["mic"] = None


# --- Brightness Display ---
def bright() -> str:
    # Fetch brightness using 'brillo -G' each time to ensure it is updated
    output = run_command(["brillo", "-G"])

    if output is None:
        result = '<span foreground="grey">󰳲 N/A</span>'
        return result

    try:
        # Parse the brightness percentage from the command output
        percent = int(float(output.strip()))

        # Define brightness levels and associated icons
        THRESHOLDS = [
            (80, "󰃠  ", "gold"),
            (60, "󰃝  ", "darkorange"),
            (40, "󰃟  ", "orchid"),
            (20, "󰃞  ", "pink"),
            (0, "󰃜 ", "dimgrey"),
        ]

        # Check the brightness level and return the appropriate icon and color
        for threshold, icon, color in THRESHOLDS:
            if percent >= threshold:
                result = f'<span foreground="{color}">{icon} {percent}%</span>'
                return result

    except (ValueError, TypeError) as e:
        logging.warning(f"Brightness parsing error: {e}")
        result = '<span foreground="grey">󰳲 Error</span>'
        return result

    # Default fallback if parsing fails
    result = '<span foreground="grey">󰳲 N/A</span>'
    return result


# --- Battery Display ---
def batt() -> str:
    try:
        # Fetch battery status
        battery = psutil.sensors_battery()
        if battery is None:
            return '<span foreground="grey">󰈸 No Battery</span>'

        # Get battery percentage and charging status
        capacity = int(battery.percent)
        charging = battery.power_plugged

        # Define battery icon and colors based on capacity
        if capacity >= 80:
            icon, color = "  ", "lime"
        elif capacity >= 60:
            icon, color = "  ", "palegreen"
        elif capacity >= 40:
            icon, color = "  ", "orange"
        elif capacity >= 20:
            icon, color = "  ", "coral"
        else:
            icon, color = "  ", "red"

        # If charging, display a different icon
        if charging:
            icon = f" {icon}"
            color = "aqua"

        # Return the formatted result
        return f'<span foreground="{color}">{icon} {capacity}%</span>'

    except Exception as e:
        logging.warning(f"Battery reading error: {e}")
        return '<span foreground="grey">󰈸 --%</span>'
