import re
import subprocess
import time
from pathlib import Path


def run_command(cmd, timeout=0.5):
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=timeout
        )
        return result.stdout.strip()
    except (subprocess.SubprocessError, ValueError, FileNotFoundError):
        return None


def cached_getter(func, timeout=0.2):
    def wrapper(*args, **kwargs):
        current_time = time.time()
        if current_time - wrapper.cache["last_check"] < timeout:
            return wrapper.cache["value"]

        result = func(*args, **kwargs)
        wrapper.cache["value"] = result
        wrapper.cache["last_check"] = current_time
        return result

    wrapper.cache = {"value": None, "last_check": 0}
    wrapper.func = func

    return wrapper


@cached_getter
def bright(timeout=0.2):
    THRESHOLDS = [
        (80, "󰃠  ", "gold"),
        (60, "󰃝  ", "darkorange"),
        (40, "󰃟  ", "orchid"),
        (20, "󰃞  ", "pink"),
        (0, "󰃜  ", "dimgrey"),
    ]

    output = run_command(["brillo", "-G"])
    if not output:
        return '<span foreground="grey">󰳲 N/A</span>'

    try:
        percent = int(float(output))

        for threshold, icon, color in THRESHOLDS:
            if percent >= threshold:
                return f'<span foreground="{color}">{icon} {percent}%</span>'
    except ValueError:
        pass

    return '<span foreground="grey">󰳲 N/A</span>'


def batt():
    try:
        base = Path("/sys/class/power_supply/")
        battery = next((b for b in base.glob("BAT*") if b.is_dir()), None)
        if not battery:
            raise FileNotFoundError("Battery directory not found")

        capacity = int((battery / "capacity").read_text().strip())
        status = (battery / "status").read_text().strip()

        if capacity > 80:
            icon, color = "  ", "lime"
        elif capacity > 60:
            icon, color = "  ", "palegreen"
        elif capacity > 40:
            icon, color = "  ", "orange"
        elif capacity > 20:
            icon, color = "  ", "coral"
        else:
            icon, color = "  ", "red"

        if status.lower() == "charging":
            icon = f" {icon}"
            color = "aqua"

        return f'<span foreground="{color}">{icon} {capacity}%</span>'

    except Exception:
        return '<span foreground="grey">󰈸 --%</span>'


def get_audio_info(source=False):
    device_type = "source" if source else "sink"
    default_device = f"@DEFAULT_{device_type.upper()}@"

    volume_output = run_command(["pactl", f"get-{device_type}-volume", default_device])
    mute_output = run_command(["pactl", f"get-{device_type}-mute", default_device])

    if volume_output and mute_output:
        volume_match = re.search(r"Volume:.*?(\d+)%", volume_output)
        if volume_match:
            volume = int(volume_match.group(1))
            is_muted = "yes" in mute_output
            return volume, is_muted

    control = "Capture" if source else "Master"
    output = run_command(["amixer", "get", control])

    if output:
        matches = re.findall(r"\[(\d+)%\] \[(on|off)\]", output)
        if matches:
            volume_str, state = matches[-1]
            return int(volume_str), state == "off"

    return 0, True  # Default to 0 volume and muted


@cached_getter
def vol(timeout=0.1):
    THRESHOLDS = [
        (80, "󰕾 ", "tomato"),
        (60, "󰕾 ", "tan"),
        (40, "󰕾 ", "orchid"),
        (20, "󰖀 ", "dodgerblue"),
        (0, "󰕿 ", "dimgrey"),
    ]
    MUTED_ICON = "󰝟 "
    MUTED_COLOR = "dimgrey"

    volume, is_muted = get_audio_info(source=False)

    if is_muted or volume == 0:
        icon, color = MUTED_ICON, MUTED_COLOR
    else:
        for threshold, icon, color in THRESHOLDS:
            if volume > threshold:
                break

    return f'<span foreground="{color}">{icon} {volume}%</span>'


@cached_getter
def mic(timeout=0.1):
    THRESHOLDS = [
        (80, " ", "tomato"),
        (60, " ", "tan"),
        (40, " ", "orchid"),
        (20, " ", "dodgerblue"),
        (0, "  ", "dimgrey"),
    ]
    MUTED_ICON = "  "
    MUTED_COLOR = "dimgrey"

    volume, is_muted = get_audio_info(source=True)

    if is_muted or volume == 0:
        icon, color = MUTED_ICON, MUTED_COLOR
    else:
        for threshold, icon, color in THRESHOLDS:
            if volume > threshold:
                break

    return f'<span foreground="{color}">{icon} {volume}%</span>'


def volume_up(qtile):
    volume, _ = get_audio_info(source=False)

    if volume < 100:
        increment = min(5, 100 - volume)
        if (
            run_command(
                ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"+{increment}%"]
            )
            is None
        ):
            run_command(["amixer", "set", "Master", f"{increment}%+"])
    vol.cache["last_check"] = 0


def volume_down(qtile):
    if run_command(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "-5%"]) is None:
        run_command(["amixer", "set", "Master", "5%-"])
    vol.cache["last_check"] = 0


def volume_mute(qtile):
    if run_command(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "toggle"]) is None:
        run_command(["amixer", "set", "Master", "toggle"])
    vol.cache["last_check"] = 0


def mic_up(qtile):
    volume, _ = get_audio_info(source=True)

    if volume < 100:
        increment = min(5, 100 - volume)
        if (
            run_command(
                ["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"+{increment}%"]
            )
            is None
        ):
            run_command(["amixer", "set", "Capture", f"{increment}%+"])
    mic.cache["last_check"] = 0


def mic_down(qtile):
    if run_command(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "-5%"]) is None:
        run_command(["amixer", "set", "Capture", "5%-"])
    mic.cache["last_check"] = 0


def mic_mute(qtile):
    if run_command(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"]) is None:
        run_command(["amixer", "set", "Capture", "toggle"])
    mic.cache["last_check"] = 0
