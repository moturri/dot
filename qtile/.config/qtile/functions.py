import functools
import subprocess
import time
import re
from pathlib import Path

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


# ------------------------ VOLUME ------------------------

# ----------------------- amixer -------------------------
# def get_current_volume():
#     try:
#         output = subprocess.check_output("amixer get Master", shell=True).decode()
#         match = re.search(r"\[(\d+)%\]", output)
#         return int(match.group(1)) if match else 0
#     except Exception:
#         return 0
#
#
# @cached(1)
# def vol():
#     try:
#         output = subprocess.check_output("amixer get Master", shell=True).decode()
#         volume_match = re.search(r"\[(\d+)%\]", output)
#         mute_match = re.search(r"\[(on|off)\]", output)
#         volume = int(volume_match.group(1)) if volume_match else 0
#         muted = mute_match and mute_match.group(1) == "off"
#     except Exception:
#         return fmt("󰖁", 0, "dimgrey")
#
#     if muted:
#         return fmt("󰝟", volume, "dimgrey")
#     elif volume >= 70:
#         return fmt("󰕾", volume, "salmon")
#     elif volume >= 40:
#         return fmt("󰖀", volume, "orchid")
#     elif volume > 0:
#         return fmt("󰕿", volume, "springgreen")
#     else:
#         return fmt("󰕿", volume, "palegreen")
#
#
# def vol_up(qtile=None):
#     subprocess.run("amixer set Master 2%+", shell=True)
#     vol(force=True)
#
#
# def vol_down(qtile=None):
#     subprocess.run("amixer set Master 2%-", shell=True)
#     vol(force=True)
#
#
# def vol_mute(qtile=None):
#     subprocess.run("amixer set Master toggle", shell=True)
#     vol(force=True)


# --------------------------- pactl ------------------------------------
# def get_current_volume():
#     try:
#         output = subprocess.check_output("pactl get-sink-volume @DEFAULT_SINK@", shell=True).decode()
#         match = re.search(r'(\d+)%', output)
#         return int(match.group(1)) if match else 0
#     except Exception:
#         return 0
#
#
# @cached(1)
# def vol():
#     try:
#         output = subprocess.check_output("pactl get-sink-volume @DEFAULT_SINK@", shell=True).decode()
#         mute_status = subprocess.check_output("pactl get-sink-mute @DEFAULT_SINK@", shell=True).decode()
#         match = re.search(r'(\d+)%', output)
#         volume = int(match.group(1)) if match else 0
#         muted = "yes" in mute_status.lower()
#     except Exception:
#         return fmt("󰖁", 0, "dimgrey")
#
#     if muted:
#         return fmt("󰝟", volume, "dimgrey")
#     elif volume >= 70:
#         return fmt("󰕾", volume, "salmon")
#     elif volume >= 40:
#         return fmt("󰖀", volume, "orchid")
#     elif volume > 0:
#         return fmt("󰕿", volume, "springgreen")
#     else:
#         return fmt("󰕿", volume, "palegreen")
#
#
# def vol_up(qtile=None):
#     current = get_current_volume()
#     if current < 100:
#         increment = min(2, 100 - current)
#         subprocess.run(f"pactl set-sink-volume @DEFAULT_SINK@ +{increment}%", shell=True)
#     vol(force=True)
#
#
# def vol_down(qtile=None):
#     subprocess.run("pactl set-sink-volume @DEFAULT_SINK@ -2%", shell=True)
#     vol(force=True)
#
#
# def vol_mute(qtile=None):
#     subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ toggle", shell=True)
#     vol(force=True)


# ------------------------ wpctl ------------------------------


def get_current_volume():
    try:
        output = subprocess.check_output(
            "pactl get-sink-volume @DEFAULT_SINK@", shell=True
        ).decode()
        match = re.search(r"(\d+)%", output)
        return int(match.group(1)) if match else 0
    except Exception:
        return 0


@cached(1)
def vol():
    try:
        output = subprocess.check_output(
            "pactl get-sink-volume @DEFAULT_SINK@", shell=True
        ).decode()
        mute_status = subprocess.check_output(
            "pactl get-sink-mute @DEFAULT_SINK@", shell=True
        ).decode()
        match = re.search(r"(\d+)%", output)
        volume = int(match.group(1)) if match else 0
        muted = "yes" in mute_status.lower()
    except Exception:
        return fmt("󰖁", 0, "dimgrey")

    if muted:
        return fmt("󰝟", volume, "dimgrey")
    elif volume >= 70:
        return fmt("󰕾", volume, "salmon")
    elif volume >= 40:
        return fmt("󰖀", volume, "orchid")
    elif volume > 0:
        return fmt("󰕿", volume, "springgreen")
    else:
        return fmt("󰕿", volume, "palegreen")


def vol_up(qtile=None):
    current = get_current_volume()
    if current < 100:
        increment = min(2, 100 - current)
        subprocess.run(
            f"pactl set-sink-volume @DEFAULT_SINK@ +{increment}%", shell=True
        )
    vol(force=True)


def vol_down(qtile=None):
    subprocess.run("pactl set-sink-volume @DEFAULT_SINK@ -2%", shell=True)
    vol(force=True)


def vol_mute(qtile=None):
    subprocess.run("pactl set-sink-mute @DEFAULT_SINK@ toggle", shell=True)
    vol(force=True)


# ------------------------ MICROPHONE ------------------------

# ------------------------ amixer ----------------------------
# def get_current_mic_volume():
#     try:
#         output = subprocess.check_output("amixer get Capture", shell=True).decode()
#         match = re.search(r"\[(\d+)%\]", output)
#         return int(match.group(1)) if match else 0
#     except Exception:
#         return 0
#
#
# @cached(1)
# def mic():
#     try:
#         output = subprocess.check_output("amixer get Capture", shell=True).decode()
#         volume_match = re.search(r"\[(\d+)%\]", output)
#         mute_match = re.search(r"\[(on|off)\]", output)
#         volume = int(volume_match.group(1)) if volume_match else 0
#         muted = mute_match and mute_match.group(1) == "off"
#     except Exception:
#         return fmt("󰍭", 0, "dimgrey")
#
#     icon = "󰍭" if muted else "󰍬"
#     if muted:
#         color = "dimgrey"
#     elif volume >= 70:
#         color = "salmon"
#     elif volume >= 40:
#         color = "violet"
#     elif volume > 0:
#         color = "springgreen"
#     else:
#         color = "palegreen"
#
#     return fmt(icon, volume, color)
#
#
# def mic_up(qtile=None):
#     subprocess.run("amixer set Capture 2%+", shell=True)
#     mic(force=True)
#
#
# def mic_down(qtile=None):
#     subprocess.run("amixer set Capture 2%-", shell=True)
#     mic(force=True)
#
#
# def mic_mute(qtile=None):
#     subprocess.run("amixer set Capture toggle", shell=True)
#     mic(force=True)

# ------------------------- pactl ------------------------------
# def get_current_mic_volume():
#     try:
#         output = subprocess.check_output("pactl get-source-volume @DEFAULT_SOURCE@", shell=True).decode()
#         match = re.search(r'(\d+)%', output)
#         return int(match.group(1)) if match else 0
#     except Exception:
#         return 0
#
#
# @cached(1)
# def mic():
#     try:
#         output = subprocess.check_output("pactl get-source-volume @DEFAULT_SOURCE@", shell=True).decode()
#         mute_status = subprocess.check_output("pactl get-source-mute @DEFAULT_SOURCE@", shell=True).decode()
#         match = re.search(r'(\d+)%', output)
#         volume = int(match.group(1)) if match else 0
#         muted = "yes" in mute_status.lower()
#     except Exception:
#         return fmt("󰍭", 0, "dimgrey")
#
#     icon = "󰍭" if muted else "󰍬"
#     if muted:
#         color = "dimgrey"
#     elif volume >= 70:
#         color = "salmon"
#     elif volume >= 40:
#         color = "violet"
#     elif volume > 0:
#         color = "springgreen"
#     else:
#         color = "palegreen"
#
#     return fmt(icon, volume, color)
#
#
# def mic_up(qtile=None):
#     current = get_current_mic_volume()
#     if current < 100:
#         increment = min(2, 100 - current)
#         subprocess.run(f"pactl set-source-volume @DEFAULT_SOURCE@ +{increment}%", shell=True)
#     mic(force=True)
#
#
# def mic_down(qtile=None):
#     subprocess.run("pactl set-source-volume @DEFAULT_SOURCE@ -2%", shell=True)
#     mic(force=True)
#
#
# def mic_mute(qtile=None):
#     subprocess.run("pactl set-source-mute @DEFAULT_SOURCE@ toggle", shell=True)
#     mic(force=True)

# ------------------------ wpctl -----------------------------


def get_current_mic_volume():
    try:
        output = subprocess.check_output(
            "pactl get-source-volume @DEFAULT_SOURCE@", shell=True
        ).decode()
        match = re.search(r"(\d+)%", output)
        return int(match.group(1)) if match else 0
    except Exception:
        return 0


@cached(1)
def mic():
    try:
        output = subprocess.check_output(
            "pactl get-source-volume @DEFAULT_SOURCE@", shell=True
        ).decode()
        mute_status = subprocess.check_output(
            "pactl get-source-mute @DEFAULT_SOURCE@", shell=True
        ).decode()
        match = re.search(r"(\d+)%", output)
        volume = int(match.group(1)) if match else 0
        muted = "yes" in mute_status.lower()
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
    current = get_current_mic_volume()
    if current < 100:
        increment = min(2, 100 - current)
        subprocess.run(
            f"pactl set-source-volume @DEFAULT_SOURCE@ +{increment}%", shell=True
        )
    mic(force=True)


def mic_down(qtile=None):
    subprocess.run("pactl set-source-volume @DEFAULT_SOURCE@ -2%", shell=True)
    mic(force=True)


def mic_mute(qtile=None):
    subprocess.run("pactl set-source-mute @DEFAULT_SOURCE@ toggle", shell=True)
    mic(force=True)


# ------------------------ BRIGHTNESS ------------------------


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


# ------------------------ BATTERY ------------------------


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
