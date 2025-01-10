import os
import subprocess

from bars import main, misc  # rangi
from keybinds import *
from libqtile import bar, hook, layout
from libqtile.config import Match, Screen

layout_theme = {
    "margin": 8,
    "border_width": 0,
    # "border_focus": colors[2],
    # "border_normal": colors[0],
}


layouts = [
    layout.MonadTall(**layout_theme),
    layout.MonadWide(**layout_theme),
    layout.MonadThreeCol(**layout_theme),
    layout.Max(**layout_theme),
]


widget_defaults = dict(
    font="Inter Variable Bold",
    fontsize=14,
)

lucid = "#00000000"

screens = [
    Screen(
        wallpaper="/mnt/sda2/Library/UnixImgs/arc.jpg",
        wallpaper_mode="stretch",
        top=bar.Bar(main(), 28, background=lucid, margin=[4, 8, 0, 8]),
    ),
    Screen(
        wallpaper="/mnt/sda2/Library/UnixImgs/thunder.jpg",
        wallpaper_mode="stretch",
        top=bar.Bar(misc(), 28, background=lucid, margin=[4, 8, 0, 8]),
    ),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    border_width=0,
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),
        Match(wm_class="makebranch"),
        Match(wm_class="maketag"),
        Match(wm_class="ssh-askpass"),
        Match(title="branchdialog"),
        Match(title="pinentry"),
        Match(wm_class="arandr"),
        Match(wm_class="blueman-manager"),
        Match(wm_class="localsend_app"),
        Match(wm_class="wihotspot"),
        Match(wm_class="nm-connection-editor"),
    ],
)


auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wl_input_rules = None
wl_xcursor_theme = None
wl_xcursor_size = 24


@hook.subscribe.startup_once
def autostart():
    autostartScript = os.path.expanduser("~/.config/qtile/scripts/autostart.sh")
    monitorScript = os.path.expanduser("~/.config/qtile/scripts/monitors.sh")
    subprocess.run([autostartScript])
    subprocess.run([monitorScript])


wmname = "qtile"
