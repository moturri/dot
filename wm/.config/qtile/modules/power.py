import subprocess

from libqtile.core.manager import Qtile
from libqtile.lazy import lazy
from qtile_extras.popup import PopupRelativeLayout, PopupText


def show_power_menu(qtile: Qtile) -> None:

    lock_cmd = "i3lock -n -c 000000"

    if (
        subprocess.call(
            ["which", "i3lock"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        != 0
    ):
        lock_action = lazy.spawn("notify-send 'i3lock not found'")
    else:
        lock_action = lazy.spawn(lock_cmd)

    entries = [
        ("Lock", lock_action),
        ("Suspend", lazy.spawn("systemctl suspend")),
        ("Logout", lazy.shutdown()),
        ("Reboot", lazy.spawn("systemctl reboot")),
        ("Shutdown", lazy.spawn("systemctl poweroff")),
        ("Cancel", None),
    ]

    controls = []
    y = 0.05
    entry_height = 0.13
    entry_width = 0.7

    for label, action in entries:
        controls.append(
            PopupText(  # type: ignore
                text=label,
                pos_x=(1 - entry_width) / 2,
                pos_y=y,
                width=entry_width,
                height=entry_height,
                h_align="center",
                v_align="center",
                highlight="7d37a3",
                mouse_callbacks={"Button1": action} if action else {},
            )
        )
        y += entry_height + 0.02

    layout = PopupRelativeLayout(
        qtile,
        width=220,
        height=240,
        controls=controls,
        background="000000",
        border_width=0,
        close_on_click=True,
        initial_focus=None,
    )

    layout.show(
        centered=True,
        relative_to=5,
        relative_to_bar=True,
    )
