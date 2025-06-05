from typing import Any, Dict, List

from brillo import BrilloWidget
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration
from upower import UpowerWidget
from wpctl import AudioWidget, MicWidget

# Theme
theme: Dict[str, Any] = {
    "accent": "#6f3aea",
    "alert": "#ff5555",
    "fg": "#FFFFFF",
    "bg": "#110000",
    "padding": 6,
}

# Icons
ICON_NOTIFICATION = "󰂚"
ICON_PLAYER = "󰀰 "
ICON_NO_METADATA = "󱆵 "
ICON_PAUSED = "󱆵 "

# Decoration template
wdecor: Dict[str, Any] = {
    "background": theme["bg"],
    "foreground": theme["fg"],
    "decorations": [
        RectDecoration(use_widget_background=True, radius=12, filled=True, group=True)  # type: ignore
    ],
    "padding": theme["padding"],
}


# Reusable Spacer
def spacer(length: int = 10) -> Any:
    return widget.Spacer(length=length)


# Clock
timeWidget: List[Any] = [
    widget.Clock(format="   %e %b    %H:%M  ", **wdecor),
    spacer(),
]


# Group + Task
def groupWidgets() -> List[Any]:
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
            padding=5,
        ),
    ]


# Tray
def systemTrayWidget() -> List[Any]:
    return [widget.Systray(padding=10), spacer()]


# Audio/Brightness/Battery group
def systemWidgets(show_brightness: bool = True, show_battery: bool = True) -> List[Any]:
    widgets: List[Any] = [
        widget.TextBox(
            text=f" {ICON_NOTIFICATION} ",
            mouse_callbacks={
                "Button1": lazy.spawn("dunstctl history-pop"),
                "Button3": lazy.spawn("dunstctl history-clear"),
            },
            **wdecor,
        ),
        widget.Mpris2(
            name="mpris",
            format=ICON_PLAYER,
            no_metadata_text=ICON_NO_METADATA,
            paused_text=ICON_PAUSED,
            popup_hide_timeout=8,
            width=60,
            mouse_callbacks={"Button3": lazy.widget["mpris"].toggle_player()},
            **wdecor,
        ),
        spacer(),
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
    ]

    if show_brightness:
        widgets += [
            BrilloWidget(
                name="brillo",
                mouse_callbacks={
                    "Button4": lazy.widget["brillo"].increase(),
                    "Button5": lazy.widget["brillo"].decrease(),
                },
                **wdecor,
            ),
            spacer(),
        ]

    if show_battery:
        widgets.append(UpowerWidget(**wdecor))

    return widgets


# Entrypoints
def main() -> List[Any]:
    return timeWidget + groupWidgets() + systemTrayWidget() + systemWidgets()


def misc() -> List[Any]:
    return timeWidget + groupWidgets() + systemWidgets()
