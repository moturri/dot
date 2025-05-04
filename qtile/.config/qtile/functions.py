import psutil
import subprocess
import time
import re
from collections import namedtuple
from typing import Optional, Tuple, List, Callable

# Define the named tuple for audio info
AudioInfo = namedtuple("AudioInfo", ["volume", "muted"])


# Define a class to handle polling state
class PollingManager:
    def __init__(self):
        self.active = False

    def start(self):
        self.active = True

    def stop(self):
        self.active = False


polling = PollingManager()


def run_command(cmd: List[str], timeout: float = 1.0) -> Optional[str]:
    """
    Runs a shell command and returns the output as a string.
    """
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=timeout
        )
        return result.stdout.strip()
    except subprocess.SubprocessError as e:
        print(f"Command failed: {' '.join(cmd)}, Error: {e}")
        return None


def cached_getter(timeout: float = 0.5):
    """
    Caching decorator to avoid repeated polling within a short time window.
    """

    def decorator(func: Callable):
        cache = {"value": None, "last_check": 0}

        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - cache["last_check"] < timeout and not polling.active:
                return cache["value"]

            result = func(*args, **kwargs)
            cache["value"] = result
            cache["last_check"] = current_time
            return result

        wrapper.cache = cache
        return wrapper

    return decorator


def start_polling():
    polling.start()


def stop_polling():
    polling.stop()


def get_audio_info() -> Tuple[AudioInfo, AudioInfo]:
    """
    Fetches both volume and mute status for Master (volume) and Capture (mic).
    """
    master_cmd = ["amixer", "get", "Master"]
    capture_cmd = ["amixer", "get", "Capture"]

    master_output = run_command(master_cmd)
    capture_output = run_command(capture_cmd)

    default_info = AudioInfo(volume=0, muted=True)

    volume_info = parse_amixer_section(master_output) if master_output else default_info
    mic_info = parse_amixer_section(capture_output) if capture_output else default_info

    return volume_info, mic_info


def parse_amixer_section(section: str) -> AudioInfo:
    """
    Helper function to parse a single amixer section.
    """
    volume = 0
    muted = True

    volume_match = re.search(r"(\d+)%", section)
    mute_match = re.search(r"\[(on|off)\]", section)

    if volume_match:
        volume = int(volume_match.group(1))

    if mute_match:
        muted = mute_match.group(1) == "off"

    return AudioInfo(volume=volume, muted=muted)


@cached_getter()
def vol() -> str:
    """
    Get formatted volume indicator string with icon and color.
    """
    volume_info, _ = get_audio_info()
    THRESHOLDS = [
        (80, "󰕾 ", "salmon"),
        (60, "󰕾 ", "tan"),
        (40, "󰕾 ", "violet"),
        (20, "󰖀 ", "springgreen"),
        (0, "󰕿 ", "palegreen"),
    ]

    if volume_info.muted or volume_info.volume == 0:
        return f'<span foreground="dimgrey">󰝟  {volume_info.volume}%</span>'

    for threshold, icon, color in THRESHOLDS:
        if volume_info.volume >= threshold:
            return f'<span foreground="{color}">{icon} {volume_info.volume}%</span>'


@cached_getter()
def mic() -> str:
    """
    Get formatted microphone indicator string.
    """
    _, mic_info = get_audio_info()
    THRESHOLDS = [
        (80, " ", "salmon"),
        (60, " ", "tan"),
        (40, " ", "violet"),
        (20, " ", "springgreen"),
        (0, " ", "palegreen"),
    ]

    if mic_info.muted or mic_info.volume == 0:
        return f'<span foreground="dimgrey">   {mic_info.volume}%</span>'

    for threshold, icon, color in THRESHOLDS:
        if mic_info.volume >= threshold:
            return f'<span foreground="{color}">{icon} {mic_info.volume}%</span>'


def volume_up(qtile):
    run_command(["amixer", "set", "Master", "5%+"])
    vol.cache["last_check"] = 0


def volume_down(qtile):
    run_command(["amixer", "set", "Master", "5%-"])
    vol.cache["last_check"] = 0


def volume_mute(qtile):
    run_command(["amixer", "set", "Master", "toggle"])
    vol.cache["last_check"] = 0


def mic_up(qtile):
    run_command(["amixer", "set", "Capture", "5%+"])
    mic.cache["last_check"] = 0


def mic_down(qtile):
    run_command(["amixer", "set", "Capture", "5%-"])
    mic.cache["last_check"] = 0


def mic_mute(qtile):
    run_command(["amixer", "set", "Capture", "toggle"])
    mic.cache["last_check"] = 0


@cached_getter()
def bright() -> str:
    """
    Get formatted brightness indicator string.
    """
    THRESHOLDS = [
        (80, "󰃠  ", "gold"),
        (60, "󰃝  ", "darkorange"),
        (40, "󰃟  ", "orchid"),
        (20, "󰃞  ", "pink"),
        (0, "󰃜 ", "dimgrey"),
    ]

    output = run_command(["brillo", "-G"])
    if not output:
        return '<span foreground="grey">󰳲 N/A</span>'

    try:
        percent = int(float(output.strip()))
        for threshold, icon, color in THRESHOLDS:
            if percent >= threshold:
                return f'<span foreground="{color}">{icon} {percent}%</span>'
    except (ValueError, TypeError):
        return '<span foreground="grey">󰳲 Error</span>'

    return '<span foreground="grey">󰳲 N/A</span>'


@cached_getter()
def batt() -> str:
    """
    Get formatted battery indicator string with icon and color.
    """
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            return '<span foreground="grey">󰈸 No Battery</span>'

        capacity = int(battery.percent)
        charging = battery.power_plugged
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

        if charging:
            icon = f" {icon}"
            color = "aqua"

        return f'<span foreground="{color}">{icon} {capacity}%</span>'

    except Exception:
        return '<span foreground="grey">󰈸 --%</span>'
