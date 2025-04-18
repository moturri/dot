from functions import *
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration

widget_defaults = dict(
    font="Inter Variable Bold",
    fontsize=14,
)


black = [
    "#0d0d0d",
    "#d3d3d3",
    # "#383838",
    # "#545454",
]

rangi = black

wdecor = {
    "background": rangi[0],
    "foreground": rangi[1],
    "decorations": [
        RectDecoration(use_widget_background=True, radius=12, filled=True, group=True),
    ],
    "padding": 6,
}


def main():
    return [
        widget.Clock(
            format="%e %b   %H:%M ",
            **wdecor,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.GenPollText(
            update_interval=0.1,
            func=vol,
            mouse_callbacks={
                "Button4": lazy.spawn("amixer set Master 5%+"),
                "Button5": lazy.spawn("amixer set Master 5%-"),
                "Button2": lazy.spawn("amixer set Master toggle"),
            },
            **wdecor,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.GenPollText(
            update_interval=0.1,
            func=mic,
            mouse_callbacks={
                "Button4": lazy.spawn("amixer set Capture 5%+"),
                "Button5": lazy.spawn("amixer set Capture 5%-"),
                "Button2": lazy.spawn("amixer set Capture toggle"),
            },
            **wdecor,
        ),
        widget.Spacer(),
        widget.GroupBox(
            hide_unused=True,
            highlight_method="text",
            fontsize=18,
            disable_drag=True,
            **wdecor,
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
        widget.Net(
            interface="wlp1s0",
            format="{down:.0f}{down_suffix} ↓↑ {up:.0f}{up_suffix}",
            update_interval=2,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.GenPollText(
            func=batt,
            update_interval=1,
            **wdecor,
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
            **wdecor,
        ),
    ]


def misc():
    return [
        widget.Clock(
            format=" %H:%M ",
            **wdecor,
        ),
        widget.Spacer(),
        widget.GroupBox(
            hide_unused=True,
            highlight_method="text",
            fontsize=18,
            disable_drag=True,
            **wdecor,
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
