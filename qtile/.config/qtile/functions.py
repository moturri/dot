import re
import subprocess


def bright():
    try:
        # Get current and max brightness using brightnessctl
        current = subprocess.run(
            ["brightnessctl", "g"], capture_output=True, text=True, check=True
        )
        maximum = subprocess.run(
            ["brightnessctl", "m"], capture_output=True, text=True, check=True
        )

        current_val = int(current.stdout.strip())
        max_val = int(maximum.stdout.strip())

        percent = int((current_val / max_val) * 100)

        # Determine icon and color based on brightness percentage
        if percent > 80:
            icon, color = "󰃠  ", "gold"
        elif percent > 60:
            icon, color = "󰃝  ", "darkorange"
        elif percent > 40:
            icon, color = "󰃟  ", "orchid"
        elif percent > 20:
            icon, color = "󰃞  ", "pink"
        else:
            icon, color = "󰃜 ", "dimgrey"

        return f'<span foreground="{color}">{icon} {percent}%</span>'

    except (subprocess.CalledProcessError, ValueError):
        return '<span foreground="grey">󰳲 --%</span>'


def batt():
    try:
        result = subprocess.run(["acpi"], capture_output=True, text=True, check=True)
        output = result.stdout.strip()

        # Example ACPI output: "Battery 0: Discharging, 55%, 02:10:00 remaining"
        parts = output.split(", ")
        status = parts[0].split(": ")[1].strip()
        percentage = int(parts[1].replace("%", "").strip())

        # Choose icon and color based on percentage
        if percentage > 80:
            icon, color = "  ", "lime"
        elif percentage > 60:
            icon, color = "  ", "palegreen"
        elif percentage > 40:
            icon, color = "  ", "orange"
        elif percentage > 20:
            icon, color = "  ", "coral"
        else:
            icon, color = "  ", "red"

        # If charging, override icon and color
        if "Charging" in status:
            icon = " " + icon
            color = "aqua"

        return f'<span foreground="{color}">{icon} {percentage}%</span>'

    except (subprocess.CalledProcessError, IndexError, ValueError):
        return '<span foreground="grey">󰈸 --%</span>'


def vol():
    try:
        result = subprocess.run(
            ["amixer", "get", "Master"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
        lines = output.splitlines()
        playback_line = next(
            (line for line in reversed(lines) if "Playback" in line), None
        )

        if not playback_line:
            return '<span foreground="dimgrey">󰕿 0%</span>'

        volume_str = playback_line.split("[")[1].split("%")[0]
        volume = int(volume_str)
        is_muted = "[off]" in playback_line

        # Determine icon and color
        if is_muted or volume == 0:
            icon, color = "  ", "dimgrey"
        elif volume > 100:
            icon, color = "󰕾 ", "peru"
        elif volume > 80:
            icon, color = "󰕾 ", "tomato"
        elif volume > 60:
            icon, color = "󰕾 ", "tan"
        elif volume > 40:
            icon, color = "󰕾 ", "orchid"
        elif volume > 20:
            icon, color = "󰖀 ", "dodgerblue"
        else:
            icon, color = "󰕿 ", "dimgrey"

        return f'<span foreground="{color}">{icon} {volume}%</span>'

    except subprocess.CalledProcessError:
        return '<span foreground="dimgrey">󰕿 0%</span>'


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
            return '<span foreground="grey">  0%</span>'

        volume_str, state = matches[-1]
        volume = int(volume_str)
        is_muted = state == "off"

        if is_muted or volume == 0:
            icon, color = "  ", "dimgrey"
        elif volume > 80:
            icon, color = " ", "tomato"
        elif volume > 60:
            icon, color = " ", "tan"
        elif volume > 40:
            icon, color = " ", "orchid"
        elif volume > 20:
            icon, color = " ", "dodgerblue"
        else:
            icon, color = " ", "dimgrey"

        return f'<span foreground="{color}">{icon} {volume}%</span>'

    except subprocess.CalledProcessError:
        return '<span foreground="grey"> Error</span>'
