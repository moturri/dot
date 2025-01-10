import subprocess

from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration

black = [
    "#0d0d0d",
    "#d3d3d3",
    # "#383838",
    # "#545454",
]

rangi = black

decor = {
    "background": rangi[0],
    "foreground": rangi[1],
    "decorations": [
        RectDecoration(use_widget_background=True, radius=12, filled=True, group=True),
    ],
    "padding": 6,
}


def bright():
    result = subprocess.run(["brightnessctl", "g"], capture_output=True, text=True)
    max_brightness = subprocess.run(
        ["brightnessctl", "m"], capture_output=True, text=True
    )

    if result.returncode != 0 or max_brightness.returncode != 0:
        return "👾 %"

    current_brightness = int(result.stdout.strip())
    max_brightness = int(max_brightness.stdout.strip())
    brightness_percentage = int((current_brightness / max_brightness) * 100)

    if brightness_percentage > 80:
        icon = "🌞 "
        color = "gold"
    elif brightness_percentage > 60:
        icon = "🌤️ "
        color = "darkorange"
    elif brightness_percentage > 40:
        icon = "🌥️ "
        color = "dodgerblue"
    elif brightness_percentage > 20:
        icon = "🌙 "
        color = "peru"
    else:
        icon = "🌒 "
        color = "dimgrey"

    return f'<span foreground="{color}">{icon} {brightness_percentage}%</span>'


def batt():
    result = subprocess.run(["acpi"], capture_output=True, text=True)
    if result.returncode != 0:
        return "💀 %"

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
        color = "tan"
    elif battery_percentage > 20:
        icon = "  "
        color = "coral"
    else:
        icon = "  "
        color = "red"

    if battery_state == "Charging":
        icon = "⚡ " + icon
        color = "aqua"

    return f'<span foreground="{color}">{icon}  {battery_percentage}%</span>'


def vol():
    try:
        result = subprocess.run(
            ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
            capture_output=True,
            text=True,
            check=True,
        )
        volume_info = result.stdout.strip().split()
        volume_percentage = int(volume_info[4][:-1])

        if volume_percentage > 150:
            volume_percentage = 150
        if volume_percentage == 0:
            icon = "  "
            color = "brown"
        elif volume_percentage > 125:
            icon = "󰕾  "
            color = "crimson"
        elif volume_percentage > 100:
            icon = "󰕾  "
            color = "peru"
        elif volume_percentage > 80:
            icon = "󰕾  "
            color = "tomato"
        elif volume_percentage > 60:
            icon = "󰕾  "
            color = "tan"
        elif volume_percentage > 40:
            icon = "󰕾  "
            color = "skyblue"
        elif volume_percentage > 20:
            icon = "󰖀  "
            color = "orchid"
        else:
            icon = "󰕿  "
            color = "dimgrey"

        return f'<span foreground="{color}">{icon} {volume_percentage}%</span>'

    except subprocess.CalledProcessError:
        return "󰕿 %"


def main():
    return [
        widget.Clock(
            format="%e %b   %H:%M ",
            **decor,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.GenPollText(
            update_interval=0.1,
            func=vol,
            mouse_callbacks={
                "Button4": lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ +5% "),
                "Button5": lazy.spawn("pactl set-sink-volume @DEFAULT_SINK@ -5%"),
            },
            **decor,
        ),
        widget.Spacer(),
        widget.GroupBox(
            hide_unused=True,
            highlight_method="text",
            fontsize=18,
            disable_drag=True,
            **decor,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.TaskList(
            icon_size=24,
            parse_text=lambda _: "",
            highlight_method="text",
            txt_floating="󱂬 ",
            txt_maximized="󰏋 ",
            txt_minimized="󰖰 ",
        ),
        widget.Prompt(),
        widget.Spacer(
            length=10,
        ),
        widget.GenPollText(
            func=batt,
            update_interval=1,
            **decor,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.Systray(
            padding=10,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.GenPollText(
            func=bright,
            update_interval=0.1,
            mouse_callbacks={
                "Button4": lazy.spawn("brightnessctl set +5%"),
                "Button5": lazy.spawn("brightnessctl set 5%-"),
            },
            **decor,
        ),
    ]


def misc():
    return [
        widget.Clock(
            format=" %H:%M ",
            **decor,
        ),
        widget.Spacer(),
        widget.GroupBox(
            hide_unused=True,
            highlight_method="text",
            fontsize=18,
            disable_drag=True,
            **decor,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.TaskList(
            icon_size=24,
            parse_text=lambda _: "",
            highlight_method="text",
            txt_floating="󱂬 ",
            txt_maximized="󰏋 ",
            txt_minimized="󰖰 ",
        ),
    ]
