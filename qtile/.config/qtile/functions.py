import psutil
import subprocess
import time
from collections import namedtuple

# Define the named tuple for audio info
AudioInfo = namedtuple("AudioInfo", ["volume", "muted"])

# Polling control flag
polling_active = False


def run_command(cmd, timeout=0.5):
    """Runs a shell command and returns the output as a string."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=timeout
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, ValueError, FileNotFoundError):
        return None


def cached_getter(timeout=0.5):
    """Caching decorator to avoid repeated polling within a short time window."""

    def decorator(func):
        cache = {"value": None, "last_check": 0}

        def wrapper(*args, **kwargs):
            current_time = time.time()
            if current_time - cache["last_check"] < timeout and not polling_active:
                return cache["value"]

            result = func(*args, **kwargs)
            cache["value"] = result
            cache["last_check"] = current_time
            return result

        wrapper.cache = cache
        return wrapper

    return decorator


def start_polling():
    global polling_active
    polling_active = True


def stop_polling():
    global polling_active
    polling_active = False


def get_audio_info():
    """Fetches both volume and mute status for Master (volume) and Capture (mic) using amixer."""

    # Run amixer commands separately for Master (volume) and Capture (mic)
    master_cmd = ["amixer", "get", "Master"]
    capture_cmd = ["amixer", "get", "Capture"]

    master_output = run_command(master_cmd)
    capture_output = run_command(capture_cmd)

    if not master_output or not capture_output:
        return AudioInfo(volume=0, muted=True), AudioInfo(volume=0, muted=True)

    # Parse both outputs
    volume_info = parse_amixer_section(master_output)
    mic_info = parse_amixer_section(capture_output)

    return volume_info, mic_info


def parse_amixer_section(section):
    """Helper function to parse a single amixer section (either Master or Capture)."""
    volume = 0
    muted = True

    for line in section.splitlines():
        if "%" in line:
            try:
                # Extract volume and muted status from the line
                vol_str = next(seg for seg in line.split() if "%" in seg)
                volume = int(vol_str.strip("[]%"))
                muted = "[off]" in line
                break  # No need to process further lines
            except Exception:
                continue

    return AudioInfo(volume=volume, muted=muted)


@cached_getter()
def vol():
    volume_info, _ = get_audio_info()
    THRESHOLDS = [
        (80, "󰕾 ", "salmon"),
        (60, "󰕾 ", "tan"),
        (40, "󰕾 ", "violet"),
        (20, "󰖀 ", "springgreen"),
        (0, "󰕿 ", "palegreen"),
    ]

    # Handle muted state
    if volume_info.muted or volume_info.volume == 0:
        return f'<span foreground="dimgrey">󰝟  {volume_info.volume}%</span>'

    # Apply thresholds for volume color coding
    for threshold, icon, color in THRESHOLDS:
        if volume_info.volume >= threshold:
            return f'<span foreground="{color}">{icon} {volume_info.volume}%</span>'


@cached_getter()
def mic():
    _, mic_info = get_audio_info()
    THRESHOLDS = [
        (80, " ", "salmon"),
        (60, " ", "tan"),
        (40, " ", "violet"),
        (20, " ", "springgreen"),
        (0, " ", "palegreen"),
    ]

    # Handle muted state
    if mic_info.muted or mic_info.volume == 0:
        return f'<span foreground="dimgrey">   {mic_info.volume}%</span>'

    # Apply thresholds for mic volume color coding
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
def bright():
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
    except ValueError:
        pass

    return '<span foreground="grey">󰳲 N/A</span>'


@cached_getter()
def batt():
    try:
        battery = psutil.sensors_battery()
        if battery is None:
            raise RuntimeError("No battery is detected")

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
