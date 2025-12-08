# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import subprocess
from typing import Any, List

from bars import main, misc, theme
from groups import groups  # noqa: F401
from keys import keys, mouse  # noqa: F401
from libqtile import bar, hook, layout
from libqtile.config import Match, Screen

widget_defaults = dict(
    font="Inter Variable Bold",
    fontsize=15,
)

ldecor = {
    "margin": 8,
    "border_width": 0,
    "border_focus": theme["active"],
    "border_normal": theme["bbg"],
}

layouts = [
    layout.MonadTall(**ldecor),  # type: ignore
    layout.MonadWide(**ldecor),  # type: ignore
    layout.MonadThreeCol(**ldecor),  # type: ignore
    layout.Max(**ldecor),  # type: ignore
]

# wallpaper_path = "/home/m/.config/qtile/wallpaper/arc.jpg"

screens = [
    Screen(
        # wallpaper=wallpaper_path,
        # wallpaper_mode="stretch",
        top=bar.Bar(
            main(),
            28,
            # background=theme["transparent"],
            margin=[0, 8, 0, 8],
        ),
    ),
    Screen(
        # wallpaper=wallpaper_path,
        # wallpaper_mode="stretch",
        top=bar.Bar(
            misc(),
            28,
            # background=theme["transparent"],
            margin=[0, 8, 0, 8],
        ),
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
        Match(wm_class="iwgtk"),
        Match(wm_class="crx_nngceckbapebfimnlniiiahkandclblb"),
        Match(wm_class="remote-viewer"),
        Match(wm_class="nm-connection-editor"),
        Match(wm_class="wihotspot"),
    ],
)

dgroups_key_binder = None
dgroups_app_rules: List[Any] = []
follow_mouse_focus = True
bring_front_click = "floating_only"
floats_kept_above = True
cursor_warp = True
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wl_input_rules = None
wl_xcursor_theme = None
wl_xcursor_size = 24
wmname = "Qtile"


@hook.subscribe.startup_once
def autostart() -> None:
    home = os.path.expanduser("~/.config/qtile/scripts")
    scripts = ["autostart.sh", "monitors.sh"]
    for script in scripts:
        script_path = os.path.join(home, script)
        if os.path.exists(script_path):
            subprocess.Popen([script_path])
