import subprocess
import time
import functools
from pathlib import Path

# Pre-computed constants
_FMT = '<span foreground="{}">{} {:>3}%</span>'
_BAT_CAPACITY_PATH = Path("/sys/class/power_supply/BAT0/capacity")
_AC_ONLINE_PATHS = tuple(
    p / "online" for p in Path("/sys/class/power_supply").glob("AC*")
)
_BATTERY_STATES = (
    (80, " ", ("lime", "aqua")),
    (60, " ", ("palegreen", "aqua")),
    (40, " ", ("orange", "aqua")),
    (20, " ", ("coral", "aqua")),
    (0, " ", ("red", "aqua")),
)


def run(cmd, timeout=0.15):
    """Run a command with minimal overhead"""
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            bufsize=-1,
            shell=False,
            check=False,
        ).stdout.strip()
    except subprocess.TimeoutExpired:
        return ""


def cached(seconds):
    """Cache decorator with zero-allocation design"""

    def wrap(fn):
        cache = ["", 0.0]  # [value, timestamp]

        @functools.wraps(fn)
        def inner(force=False):
            now = time.monotonic()
            if not force and now - cache[1] < seconds:
                return cache[0]
            out = fn()
            if out:
                cache[0], cache[1] = out, now
            return cache[0]

        return inner

    return wrap


def fmt(icon, val, color):
    """Format output string with minimal allocations"""
    return _FMT.format(color, icon, val)


# Audio sink (output) management
@cached(1)
def vol():
    """Get volume status with lazy parsing"""
    out = run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
    if "Volume:" not in out:
        return fmt("󰖁", 0, "dimgrey")

    parts = out.split("Volume:")
    if len(parts) < 2:
        return fmt("󰖁", 0, "dimgrey")

    try:
        v = int(float(parts[1].split()[0]) * 100)
    except (ValueError, IndexError):
        return fmt("󰖁", 0, "dimgrey")

    muted = "[MUTED]" in out

    if muted:
        return fmt("󰖁", v, "dimgrey")
    elif v >= 70:
        return fmt("󰕾", v, "salmon")
    elif v >= 40:
        return fmt("󰖀", v, "violet")
    elif v > 0:
        return fmt("󰕿", v, "springgreen")
    else:
        return fmt("󰕿", v, "palegreen")


def vol_up(qtile=None):
    run(["wpctl", "set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", "0.05+"])
    vol(force=True)


def vol_down(qtile=None):
    run(["wpctl", "set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", "0.05-"])
    vol(force=True)


def vol_mute(qtile=None):
    run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
    vol(force=True)


# Audio source (microphone) management
@cached(1)
def mic():
    """Get microphone status with lazy parsing"""
    out = run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"])
    if "Volume:" not in out:
        return fmt("󰍭", 0, "dimgrey")

    parts = out.split("Volume:")
    if len(parts) < 2:
        return fmt("󰍭", 0, "dimgrey")

    try:
        v = int(float(parts[1].split()[0]) * 100)
    except (ValueError, IndexError):
        return fmt("󰍭", 0, "dimgrey")

    muted = "[MUTED]" in out
    icon = "󰍭" if muted else "󰍬"

    if muted:
        color = "dimgrey"
    elif v >= 70:
        color = "salmon"
    elif v >= 40:
        color = "violet"
    elif v > 0:
        color = "springgreen"
    else:
        color = "palegreen"

    return fmt(icon, v, color)


def mic_up(qtile=None):
    run(["wpctl", "set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SOURCE@", "0.05+"])
    mic(force=True)


def mic_down(qtile=None):
    run(["wpctl", "set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SOURCE@", "0.05-"])
    mic(force=True)


def mic_mute(qtile=None):
    run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SOURCE@", "toggle"])
    mic(force=True)


# Brightness management
@cached(0.3)
def bright():
    """Get brightness with minimal processing"""
    try:
        v = int(float(run(["brillo", "-G"])))
    except (ValueError, TypeError):
        return '<span foreground="grey">󰳲  --%</span>'

    if v >= 80:
        return fmt("󰃠 ", v, "gold")
    elif v >= 60:
        return fmt("󰃝 ", v, "darkorange")
    elif v >= 40:
        return fmt("󰃟 ", v, "orchid")
    elif v >= 20:
        return fmt("󰃞 ", v, "pink")
    else:
        return fmt("󰃜", v, "dimgrey")


def is_charging():
    """Check charging status with minimal file operations"""
    for ac_path in _AC_ONLINE_PATHS:
        try:
            if ac_path.exists() and ac_path.read_text().strip() == "1":
                return True
        except (OSError, FileNotFoundError):
            continue
    return False


@cached(3)
def batt():
    """Get battery status with minimal file operations"""
    try:
        if not _BAT_CAPACITY_PATH.exists():
            return '<span foreground="grey">  --%</span>'
        v = int(_BAT_CAPACITY_PATH.read_text().strip())
    except (OSError, ValueError):
        return '<span foreground="grey">  --%</span>'

    chg = is_charging()

    for threshold, icon, (normal_color, charging_color) in _BATTERY_STATES:
        if v >= threshold:
            color = charging_color if chg else normal_color
            final_icon = "" + icon if chg else icon  # Add lightning icon if charging
            return fmt(final_icon, v, color)

    return fmt("" if chg else " ", v, "aqua" if chg else "red")
