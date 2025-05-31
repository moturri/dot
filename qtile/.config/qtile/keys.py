import os

from brillo import BrilloWidget
from libqtile.config import Click, Drag, Key, KeyChord
from libqtile.core.manager import Qtile
from libqtile.lazy import lazy
from wpctl import AudioWidget, MicWidget

mod = "mod4"
terminal = "kitty"

# Instantiate custom widgets to call their methods in keybindings
audio = AudioWidget()
mic = MicWidget()
brillo = BrilloWidget()


# Brightness control helpers
def brillo_up(qtile: Qtile) -> None:
    brillo.increase()


def brillo_down(qtile: Qtile) -> None:
    brillo.decrease()


# Audio control helpers
def volume_up(qtile: Qtile) -> None:
    audio.volume_up()


def volume_down(qtile: Qtile) -> None:
    audio.volume_down()


def toggle_mute(qtile: Qtile) -> None:
    audio.toggle_mute()


def toggle_mic_mute(qtile: Qtile) -> None:
    mic.toggle_mute()


# Common rofi scripts path
rofi_scripts_path: str = os.path.expanduser("~/.config/rofi/scripts/")

# Keybindings:
keys = [
    # Window navigation
    Key([mod], "h", lazy.layout.left()),
    Key([mod], "l", lazy.layout.right()),
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "k", lazy.layout.up()),
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
    Key([mod, "shift"], "space", lazy.layout.flip()),
    Key([mod, "shift"], "Return", lazy.layout.toggle_split()),
    Key([mod], "Tab", lazy.next_layout()),
    # Program launchers
    Key([mod], "Return", lazy.spawn(terminal)),
    Key([mod], "r", lazy.spawn("rofi -show drun")),
    Key([mod], "z", lazy.spawn("rofi -show window")),
    Key(
        [mod, "shift"],
        "c",
        lazy.spawn("rofi -show calc -modi calc -no-show-match -no-sort"),
    ),
    Key([mod, "shift"], "e", lazy.spawn("rofi -modi emoji -show emoji")),
    Key([mod], "t", lazy.spawn(os.path.join(rofi_scripts_path, "rofi-websearch.sh"))),
    Key(
        [mod], "v", lazy.spawn("rofi -modi 'clipboard:greenclip print' -show clipboard")
    ),
    Key([mod], "F1", lazy.spawn(os.path.join(rofi_scripts_path, "rofi-power.sh"))),
    Key([mod], "F12", lazy.spawn(os.path.join(rofi_scripts_path, "rofi-keys.sh"))),
    Key(
        [mod, "shift"],
        "a",
        lazy.spawn(os.path.join(rofi_scripts_path, "rofi-display.sh")),
    ),
    # Session/window management
    Key([mod], "w", lazy.window.kill()),
    Key([mod], "F11", lazy.window.toggle_fullscreen()),
    Key([mod], "F4", lazy.window.toggle_floating()),
    Key([mod, "control"], "r", lazy.reload_config()),
    Key([mod, "control"], "q", lazy.shutdown()),
    Key([mod], "period", lazy.next_screen()),
    Key([mod], "comma", lazy.prev_screen()),
    # System control
    Key([mod], "F2", lazy.spawn("i3lock -c 000000")),
    Key([mod], "Print", lazy.spawn("screengrab")),
    # Brightness keys
    Key([], "XF86MonBrightnessUp", lazy.function(brillo_up)),
    Key([], "XF86MonBrightnessDown", lazy.function(brillo_down)),
    # Audio keys
    Key([], "XF86AudioRaiseVolume", lazy.function(volume_up)),
    Key([], "XF86AudioLowerVolume", lazy.function(volume_down)),
    Key([], "XF86AudioMute", lazy.function(toggle_mute)),
    Key([], "XF86AudioMicMute", lazy.function(toggle_mic_mute)),
    # Media controls (with mpris widget)
    Key([mod], "F7", lazy.widget["mpris"].toggle_player()),
] + [
    KeyChord(
        [mod],
        "b",
        [
            Key([], "p", lazy.spawn("pcmanfm-qt")),
            Key([], "x", lazy.spawn("kitty")),
        ],
    )
]

# Mouse bindings
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
