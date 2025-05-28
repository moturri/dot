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
    "padding": 6,
}

# Common widget decoration dictionary
wdecor = {
    "background": theme["bg"],
    "foreground": theme["fg"],
    "decorations": [
        RectDecoration(use_widget_background=True, radius=12, filled=True, group=True)
    ],
    "padding": theme["padding"],
}


def spacer(length=10):
    return widget.Spacer(length=length)


# Clock widget setup
timeWidget = [
    widget.Clock(format="   %e %b    %H:%M  ", **wdecor),
    spacer(),
]


def system_widgets():
    return [
        widget.Mpris2(
            name="mpris",
            format=" 󰓃 ",  # Play icon
            no_metadata_text=" 󰓄 ",  # Stop icon
            paused_text=" 󰓄 ",
            popup_hide_timeout=8,
            width=60,
            mouse_callbacks={"Button3": lazy.widget["mpris"].toggle_player()},
            **wdecor,
        ),
        AudioWidget(
            name="audio",
            mouse_callbacks={
                "Button3": lazy.widget["audio"].toggle_mute(),
                "Button4": lazy.widget["audio"].volume_up(),
                "Button5": lazy.widget["audio"].volume_down(),
            },
            **wdecor,
        ),
        MicWidget(
            name="mic",
            mouse_callbacks={
                "Button3": lazy.widget["mic"].toggle_mute(),
                "Button4": lazy.widget["mic"].volume_up(),
                "Button5": lazy.widget["mic"].volume_down(),
            },
            **wdecor,
        ),
        spacer(),
        BrilloWidget(
            name="brightness",
            mouse_callbacks={
                "Button4": lazy.widget["brightness"].increase(),
                "Button5": lazy.widget["brightness"].decrease(),
            },
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
    return timeWidget + group_widgets() + system_tray_widget() + system_widgets()


def misc():
    return timeWidget + group_widgets() + system_widgets()
