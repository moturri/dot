import subprocess

from audio import AudioWidget, MicWidget
from battery import BatteryWidget
from brillo import BrilloWidget
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration

# Theme colors
theme = {
    "accent": "#6f3aea",
    "alert": "#ff5555",
    "fg": "#FFFFFF",
    "bg": "#000000",
}

# Common widget decoration
wdecor = {
    "background": theme["bg"],
    "foreground": theme["fg"],
    "decorations": [
        RectDecoration(use_widget_background=True, radius=12, filled=True, group=True)
    ],
    "padding": 6,
}


def spacer(length=10):
    return widget.Spacer(length=length)


# Dunst notification handlers
def show_dunst_history(qtile):
    subprocess.Popen(["dunstctl", "history-pop"])


def clear_dunst_history(qtile):
    subprocess.Popen(["dunstctl", "history-clear"])


wakati = [
    widget.Clock(format="   %e %b    %H:%M  ", **wdecor),
    spacer(),
]


def system_widgets():
    return [
        BrilloWidget(
            mouse_callbacks={
                "Button4": lazy.widget["brightness"].increase(),
                "Button5": lazy.widget["brightness"].decrease(),
            },
            name="brightness",
            **wdecor,
        ),
        spacer(),
        widget.Mpris2(
            name="mpris",
            format=" 󰝚",
            no_metadata_text=" 󰝛",
            paused_text=" 󰝛",
            popup_hide_timeout=8,
            width=60,
            mouse_callbacks={"Button3": lazy.widget["mpris"].toggle_player()},
            **wdecor,
        ),
        widget.TextBox(
            text=" 󰂚 ",
            mouse_callbacks={
                "Button1": lazy.function(show_dunst_history),
                "Button3": lazy.function(clear_dunst_history),
            },
            **wdecor,
        ),
        spacer(),
        AudioWidget(
            mouse_callbacks={
                "Button3": lazy.widget["audio"].toggle_mute(),
                "Button4": lazy.widget["audio"].volume_up(),
                "Button5": lazy.widget["audio"].volume_down(),
            },
            name="audio",
            **wdecor,
        ),
        MicWidget(
            mouse_callbacks={
                "Button3": lazy.widget["mic"].toggle_mute(),
                "Button4": lazy.widget["mic"].volume_up(),
                "Button5": lazy.widget["mic"].volume_down(),
            },
            name="mic",
            **wdecor,
        ),
        spacer(),
        BatteryWidget(**wdecor),
    ]


def group_widgets():
    return [
        widget.GroupBox(
            hide_unused=True,
            highlight_method="text",
            urgent_alert_method="text",
            fontsize=18,
            disable_drag=True,
            this_current_screen_border=theme["accent"],
            urgent_border=theme["alert"],
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
            border=theme["accent"],
            urgent_border=theme["alert"],
            margin=3,
            padding=5,
        ),
    ]


def system_tray_widget():
    return [
        widget.Systray(padding=10),
        spacer(),
    ]


def main():
    return wakati + group_widgets() + system_tray_widget() + system_widgets()


def misc():
    return wakati + group_widgets() + system_widgets()
