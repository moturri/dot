from functions import batt, bright, load_avg, mic, vol
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration

black = [
    "#000000",
    "#FFFFFF",
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
        widget.Spacer(length=10),
        widget.GenPollText(
            update_interval=5,
            func=load_avg,
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
        widget.Spacer(length=10),
        widget.Mpris2(
            name="mpris",
            format=" 󰝚 ",
            no_metadata_text=" 󰝛 ",
            paused_text=" 󰝛 ",
            popup_hide_timeout=8,
            width=30,
            popup_controls=True,
            mouse_callbacks={
                "Button3": lazy.widget["mpris"].toggle_player(),
            },
            **wdecor,
        ),
        widget.TaskList(
            icon_size=24,
            parse_text=lambda _: "",
            highlight_method="text",
            txt_floating="󱂬 ",
            txt_maximized="󰏋 ",
            txt_minimized="󰖰 ",
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
        widget.Spacer(length=10),
        widget.Systray(
            padding=10,
        ),
        widget.Spacer(length=10),
        widget.GenPollText(
            func=bright,
            update_interval=0.1,
            mouse_callbacks={
                "Button4": lazy.spawn("brillo -A 5"),
                "Button5": lazy.spawn("brillo -U 5"),
            },
            **wdecor,
        ),
        widget.Spacer(length=10),
        widget.GenPollText(
            func=batt,
            update_interval=1,
            **wdecor,
        ),
    ]


def misc():
    return [
        widget.Clock(
            format="%e %b   %H:%M ",
            **wdecor,
        ),
        widget.Spacer(length=10),
        widget.GenPollText(
            update_interval=5,
            func=load_avg,
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
        widget.Spacer(length=10),
        widget.Mpris2(
            name="mpris",
            format=" 󰝚 ",
            no_metadata_text=" 󰝛 ",
            paused_text=" 󰝛 ",
            popup_hide_timeout=10,
            width=30,
            popup_controls=True,
            mouse_callbacks={
                "Button3": lazy.widget["mpris"].toggle_player(),
            },
            **wdecor,
        ),
        widget.TaskList(
            icon_size=24,
            parse_text=lambda _: "",
            highlight_method="text",
            txt_floating="󱂬 ",
            txt_maximized="󰏋 ",
            txt_minimized="󰖰 ",
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
        widget.Spacer(length=10),
        widget.GenPollText(
            func=batt,
            update_interval=1,
            **wdecor,
        ),
    ]
