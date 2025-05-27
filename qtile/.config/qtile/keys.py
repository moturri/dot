import os

from audio import AudioWidget, MicWidget
from brightness import BrilloWidget
from libqtile.config import Click, Drag, Key
from libqtile.lazy import lazy

mod = "mod4"
terminal = "kitty"

# Custom widgets
audio_widget = AudioWidget()
mic_widget = MicWidget()
brightness_widget = BrilloWidget()


# Define functions instead of inline lambdas
def increase_brightness(qtile):
    brightness_widget.cmd_increase()


def decrease_brightness(qtile):
    brightness_widget.cmd_decrease()


def volume_up(qtile):
    audio_widget.cmd_volume_up()


def volume_down(qtile):
    audio_widget.cmd_volume_down()


def toggle_mute(qtile):
    audio_widget.cmd_toggle_mute()


def toggle_mic_mute(qtile):
    mic_widget.cmd_toggle_mute()


# Common paths
rofi_scripts_path = "/home/m/.config/rofi/scripts/"

# Keybinding groups
window_navigation_keys = [
    Key([mod], "h", lazy.layout.left()),
    Key([mod], "l", lazy.layout.right()),
    Key([mod], "j", lazy.layout.down()),
    Key([mod], "k", lazy.layout.up()),
]

window_swapping_keys = [
    Key([mod, "shift"], "h", lazy.layout.swap_left()),
    Key([mod, "shift"], "l", lazy.layout.swap_right()),
    Key([mod, "shift"], "j", lazy.layout.shuffle_down()),
    Key([mod, "shift"], "k", lazy.layout.shuffle_up()),
]

window_resize_keys = [
    Key([mod], "i", lazy.layout.grow()),
    Key([mod], "m", lazy.layout.shrink()),
    Key([mod], "n", lazy.layout.reset()),
    Key([mod, "shift"], "n", lazy.layout.normalize()),
]

layout_control_keys = [
    Key([mod], "o", lazy.layout.maximize()),
    Key([mod, "shift"], "space", lazy.layout.flip()),
    Key([mod, "shift"], "Return", lazy.layout.toggle_split()),
    Key([mod], "Tab", lazy.next_layout()),
]

program_launch_keys = [
    Key([mod], "Return", lazy.spawn(terminal)),
    Key([mod], "r", lazy.spawn("rofi -show drun")),
    Key([mod], "z", lazy.spawn("rofi -show window")),
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
]

session_keys = [
    Key([mod], "w", lazy.window.kill()),
    Key([mod], "F11", lazy.window.toggle_fullscreen()),
    Key([mod], "F4", lazy.window.toggle_floating()),
    Key([mod, "control"], "r", lazy.reload_config()),
    Key([mod, "control"], "q", lazy.shutdown()),
    Key([mod], "period", lazy.next_screen()),
    Key([mod], "comma", lazy.prev_screen()),
]

system_keys = [
    Key([mod], "F2", lazy.spawn("i3lock -c 000000")),
    Key([mod], "Print", lazy.spawn("screengrab")),
]

brightness_keys = [
    Key([], "XF86MonBrightnessUp", lazy.function(increase_brightness)),
    Key([], "XF86MonBrightnessDown", lazy.function(decrease_brightness)),
]

audio_keys = [
    Key([], "XF86AudioRaiseVolume", lazy.function(volume_up)),
    Key([], "XF86AudioLowerVolume", lazy.function(volume_down)),
    Key([], "XF86AudioMute", lazy.function(toggle_mute)),
    Key([], "XF86AudioMicMute", lazy.function(toggle_mic_mute)),
]

media_keys = [
    Key([mod], "F7", lazy.widget["mpris"].toggle_player()),
]

# Combine all keybindings
keys = (
    window_navigation_keys
    + window_swapping_keys
    + window_resize_keys
    + layout_control_keys
    + program_launch_keys
    + session_keys
    + system_keys
    + brightness_keys
    + audio_keys
    + media_keys
)

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
