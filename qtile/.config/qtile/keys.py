from brightness import bright_down, bright_up
from libqtile.config import Click, Drag, Key
from libqtile.lazy import lazy
from mic import mic_mute
from volume import vol_down, vol_mute, vol_up

mod = "mod4"
terminal = "kitty"


keys = [
    Key([mod], "h", lazy.layout.left()),
    Key([mod], "l", lazy.layout.right()),
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "k", lazy.layout.up()),
    Key([mod, "shift"], "h", lazy.layout.swap_left()),
    Key([mod, "shift"], "l", lazy.layout.swap_right()),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
    Key([mod], "i", lazy.layout.grow()),
    Key([mod], "m", lazy.layout.shrink()),
    Key([mod], "n", lazy.layout.reset()),
    Key([mod, "shift"], "n", lazy.layout.normalize()),
    Key([mod], "o", lazy.layout.maximize()),
    Key([mod, "shift"], "space", lazy.layout.flip()),
    Key([mod, "shift"], "Return", lazy.layout.toggle_split()),
    Key([mod], "Return", lazy.spawn(terminal)),
    Key([mod], "r", lazy.spawn("rofi -show drun")),
    Key([mod], "z", lazy.spawn("rofi -show window")),
    Key([mod], "t", lazy.spawn("/home/m/.config/rofi/scripts/rofi-websearch.sh")),
    Key(
        [mod], "v", lazy.spawn("rofi -modi 'clipboard:greenclip print' -show clipboard")
    ),
    Key([mod], "F1", lazy.spawn("/home/m/.config/rofi/scripts/rofi-power.sh")),
    Key([mod], "F12", lazy.spawn("/home/m/.config/rofi/scripts/rofi-keys.sh")),
    Key(
        [mod, "shift"],
        "a",
        lazy.spawn("/home/m/.config/rofi/scripts/rofi-display.sh"),
    ),
    Key([mod], "Tab", lazy.next_layout()),
    Key([mod], "w", lazy.window.kill()),
    Key([mod], "F11", lazy.window.toggle_fullscreen()),
    Key([mod], "F4", lazy.window.toggle_floating()),
    Key([mod, "control"], "r", lazy.reload_config()),
    Key([mod, "control"], "q", lazy.shutdown()),
    Key([mod], "period", lazy.next_screen()),
    Key([mod], "comma", lazy.prev_screen()),
    Key([mod], "F2", lazy.spawn("i3lock -c 000000")),
    Key([mod], "Print", lazy.spawn("screengrab")),
    Key([], "XF86MonBrightnessDown", lazy.function(bright_down)),
    Key([], "XF86MonBrightnessUp", lazy.function(bright_up)),
    Key([], "XF86AudioLowerVolume", lazy.function(vol_down)),
    Key([], "XF86AudioRaiseVolume", lazy.function(vol_up)),
    Key([], "XF86AudioMicMute", lazy.function(mic_mute)),
    Key([], "XF86AudioMute", lazy.function(vol_mute)),
    Key([mod], "F7", lazy.widget["mpris"].toggle_player()),
]


mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod],
        "Button3",
        lazy.window.set_size_floating(),
        start=lazy.window.get_size(),
    ),
    Click(
        [mod],
        "Button2",
        lazy.window.bring_to_front(),
    ),
    Drag(
        [mod],
        "Button4",
        lazy.layout.up(),
        start=lazy.layout.previous(),
    ),
    Drag(
        [mod],
        "Button5",
        lazy.layout.down(),
        start=lazy.layout.next(),
    ),
]
