import subprocess
import re
from pathlib import Path

VOL_PATTERN = re.compile(r"\[([0-9]+)%\]")
MUTE_PATTERN = re.compile(r"\[(on|off)\]")


def run_command(cmd, timeout=0.2):
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=timeout,
            check=False,
        )
        return result.stdout
    except Exception:
        return ""


def vol():
    out = run_command(["amixer", "-M", "get", "Master"])
    vol_match = VOL_PATTERN.search(out)
    mute_match = MUTE_PATTERN.search(out)
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
    out = run_command(["amixer", "-M", "get", "Capture"])

    vol_match = VOL_PATTERN.search(out)
    mute_match = MUTE_PATTERN.search(out)
    volume = int(vol_match.group(1)) if vol_match else 0
    muted = mute_match.group(1) == "off" if mute_match else True

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
        bat_path = Path("/sys/class/power_supply/BAT0")
        ac_path = Path("/sys/class/power_supply/AC")

        if not bat_path.exists():
            return '<span foreground="grey">󰈸  --%</span>'
        try:
            with open(bat_path / "capacity", "r") as f:
                capacity = int(f.read().strip())

            charging = False
            if (ac_path / "online").exists():
                with open(ac_path / "online", "r") as f:
                    charging = f.read().strip() == "1"
        except (IOError, ValueError):
            return '<span foreground="grey">󰈸  --%</span>'

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

        return f'<span foreground="{color}">{icon}   {capacity:>3}%</span>'
    except Exception:
        return '<span foreground="grey">󰈸  --%</span>'
