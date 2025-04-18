import os
import re
import subprocess


def bright():
    result = subprocess.run(["brightnessctl", "g"], capture_output=True, text=True)
    max_brightness = subprocess.run(
        ["brightnessctl", "m"], capture_output=True, text=True
    )

    if result.returncode != 0 or max_brightness.returncode != 0:
        return "󰳲 "

    current_brightness = int(result.stdout.strip())
    max_brightness = int(max_brightness.stdout.strip())
    brightness_percentage = int((current_brightness / max_brightness) * 100)

    if brightness_percentage > 80:
        icon = "󰃠 "
        color = "gold"
    elif brightness_percentage > 60:
        icon = "󰃟 "
        color = "darkorange"
    elif brightness_percentage > 40:
        icon = "󰅟 "
        color = "orchid"
    elif brightness_percentage > 20:
        icon = "󰃝 "
        color = "dodgerblue"
    else:
        icon = "󰃜 "
        color = "dimgrey"

    return f'<span foreground="{color}">{icon}  {brightness_percentage}%</span>'


def batt():
    result = subprocess.run(["acpi"], capture_output=True, text=True)
    if result.returncode != 0:
        return "󰈸 %"

    output = result.stdout.strip().split(", ")
    battery_percentage = int(output[1].replace("%", "").strip())
    battery_state = output[0].split()[-1]
    if battery_percentage > 80:
        icon = "  "
        color = "lime"
    elif battery_percentage > 60:
        icon = "  "
        color = "palegreen"
    elif battery_percentage > 40:
        icon = "  "
        color = "orange"
    elif battery_percentage > 20:
        icon = "  "
        color = "coral"
    else:
        icon = "  "
        color = "red"

    if battery_state == "Charging":
        icon = " " + icon
        color = "aqua"

    return f'<span foreground="{color}">{icon} {battery_percentage}%</span>'


def vol():
    try:
        result = subprocess.run(
            ["amixer", "get", "Master"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()

        volume_line = [line for line in output.splitlines() if "Playback" in line][-1]
        volume_percentage = int(volume_line.split("[")[1].split("%")[0])
        is_muted = "[off]" in volume_line

        if is_muted or volume_percentage == 0:
            icon = "  "
            color = "brown"
        elif volume_percentage > 100:
            icon = "󰕾 "
            color = "peru"
        elif volume_percentage > 80:
            icon = "󰕾 "
            color = "tomato"
        elif volume_percentage > 60:
            icon = "󰕾 "
            color = "tan"
        elif volume_percentage > 40:
            icon = "󰕾 "
            color = "dodgerblue"
        elif volume_percentage > 20:
            icon = "󰖀 "
            color = "orchid"
        else:
            icon = "󰕿 "
            color = "dimgrey"

        return f'<span foreground="{color}">{icon} {volume_percentage}%</span>'

    except subprocess.CalledProcessError:
        return "󰕿 %"


def mic():
    try:
        result = subprocess.run(
            ["amixer", "get", "Capture"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout

        matches = re.findall(r"\[(\d+)%\] \[(on|off)\]", output)
        if not matches:
            return '<span foreground="grey"> 0%</span>'

        volume, state = matches[-1]
        volume = int(volume)
        is_muted = state == "off"

        if is_muted or volume == 0:
            icon = "  "
            color = "dimgrey"
        elif volume > 80:
            icon = " "
            color = "tomato"
        elif volume > 60:
            icon = " "
            color = "tan"
        elif volume > 40:
            icon = " "
            color = "dodgerblue"
        elif volume > 20:
            icon = " "
            color = "orchid"
        else:
            icon = " "
            color = "dimgrey"

        return f'<span foreground="{color}">{icon} {volume}%</span>'

    except subprocess.CalledProcessError:
        return '<span foreground="grey"> Error</span>'
