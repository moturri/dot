import os
import subprocess

from bars import main, misc
from groups import *
from keys import *
from libqtile import bar, hook, layout
from libqtile.config import Match, Screen

widget_defaults = dict(
    font="Inter Variable Bold",
    fontsize=15,
)

ldecor = {
    "margin": 8,
    "border_width": 0,
}

layouts = [
    layout.MonadTall(**ldecor),
    layout.MonadWide(**ldecor),
    layout.MonadThreeCol(**ldecor),
    layout.Max(**ldecor),
]

uwazi = "#00000000"
wallpaper_path = "/home/m/.config/qtile/wallpaper/arc.jpg"

screens = [
    Screen(
        wallpaper=wallpaper_path,
        wallpaper_mode="stretch",
        top=bar.Bar(main(), 28, background=uwazi, margin=[4, 8, 0, 8]),
    ),
    Screen(
        wallpaper=wallpaper_path,
        wallpaper_mode="stretch",
        top=bar.Bar(misc(), 28, background=uwazi, margin=[4, 8, 0, 8]),
    ),
]

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
        Match(wm_class="blueman-manager"),
        Match(wm_class="localsend"),
        Match(wm_class="firetools"),
        Match(wm_class="iwgtk"),
        Match(wm_class="crx_nngceckbapebfimnlniiiahkandclblb"),
        Match(wm_class="remote-viewer"),
    ],
)

dgroups_key_binder = None
dgroups_app_rules = []
follow_mouse_focus = True
bring_front_click = "floating_only"
floats_kept_above = True
cursor_warp = True
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wmname = "LG3D"


@hook.subscribe.startup_once
def autostart():
    """
    Run startup scripts when Qtile starts for the first time.
    """
    home = os.path.expanduser("~/.config/qtile/scripts")
    scripts = ["autostart.sh", "monitors.sh"]
    for script in scripts:
        script_path = os.path.join(home, script)
        if os.path.exists(script_path):
            subprocess.run([script_path], check=False)
