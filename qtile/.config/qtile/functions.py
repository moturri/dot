import functools
import subprocess
import time
from pathlib import Path

from alsaaudio import Mixer

_FMT = '<span foreground="{}">{}  {:>3}%</span>'

_BAT_CAPACITY_PATH = Path("/sys/class/power_supply/BAT0/capacity")
_AC_ONLINE_PATHS = tuple(
    p / "online" for p in Path("/sys/class/power_supply").glob("AC*")
)

_BRIGHTNESS_PATH = Path("/sys/class/backlight/intel_backlight/brightness")
_MAX_BRIGHTNESS_PATH = Path("/sys/class/backlight/intel_backlight/max_brightness")

_BATTERY_STATES = (
    (80, "", ("lime", "aqua")),
    (60, "", ("palegreen", "aqua")),
    (40, "", ("orange", "aqua")),
    (20, "", ("coral", "aqua")),
    (0, "", ("red", "aqua")),
)


def cached(seconds):
    def wrap(fn):
        cache = ["", 0.0]

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
    return _FMT.format(color, icon, val)


@cached(1)
def vol():
    try:
        mixer = Mixer("Master")
        v = mixer.getvolume()[0]
        muted = mixer.getmute()[0] == 1
    except Exception:
        return fmt("󰖁", 0, "dimgrey")

    if muted:
        return fmt("󰝟", v, "dimgrey")
    elif v >= 70:
        return fmt("󰕾", v, "salmon")
    elif v >= 40:
        return fmt("󰖀", v, "orchid")
    elif v > 0:
        return fmt("󰕿", v, "springgreen")
    else:
        return fmt("󰕿", v, "palegreen")


def vol_up(qtile=None):
    mixer = Mixer("Master")
    v = mixer.getvolume()[0]
    mixer.setvolume(min(100, v + 5))
    vol(force=True)


def vol_down(qtile=None):
    mixer = Mixer("Master")
    v = mixer.getvolume()[0]
    mixer.setvolume(max(0, v - 5))
    vol(force=True)


def vol_mute(qtile=None):
    mixer = Mixer("Master")
    mixer.setmute(1 if mixer.getmute()[0] == 0 else 0)
    vol(force=True)


@cached(1)
def mic():
    try:
        # Get the current microphone volume and mute status using amixer
        output = subprocess.check_output("amixer get Capture", shell=True).decode()
        volume = int(output.split("[")[1].split("%")[0].strip())
        muted = "off" in output
    except Exception:
        return fmt("󰍭", 0, "dimgrey")

    icon = "󰍭" if muted else "󰍬"
    if muted:
        color = "dimgrey"
    elif volume >= 70:
        color = "salmon"
    elif volume >= 40:
        color = "violet"
    elif volume > 0:
        color = "springgreen"
    else:
        color = "palegreen"

    return fmt(icon, volume, color)


def mic_up(qtile=None):
    try:
        subprocess.run("amixer set Capture 5%+", shell=True)
    except Exception:
        pass
    mic(force=True)


def mic_down(qtile=None):
    try:
        subprocess.run("amixer set Capture 5%-", shell=True)
    except Exception:
        pass
    mic(force=True)


def mic_mute(qtile=None):
    try:
        subprocess.run("amixer set Capture toggle", shell=True)
    except Exception:
        pass
    mic(force=True)


@cached(0.3)
def bright():
    try:
        current = int(_BRIGHTNESS_PATH.read_text())
        maximum = int(_MAX_BRIGHTNESS_PATH.read_text())
        v = int((current / maximum) * 100)
    except Exception:
        return '<span foreground="grey">󰳲  --%</span>'

    if v >= 80:
        return fmt("󰃠", v, "gold")
    elif v >= 60:
        return fmt("󰃝", v, "darkorange")
    elif v >= 40:
        return fmt("󰃟", v, "darkorchid")
    elif v >= 20:
        return fmt("󰃞", v, "lightgreen")
    else:
        return fmt("󰃜", v, "dimgrey")


def is_charging():
    for ac_path in _AC_ONLINE_PATHS:
        try:
            if ac_path.exists() and ac_path.read_text().strip() == "1":
                return True
        except (OSError, FileNotFoundError):
            continue
    return False


@cached(10)
def batt():
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
            final_icon = " " + icon if chg else icon
            return fmt(final_icon, v, color)

    return fmt(" " if chg else " ", v, "aqua" if chg else "red")
