import subprocess
import time
import functools
from pathlib import Path


def run(cmd, timeout=0.2):
    try:
        return subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        ).stdout.strip()
    except subprocess.SubprocessError:
        return ""


def cached(seconds):
    def wrap(fn):
        cache = {"val": "", "ts": 0}

        @functools.wraps(fn)
        def inner(force=False):
            now = time.time()
            if not force and now - cache["ts"] < seconds:
                return cache["val"]
            out = fn()
            if out:
                cache["val"], cache["ts"] = out, now
            return out

        return inner

    return wrap


def fmt(icon, val, color):
    return f'<span foreground="{color}">{icon} {val:>3}%</span>'


@cached(1)
def vol():
    out = run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
    if "Volume:" not in out:
        return fmt("󰖁", 0, "dimgrey")
    try:
        v = int(float(out.split("Volume:")[1].split()[0]) * 100)
    except (ValueError, IndexError):
        return fmt("󰖁", 0, "dimgrey")
    if "[MUTED]" in out:
        return fmt("󰖁", v, "dimgrey")
    return fmt(
        "󰕾" if v >= 70 else "󰖀" if v >= 40 else "󰕿",
        v,
        "salmon"
        if v >= 70
        else "violet"
        if v >= 40
        else "springgreen"
        if v > 0
        else "palegreen",
    )


def vol_up(qtile=None):
    run(["wpctl", "set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", "0.05+"])
    vol(force=True)


def vol_down(qtile=None):
    run(["wpctl", "set-volume", "-l", "1.0", "@DEFAULT_AUDIO_SINK@", "0.05-"])
    vol(force=True)


def vol_mute(qtile=None):
    run(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "toggle"])
    vol(force=True)


@cached(1)
def mic():
    out = run(["wpctl", "get-volume", "@DEFAULT_AUDIO_SOURCE@"])
    if "Volume:" not in out:
        return fmt("󰍭", 0, "dimgrey")
    try:
        v = int(float(out.split("Volume:")[1].split()[0]) * 100)
    except (ValueError, IndexError):
        return fmt("󰍭", 0, "dimgrey")
    muted = "[MUTED]" in out
    icon = "󰍭" if muted else "󰍬"
    color = (
        "dimgrey"
        if muted
        else "salmon"
        if v >= 70
        else "violet"
        if v >= 40
        else "springgreen"
        if v > 0
        else "palegreen"
    )
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


@cached(0.3)
def bright():
    try:
        v = int(float(run(["brillo", "-G"])))
    except (ValueError, TypeError):
        return '<span foreground="grey">󰳲  --%</span>'
    return fmt(
        "󰃠 "
        if v >= 80
        else "󰃝 "
        if v >= 60
        else "󰃟 "
        if v >= 40
        else "󰃞 "
        if v >= 20
        else "󰃜",
        v,
        "gold"
        if v >= 80
        else "darkorange"
        if v >= 60
        else "orchid"
        if v >= 40
        else "pink"
        if v >= 20
        else "dimgrey",
    )


def is_charging():
    for ac in Path("/sys/class/power_supply").glob("AC*"):
        try:
            if ac.joinpath("online").read_text().strip() == "1":
                return True
        except (OSError, FileNotFoundError):
            continue
    return False


@cached(3)
def batt():
    try:
        v = int(Path("/sys/class/power_supply/BAT0/capacity").read_text())
    except (OSError, ValueError):
        return '<span foreground="grey">󰈸  --%</span>'
    chg = is_charging()
    icon = (
        " "
        if v >= 80
        else " "
        if v >= 60
        else " " 
        if v >= 40
        else " "
        if v >= 20
        else " "
    )
    color = (
        "aqua"
        if chg
        else "lime"
        if v >= 80
        else "palegreen"
        if v >= 60
        else "orange"
        if v >= 40
        else "coral"
        if v >= 20
        else "red"
    )
    return fmt(f" {icon}" if chg else icon, v, color)
