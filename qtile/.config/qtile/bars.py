from typing import Any, Dict, List, Union, cast

from audio import AudioWidget, MicWidget
from brillo import BrilloWidget
from libqtile.lazy import lazy
from libqtile.widget.base import _Widget as Widget
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration
from upower import UpowerWidget

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


def spacer(length: int = 10) -> Widget:
    return cast(Widget, widget.Spacer(length=length))


timeWidget: List[Widget] = [
    cast(Widget, widget.Clock(format="   %e %b    %H:%M  ", **wdecor)),
    spacer(),
]


def systemWidgets() -> List[Widget]:
    return [
        cast(
            Widget,
            widget.TextBox(
                text=" 󰂚 ",
                mouse_callbacks={
                    "Button3": lazy.spawn("dunstctl history-clear"),
                    "Button1": lazy.spawn("dunstctl history-pop"),
                },
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
                **wdecor,
            ),
        ),
        spacer(),
        cast(Widget, UpowerWidget(**wdecor)),
    ]


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
                margin=3,
                padding=5,
            ),
        ),
    ]


def systemTrayWidget() -> List[Widget]:
    return [
        cast(Widget, widget.Systray(padding=10)),
        spacer(),
    ]


def main() -> List[Widget]:
    return timeWidget + groupWidgets() + systemTrayWidget() + systemWidgets()


def misc() -> List[Widget]:
    return timeWidget + groupWidgets() + systemWidgets()
