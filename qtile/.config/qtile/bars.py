from typing import Any, Dict, List

from acpi import AcpiWidget
from brightctl import BrightctlWidget
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration
from wpctl import AudioWidget, MicWidget

theme: Dict[str, Any] = {
    "accent": "#6f3aea",
    "alert": "#ff5555",
    # "fg": "#ffffff",
    # "bg": "#000000",
    "padding": 6,
}

ICON_NOTIFICATION = "󰂚"
ICON_PLAYER = "󰀰 "
ICON_NO_METADATA = "󱆵 "
ICON_PAUSED = "󱆵 "

wdecor: Dict[str, Any] = {
    # "background": theme["bg"],
    # "foreground": theme["fg"],
    "decorations": [
        RectDecoration(
            use_widget_background=False,
            radius=12,
            filled=True,
            group=True,
        )  # type: ignore
    ],
    "padding": theme["padding"],
}


def spacer(length: int = 10) -> widget.Spacer:
    return widget.Spacer(length=length)


def groupWidgets() -> List[Any]:
    return [
        widget.Clock(format="   %e %b    %H:%M  ", **wdecor),
        spacer(),
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


def systemWidgets(
    show_brightness: bool = True,
    show_battery: bool = True,
) -> List[Any]:
    widgets: List[Any] = [
        widget.Systray(padding=10),
        # widget.StatusNotifier(padding=10),
        spacer(),
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
                "Button2": lazy.widget["audio"].refresh(),
                "Button3": lazy.widget["audio"].toggle_mute(),
                "Button4": lazy.widget["audio"].volume_up(),
                "Button5": lazy.widget["audio"].volume_down(),
            },
            **wdecor,
        ),
        MicWidget(
            name="mic",
            mouse_callbacks={
                "Button2": lazy.widget["mic"].refresh(),
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
            BrightctlWidget(
                name="brightctl",
                mouse_callbacks={
                    "Button4": lazy.widget["brightctl"].increase(),
                    "Button5": lazy.widget["brightctl"].decrease(),
                },
                **wdecor,
            ),
        ]

    if show_battery:
        widgets.append(AcpiWidget(**wdecor))

    return widgets


def main() -> List[Any]:
    return groupWidgets() + systemWidgets()


def misc() -> List[Any]:
    return groupWidgets()
