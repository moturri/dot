import subprocess
import re
import time
from pathlib import Path


# ------------ Minimal subprocess wrapper ------------
def run_command(cmd, timeout=0.2):
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
        return result.stdout
    except Exception:
        return ""


# ------------ Cache Config ------------
CACHE_DURATION = 1.0  # seconds
LONG_CACHE_DURATION = 10  # for battery

_last_vol = {"value": "", "timestamp": 0}
_last_mic = {"value": "", "timestamp": 0}
_last_bright = {"value": "", "timestamp": 0}
_last_batt = {"value": "", "timestamp": 0}


def vol(force=False):
    now = time.time()
    if not force and now - _last_vol["timestamp"] < CACHE_DURATION:
        return _last_vol["value"]

    out = run_command(["amixer", "sget", "Master"])

    vol_match = re.search(r"\[([0-9]+)%\]", out)
    mute_match = re.search(r"\[(on|off)\]", out)

    volume = int(vol_match.group(1)) if vol_match else 0
    muted = mute_match.group(1) == "off" if mute_match else True

    if muted:
        icon, color = "󰖁", "dimgrey"
    elif volume >= 70:
        icon, color = "󰕾", "salmon"
    elif volume >= 40:
        icon, color = "󰖀", "violet"
    elif volume > 0:
        icon, color = "󰕿", "springgreen"
    else:
        icon, color = "󰕿", "palegreen"

    result = f'<span foreground="{color}">{icon} {volume:>3}%</span>'
    _last_vol.update(value=result, timestamp=now)
    return result


def mic(force=False):
    now = time.time()
    if not force and now - _last_mic["timestamp"] < CACHE_DURATION:
        return _last_mic["value"]

    out = run_command(["amixer", "sget", "Capture"])

    vol_match = re.search(r"\[([0-9]+)%\]", out)
    mute_match = re.search(r"\[(on|off)\]", out)

    volume = int(vol_match.group(1)) if vol_match else 0
    muted = mute_match.group(1) == "off" if mute_match else True

    icon = "󰍭" if muted else "󰍬"
    color = (
        "dimgrey"
        if muted
        else "salmon"
        if volume >= 70
        else "violet"
        if volume >= 40
        else "springgreen"
        if volume > 0
        else "palegreen"
    )

    result = f'<span foreground="{color}">{icon} {volume:>3}%</span>'
    _last_mic.update(value=result, timestamp=now)
    return result


def bright(force=False):
    now = time.time()
    if not force and now - _last_bright["timestamp"] < CACHE_DURATION:
        return _last_bright["value"]

    out = run_command(["brillo", "-G"])

    try:
        percent = int(float(out.strip()))

        if percent >= 80:
            icon, color = "󰃠", "gold"
        elif percent >= 60:
            icon, color = "󰃝", "darkorange"
        elif percent >= 40:
            icon, color = "󰃟", "orchid"
        elif percent >= 20:
            icon, color = "󰃞", "pink"
        else:
            icon, color = "󰃜", "dimgrey"

        result = f'<span foreground="{color}">{icon}  {percent:>3}%</span>'
    except Exception:
        result = '<span foreground="grey">󰳲  --%</span>'

    _last_bright.update(value=result, timestamp=now)
    return result


BAT_PATH = Path("/sys/class/power_supply/BAT0")
AC_PATH = Path("/sys/class/power_supply/AC/online")


def batt(force=False):
    now = time.time()
    if not force and now - _last_batt["timestamp"] < LONG_CACHE_DURATION:
        return _last_batt["value"]

    if not BAT_PATH.exists():
        return '<span foreground="grey">󰈸  --%</span>'

    try:
        capacity = int((BAT_PATH / "capacity").read_text().strip())
        charging = AC_PATH.exists() and AC_PATH.read_text().strip() == "1"

        if capacity >= 80:
            icon, color = "", "lime"
        elif capacity >= 60:
            icon, color = "", "palegreen"
        elif capacity >= 40:
            icon, color = "", "orange"
        elif capacity >= 20:
            icon, color = "", "coral"
        else:
            icon, color = "", "red"

        if charging:
            icon = f" {icon}"
            color = "aqua"

        result = f'<span foreground="{color}">{icon}  {capacity:>3}%</span>'
    except Exception:
        result = '<span foreground="grey">󰈸  --%</span>'

    _last_batt.update(value=result, timestamp=now)
    return result


def vol_up(qtile=None):
    run_command(["amixer", "-q", "set", "Master", "5%+"])
    vol(force=True)


def vol_down(qtile=None):
    run_command(["amixer", "-q", "set", "Master", "5%-"])
    vol(force=True)


def vol_mute(qtile=None):
    run_command(["amixer", "-q", "set", "Master", "toggle"])
    vol(force=True)


def mic_up(qtile=None):
    run_command(["amixer", "-q", "set", "Capture", "5%+"])
    mic(force=True)


def mic_down(qtile=None):
    run_command(["amixer", "-q", "set", "Capture", "5%-"])
    mic(force=True)


def mic_mute(qtile=None):
    run_command(["amixer", "-q", "set", "Capture", "toggle"])
    mic(force=True)
