import subprocess
import re


def run_command(cmd, timeout=0.2):
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, check=False
        )
        return result.stdout
    except Exception:
        return ""


def vol():
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

    return f'<span foreground="{color}">{icon} {volume:>3}%</span>'


def mic():
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

    return f'<span foreground="{color}">{icon} {volume:>3}%</span>'


def bright():
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

        return f'<span foreground="{color}">{icon}  {percent:>3}%</span>'
    except Exception:
        return '<span foreground="grey">󰳲  --%</span>'


def batt():
    try:
        with open("/sys/class/power_supply/BAT0/capacity") as f:
            capacity = int(f.read().strip())
        with open("/sys/class/power_supply/AC/online") as f:
            charging = f.read().strip() == "1"

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

        return f'<span foreground="{color}">{icon}  {capacity:>3}%</span>'
    except Exception:
        return '<span foreground="grey">󰈸  --%</span>'
