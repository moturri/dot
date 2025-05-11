import subprocess
import re
from utils import cached, fmt


def get_current_mic_volume():
    try:
        output = subprocess.check_output(
            ["pactl", "get-source-volume", "@DEFAULT_SOURCE@"]
        ).decode()
        match = re.search(r"(\d+)%", output)
        return int(match.group(1)) if match else 0
    except Exception:
        return 0


@cached(10)
def mic():
    try:
        output = subprocess.check_output(
            ["pactl", "get-source-volume", "@DEFAULT_SOURCE@"]
        ).decode()
        mute_status = subprocess.check_output(
            ["pactl", "get-source-mute", "@DEFAULT_SOURCE@"]
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
            ["pactl", "set-source-volume", "@DEFAULT_SOURCE@", f"+{increment}%"]
        )
    mic(force=True)


def mic_down(qtile=None):
    subprocess.run(["pactl", "set-source-volume", "@DEFAULT_SOURCE@", "-2%"])
    mic(force=True)


def mic_mute(qtile=None):
    subprocess.run(["pactl", "set-source-mute", "@DEFAULT_SOURCE@", "toggle"])
    mic(force=True)
