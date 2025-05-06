from functions import (
    batt,
    bright,
    mic,
    mic_down,
    mic_mute,
    mic_up,
    vol,
    vol_down,
    vol_mute,
    vol_up,
)
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration
import subprocess

rangi = ["#000000", "#FFFFFF"]
accent_color = "#6f3aea"
alert_color = "#ff5555"

wdecor = {
    "background": rangi[0],
    "foreground": rangi[1],
    "decorations": [
        RectDecoration(use_widget_background=True, radius=12, filled=True, group=True),
    ],
    "padding": 6,
}


def show_calendar():
    calendar_cmd = "kitty --class floating_calendar -e calcurse"
    subprocess.Popen(calendar_cmd, shell=True)


def show_dunst_history():
    subprocess.Popen(["dunstctl", "history-pop"])


yao = [
    widget.Clock(
        format="   %e %b    %H:%M  ",
        mouse_callbacks={"Button2": lazy.function(lambda qtile: show_calendar())},
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
    ),
    widget.Spacer(length=5),
    widget.TextBox(
        text=" 󰂚 ",
        mouse_callbacks={"Button2": lazy.function(lambda qtile: show_dunst_history())},
        **wdecor,
    ),
    widget.GenPollText(
        update_interval=0.2,
        func=vol,
        mouse_callbacks={
            "Button2": lazy.function(vol_mute),
            "Button4": lazy.function(vol_up),
            "Button5": lazy.function(vol_down),
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
                active=rangi[1],
                inactive=rangi[1],
                this_current_screen_border=accent_color,
                urgent_border=alert_color,
                **wdecor,
            ),
            widget.TaskList(
                icon_size=24,
                max_title_width=200,
                highlight_method="text",
                urgent_alert_method="text",
                txt_floating="󱂬 ",
                txt_maximized="󰏋 ",
                txt_minimized="󰖰 ",
                border=accent_color,
                unfocused_border=rangi[0],
                foreground=rangi[1],
                urgent_border=alert_color,
                margin=3,
                padding=5,
                rounded=True,
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
            widget.Spacer(length=5),
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
                active=rangi[1],
                inactive=rangi[1],
                this_current_screen_border=accent_color,
                urgent_border=alert_color,
                **wdecor,
            ),
            widget.TaskList(
                icon_size=24,
                max_title_width=200,
                highlight_method="text",
                urgent_alert_method="text",
                txt_floating="󱂬 ",
                txt_maximized="󰏋 ",
                txt_minimized="󰖰 ",
                border=accent_color,
                unfocused_border=rangi[0],
                foreground=rangi[1],
                urgent_border=alert_color,
                margin=3,
                padding=5,
                rounded=True,
            ),
        ]
        + ming
    )
