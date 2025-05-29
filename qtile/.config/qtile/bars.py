from typing import Any, Dict, List, Union, cast

from brillo import BrilloWidget
from libqtile.lazy import lazy
from libqtile.widget.base import _Widget as Widget
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration
from upower import UpowerWidget
from wpctl import AudioWidget, MicWidget

# Theme configuration
theme: Dict[str, Union[str, int]] = {
    "accent": "#6f3aea",
    "alert": "#ff5555",
    "fg": "#FFFFFF",
    "bg": "#110000",
    "padding": 6,
}

# Widget decoration
wdecor: Dict[str, Any] = {
    "background": theme["bg"],
    "foreground": theme["fg"],
    "decorations": [
        RectDecoration(use_widget_background=True, radius=12, filled=True, group=True)  # type: ignore
    ],
    "padding": theme["padding"],
}


# Spacer utility
def spacer(length: int = 10) -> Widget:
    return cast(Widget, widget.Spacer(length=length))


# Time widget group
timeWidget: List[Widget] = [
    cast(Widget, widget.Clock(format="   %e %b    %H:%M  ", **wdecor)),
    spacer(),
]


# Group/Task widgets
def groupWidgets() -> List[Widget]:
    return [
        cast(
            Widget,
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
        ),
        spacer(10),
        cast(
            Widget,
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
        ),
    ]


# System tray widget
def systemTrayWidget() -> List[Widget]:
    return [
        cast(Widget, widget.Systray(padding=10)),
        spacer(),
    ]


# System-related widgets
def systemWidgets() -> List[Widget]:
    return [
        cast(
            Widget,
            widget.TextBox(
                text=" 󰂚 ",
                mouse_callbacks={
                    "Button1": lazy.spawn("dunstctl history-pop"),
                    "Button3": lazy.spawn("dunstctl history-clear"),
                },
                tooltip="Notifications",
                **wdecor,
            ),
        ),
        cast(
            Widget,
            widget.Mpris2(
                name="mpris",
                format="󰓃 ",
                no_metadata_text="󰓄 ",
                paused_text="󰓄 ",
                popup_hide_timeout=8,
                width=60,
                mouse_callbacks={"Button3": lazy.widget["mpris"].toggle_player()},
                tooltip="Media Player",
                **wdecor,
            ),
        ),
        spacer(),
        cast(
            Widget,
            AudioWidget(
                name="audio",
                mouse_callbacks={
                    "Button3": lazy.widget["audio"].toggle_mute(),
                    "Button4": lazy.widget["audio"].volume_up(),
                    "Button5": lazy.widget["audio"].volume_down(),
                },
                tooltip="Audio Volume",
                **wdecor,
            ),
        ),
        cast(
            Widget,
            MicWidget(
                name="mic",
                mouse_callbacks={
                    "Button3": lazy.widget["mic"].toggle_mute(),
                    "Button4": lazy.widget["mic"].volume_up(),
                    "Button5": lazy.widget["mic"].volume_down(),
                },
                tooltip="Microphone Volume",
                **wdecor,
            ),
        ),
        spacer(),
        cast(
            Widget,
            BrilloWidget(
                name="brightness",
                mouse_callbacks={
                    "Button4": lazy.widget["brightness"].increase(),
                    "Button5": lazy.widget["brightness"].decrease(),
                },
                tooltip="Screen Brightness",
                **wdecor,
            ),
        ),
        spacer(),
        cast(
            Widget,
            UpowerWidget(
                tooltip="Battery Status",
                **wdecor,
            ),
        ),
    ]


# Full widget bar for primary screen
def main() -> List[Widget]:
    return timeWidget + groupWidgets() + systemTrayWidget() + systemWidgets()


# Secondary screen widgets (no systray)
def misc() -> List[Widget]:
    return timeWidget + groupWidgets() + systemWidgets()
