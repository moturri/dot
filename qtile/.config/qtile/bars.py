from functions import (
    batt,
    bright,
    mic,
    mic_down,
    mic_mute,
    mic_up,
    vol,
    volume_down,
    volume_mute,
    volume_up,
)
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration


rangi = ["#000000", "#FFFFFF"]
wdecor = {
    "background": rangi[0],
    "foreground": rangi[1],
    "decorations": [
        RectDecoration(use_widget_background=True, radius=12, filled=True, group=True),
    ],
    "padding": 6,
}


yao = [
    widget.Clock(
        format="   %e %b    %H:%M  ",
        **wdecor,
    ),
    widget.Spacer(length=10),
    widget.GenPollText(
        update_interval=0.2,
        func=vol,
        mouse_callbacks={
            "Button2": lazy.function(volume_mute),
            "Button4": lazy.function(volume_up),
            "Button5": lazy.function(volume_down),
        },
        **wdecor,
    ),
    widget.GenPollText(
        update_interval=0.2,
        func=mic,
        mouse_callbacks={
            "Button2": lazy.function(mic_mute),
            "Button4": lazy.function(mic_up),
            "Button5": lazy.function(mic_down),
        },
        **wdecor,
    ),
    widget.Spacer(length=10),
]


ming = [
    widget.Mpris2(
        name="mpris",
        format=" 󰝚 ",
        no_metadata_text=" 󰝛 ",
        paused_text=" 󰝛 ",
        popup_hide_timeout=8,
        width=60,
        popup_controls=True,
        mouse_callbacks={"Button3": lazy.widget["mpris"].toggle_player()},
        **wdecor,
    ),
    widget.Spacer(length=5),
    widget.GenPollText(func=batt, update_interval=2, **wdecor),
]


def main():
    return (
        yao
        + [
            widget.GroupBox(
                hide_unused=True,
                highlight_method="text",
                urgent_alert_method="text",
                fontsize=18,
                disable_drag=True,
                **wdecor,
            ),
            widget.TaskList(
                icon_size=24,
                # parse_text=lambda _: "",
                max_title_width=200,
                highlight_method="text",
                urgent_alert_method="text",
                txt_floating="󱂬 ",
                txt_maximized="󰏋 ",
                txt_minimized="󰖰 ",
            ),
            widget.GenPollText(
                func=bright,
                update_interval=0.2,
                mouse_callbacks={
                    "Button4": lazy.spawn("brillo -A 5"),
                    "Button5": lazy.spawn("brillo -U 5"),
                },
                **wdecor,
            ),
            widget.Systray(padding=10),
            widget.Spacer(length=10),
        ]
        + ming
    )


def misc():
    return (
        yao
        + [
            widget.GroupBox(
                hide_unused=True,
                highlight_method="text",
                urgent_alert_method="text",
                fontsize=18,
                disable_drag=True,
                **wdecor,
            ),
            widget.TaskList(
                icon_size=24,
                # parse_text=lambda _: "",
                max_title_width=200,
                highlight_method="text",
                urgent_alert_method="text",
                txt_floating="󱂬 ",
                txt_maximized="󰏋 ",
                txt_minimized="󰖰 ",
            ),
        ]
        + ming
    )
