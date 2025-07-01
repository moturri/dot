import os

from libqtile.config import Click, Drag, Key, KeyChord
from libqtile.lazy import lazy

mod = "mod4"
terminal = "alacritty"

rofi_scripts = os.path.expanduser("~/.config/rofi/scripts/")
rofi_calc = "rofi -show calc -modi calc -no-show-match -no-sort"
rofi_emoji = "rofi -modi emoji -show emoji"
rofi_clipboard = "rofi -modi 'clipboard:greenclip print' -show clipboard"
rofi_drun = "rofi -show drun"
rofi_window = "rofi -show window"

keys = [
    # Window navigation
    Key([mod], "h", lazy.layout.left()),
    Key([mod], "l", lazy.layout.right()),
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "k", lazy.layout.up()),
    Key(["mod1"], "Tab", lazy.window.bring_to_front(), lazy.group.next_window()),
    Key(
        ["mod1", "shift"], "Tab", lazy.window.bring_to_front(), lazy.group.prev_window()
    ),
    # Window swapping
    Key([mod, "shift"], "h", lazy.layout.swap_left()),
    Key([mod, "shift"], "l", lazy.layout.swap_right()),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
    # Window resizing
    Key([mod], "i", lazy.layout.grow()),
    Key([mod], "m", lazy.layout.shrink()),
    Key([mod], "n", lazy.layout.reset()),
    Key([mod, "shift"], "n", lazy.layout.normalize()),
    # Layout control
    Key([mod], "o", lazy.layout.maximize()),
    Key([mod, "shift"], "s", lazy.layout.toggle_auto_maximize()),
    Key([mod, "shift"], "space", lazy.layout.flip()),
    Key([mod, "shift"], "Return", lazy.layout.toggle_split()),
    Key([mod], "Tab", lazy.next_layout()),
    # Application launchers
    Key([mod], "Return", lazy.spawn(terminal)),
    Key([mod], "r", lazy.spawn(rofi_drun)),
    Key([mod], "z", lazy.spawn(rofi_window)),
    Key([mod, "shift"], "c", lazy.spawn(rofi_calc)),
    Key([mod, "shift"], "e", lazy.spawn(rofi_emoji)),
    Key([mod], "v", lazy.spawn(rofi_clipboard)),
    Key([mod], "t", lazy.spawn(os.path.join(rofi_scripts, "rofi-websearch.sh"))),
    Key([mod], "F12", lazy.spawn(os.path.join(rofi_scripts, "rofi-keys.sh"))),
    Key([mod, "shift"], "a", lazy.spawn(os.path.join(rofi_scripts, "rofi-display.sh"))),
    # Session/window management
    Key([mod], "w", lazy.window.kill()),
    Key([mod], "F11", lazy.window.toggle_fullscreen()),
    Key([mod], "F4", lazy.window.toggle_floating()),
    Key([mod, "control"], "r", lazy.reload_config()),
    Key([mod, "control"], "q", lazy.shutdown()),
    Key([], "XF86PowerOff", lazy.spawn(os.path.join(rofi_scripts, "rofi-power.sh"))),
    # Multi-monitor
    Key([mod], "period", lazy.next_screen()),
    Key([mod], "comma", lazy.prev_screen()),
    # Bar visibility
    Key([mod], "F3", lazy.hide_show_bar("top")),
    # System utilities
    Key([mod], "F1", lazy.spawn("i3lock -c 000000")),
    Key([mod], "Print", lazy.spawn("screengrab")),
    # Brightness control
    Key([], "XF86MonBrightnessUp", lazy.widget["brightctl"].increase()),
    Key([], "XF86MonBrightnessDown", lazy.widget["brightctl"].decrease()),
    # Audio control
    Key([], "XF86AudioRaiseVolume", lazy.widget["audio"].volume_up()),
    Key([], "XF86AudioLowerVolume", lazy.widget["audio"].volume_down()),
    Key([], "XF86AudioMute", lazy.widget["audio"].toggle_mute()),
    # Mic mute toggle
    Key([], "XF86AudioMicMute", lazy.widget["mic"].toggle_mute()),
    # Media control
    Key([mod], "F7", lazy.widget["mpris"].toggle_player()),
] + [
    KeyChord(
        [mod],
        "b",
        [
            Key([], "o", lazy.spawn("/usr/bin/octopi")),
            Key([], "l", lazy.spawn("soffice")),
            Key([], "k", lazy.spawn("kitty")),
            Key([], "a", lazy.spawn("alacritty")),
            Key([], "p", lazy.spawn("pcmanfm-qt")),
            Key([], "z", lazy.spawn("zen-browser")),
            Key([], "c", lazy.spawn("cider")),
            Key([], "s", lazy.spawn("stremio")),
            Key([], "b", lazy.spawn("brave")),
        ],
    )
]

mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]
