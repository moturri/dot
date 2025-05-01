from functions import mic_mute, volume_down, volume_mute, volume_up
from libqtile.config import Click, Drag, DropDown, Group, Key, Match, ScratchPad
from libqtile.lazy import lazy

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
    Key([mod], "Tab", lazy.next_layout()),
    Key([mod], "w", lazy.window.kill()),
    Key([mod], "F11", lazy.window.toggle_fullscreen()),
    Key([mod], "F4", lazy.window.toggle_floating()),
    Key([mod, "control"], "r", lazy.reload_config()),
    Key([mod, "control"], "q", lazy.shutdown()),
    Key([mod], "period", lazy.next_screen()),
    Key([mod], "comma", lazy.prev_screen()),
    Key([mod], "F2", lazy.spawn("i3lock -c 000000")),
    Key([], "XF86MonBrightnessDown", lazy.spawn("brillo -U 5")),
    Key([], "XF86MonBrightnessUp", lazy.spawn("brillo -A 5")),
    Key([], "XF86AudioLowerVolume", lazy.function(volume_down)),
    Key([], "XF86AudioRaiseVolume", lazy.function(volume_up)),
    Key([], "XF86AudioMicMute", lazy.function(mic_mute)),
    Key([], "XF86AudioMute", lazy.function(volume_mute)),
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


groups = [
    Group("1", label="󰣇"),
    Group(
        "2",
        label="",
        matches=[
            Match(wm_class="alacritty"),
            Match(wm_class="org.wezfurlong.wezterm"),
        ],
    ),
    Group(
        "3",
        label="󰈹",
        matches=[
            Match(wm_class="firefox"),
            Match(wm_class="brave-browser"),
            Match(wm_class="zen"),
        ],
    ),
    Group(
        "4",
        label="󰊠",
        matches=[
            Match(wm_class="VirtualBox Manager"),
            Match(wm_class="octopi"),
        ],
    ),
    Group(
        "5",
        label="󰇮",
        matches=[
            Match(wm_class="Mail"),
        ],
    ),
    Group(
        "6",
        label="󰉌",
        matches=[
            Match(wm_class="libreoffice"),
            Match(wm_class="libreoffice-writer"),
            Match(wm_class="calibre"),
            Match(wm_class="calibre-gui"),
            Match(wm_class="org.pwmt.zathura"),
        ],
    ),
    Group(
        "7",
        label="󰠹",
        matches=[
            Match(wm_class="stremio"),
            Match(wm_class="mpv"),
        ],
    ),
    Group(
        "8",
        label="󰒃",
        matches=[
            Match(wm_class="bitwarden"),
            Match(wm_class="firewall-config"),
            Match(wm_class="gnome-disks"),
            Match(wm_class="timeshift-gtk"),
        ],
    ),
    Group(
        "9",
        label="󰌳",
        matches=[
            Match(wm_class="cider"),
            Match(wm_class="easyeffects"),
            Match(wm_class="galaxybudsclient"),
            Match(wm_class="spotify"),
            Match(wm_class="strawberry"),
        ],
    ),
]


for group in groups:
    keys.extend(
        [
            Key([mod], group.name, lazy.group[group.name].toscreen()),
            Key(
                [mod, "shift"],
                group.name,
                lazy.window.togroup(group.name, switch_group=True),
            ),
            Key([mod, "control"], group.name, lazy.window.togroup(group.name)),
        ]
    )


groups.append(
    ScratchPad(
        "scratchpad",
        [
            DropDown(
                "arandr", "arandr", width=0.4, height=0.4, x=0.3, y=0.1, opacity=0.9
            ),
            DropDown(
                "helvum", "helvum", width=0.8, height=0.8, x=0.1, y=0.1, opacity=0.9
            ),
            DropDown(
                "iwgtk", "iwgtk", width=0.4, height=0.5, x=0.3, y=0.1, opacity=0.9
            ),
            DropDown(
                "kitty", "kitty", width=0.8, height=0.8, x=0.1, y=0.1, opacity=0.9
            ),
            DropDown(
                "localsend",
                "localsend",
                width=0.6,
                height=0.6,
                x=0.2,
                y=0.1,
                opacity=0.9,
            ),
            DropDown(
                "obsidian", "obsidian", width=0.8, height=0.8, x=0.1, y=0.1, opacity=1
            ),
            DropDown(
                "thunar", "thunar", width=0.6, height=0.6, x=0.2, y=0.1, opacity=0.9
            ),
        ],
    )
)


scratches = {
    "arandr": "a",
    "helvum": "h",
    "iwgtk": "i",
    "kitty": "x",
    "localsend": "l",
    "obsidian": "o",
    "thunar": "t",
}


for name, key in scratches.items():
    keys.append(
        Key([mod, "control"], key, lazy.group["scratchpad"].dropdown_toggle(name))
    )
