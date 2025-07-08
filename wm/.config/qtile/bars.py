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
    "fg": "#ffffff",
    "bg": "#0a0a0a",
    "padding": 6,
}


def decorated_widget(widget_class: Any, **config: Any) -> Any:
    return widget_class(
        **{
            "background": theme["bg"],
            "foreground": theme["fg"],
            "decorations": [
                RectDecoration(
                    use_widget_background=True,
                    radius=12,
                    filled=True,
                    group=True,
                )  # type: ignore
            ],
            "padding": theme["padding"],
            **config,
        }
    )


def spacer(length: int = 10) -> widget.Spacer:
    return widget.Spacer(length=length)


def clockWidget() -> List[Any]:
    return [
        decorated_widget(widget.Clock, format="   %e %b    %H:%M  "),
        spacer(),
    ]


def systemTray() -> List[Any]:
    return [
        widget.Systray(padding=10),
        # widget.StatusNotifier(padding=10), # Wayland
    ]


def groupWidgets() -> List[Any]:
    return [
        decorated_widget(
            widget.GroupBox,
            hide_unused=True,
            highlight_method="text",
            urgent_alert_method="text",
            fontsize=18,
            disable_drag=True,
            this_current_screen_border=theme["accent"],
            urgent_border=theme["alert"],
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
        decorated_widget(
            widget.TextBox,
            text=" 󰂚 ",
            mouse_callbacks={
                "Button1": lazy.spawn("dunstctl history-pop"),
                "Button3": lazy.spawn("dunstctl history-clear"),
            },
        ),
        decorated_widget(
            widget.Mpris2,
            name="mpris",
            format="󰀰 ",
            no_metadata_text="󱆵 ",
            paused_text="󱆵 ",
            popup_hide_timeout=8,
            width=60,
            mouse_callbacks={"Button3": lazy.widget["mpris"].toggle_player()},
        ),
        spacer(),
        decorated_widget(
            AudioWidget,
            name="audio",
            mouse_callbacks={
                "Button2": lazy.widget["audio"].refresh(),
                "Button3": lazy.widget["audio"].toggle_mute(),
                "Button4": lazy.widget["audio"].volume_up(),
                "Button5": lazy.widget["audio"].volume_down(),
            },
        ),
        decorated_widget(
            MicWidget,
            name="mic",
            mouse_callbacks={
                "Button2": lazy.widget["mic"].refresh(),
                "Button3": lazy.widget["mic"].toggle_mute(),
                "Button4": lazy.widget["mic"].volume_up(),
                "Button5": lazy.widget["mic"].volume_down(),
            },
        ),
        spacer(),
        *(
            [
                decorated_widget(
                    BrightctlWidget,
                    name="brightctl",
                    mouse_callbacks={
                        "Button4": lazy.widget["brightctl"].increase(),
                        "Button5": lazy.widget["brightctl"].decrease(),
                    },
                ),
                spacer(),
            ]
            if show_brightness
            else []
        ),
        *(
            [
                decorated_widget(
                    AcpiWidget,
                    name="acpi",
                    mouse_callbacks={
                        "Button2": lazy.widget["acpi"].refresh(),
                    },
                )
            ]
            if show_battery
            else []
        ),
    ]

    return widgets


def main() -> List[Any]:
    return clockWidget() + groupWidgets() + systemWidgets() + systemTray()


def misc() -> List[Any]:
    return clockWidget() + groupWidgets()
