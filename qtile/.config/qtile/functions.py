import re
import subprocess


def bright():
    try:
        result = subprocess.run(
            ["brillo", "-G"], capture_output=True, text=True, check=True
        )
        percent = int(float(result.stdout.strip()))

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
    except Exception:
        return '<span foreground="grey">󰳲 --%</span>'


def batt():
    try:
        base = "/sys/class/power_supply/BAT0/"

        with open(base + "capacity") as f:
            battery_percentage = int(f.read().strip())
        with open(base + "status") as f:
            battery_status = f.read().strip()

        if battery_percentage > 80:
            icon, color = "  ", "lime"
        elif battery_percentage > 60:
            icon, color = "  ", "palegreen"
        elif battery_percentage > 40:
            icon, color = "  ", "orange"
        elif battery_percentage > 20:
            icon, color = "  ", "coral"
        else:
            icon, color = "  ", "red"

        if battery_status == "Charging":
            icon = " " + icon
            color = "aqua"

        return f'<span foreground="{color}">{icon} {battery_percentage}%</span>'
    except Exception:
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
        playback_line = next(
            (line for line in reversed(output.splitlines()) if "Playback" in line), None
        )

        if not playback_line:
            return '<span foreground="dimgrey">󰕿 0%</span>'

        volume_str = playback_line.split("[")[1].split("%")[0]
        volume = int(volume_str)
        is_muted = "[off]" in playback_line

        if is_muted or volume == 0:
            icon, color = "  ", "dimgrey"
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
        else:
            if volume > 80:
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


def load_avg():
    try:
        with open("/proc/loadavg") as f:
            loads = list(map(float, f.read().split()[:3]))

        def get_color(load):
            if load < 2.0:
                return "lime"
            elif load < 4.0:
                return "palegreen"
            elif load < 6.0:
                return "cyan"
            elif load < 8.0:
                return "orchid"
            elif load < 10.0:
                return "orange"
            elif load < 12.0:
                return "orangered"
            else:
                return "red"

        colored_loads = [
            f'<span foreground="{get_color(load)}">{load:.2f}</span>' for load in loads
        ]

        return f'<span foreground="lightsteelblue">  </span> {" ".join(colored_loads)}'
    except Exception:
        return '<span foreground="grey">  --</span>'
