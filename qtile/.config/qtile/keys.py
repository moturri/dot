from libqtile.config import (Click, Drag, DropDown, Group, Key, Match,
                             ScratchPad)
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
    Key([mod], "Tab", lazy.next_layout()),
    Key([mod], "w", lazy.window.kill()),
    Key([], "F11", lazy.window.toggle_fullscreen()),
    Key([mod], "F4", lazy.window.toggle_floating()),
    Key([mod, "control"], "r", lazy.reload_config()),
    Key([mod, "control"], "q", lazy.shutdown()),
    Key([mod], "period", lazy.next_screen()),
    Key([mod], "comma", lazy.prev_screen()),
    Key([mod, "control"], "w", lazy.spawn("i3lock -c 000000")),
    # Key([mod], "r", lazy.spawncmd()),
    Key([mod], "r", lazy.spawn("rofi -show drun")),
    Key(
        [mod],
        "v",
        lazy.spawn(
            "rofi -modi 'clipboard:greenclip print' -show clipboard -run-command '{cmd}'"
        ),
    ),
    Key([mod], "F1", lazy.spawn("/home/m/.config/rofi/scripts/rofi-power.sh")),
    Key([mod], "z", lazy.spawn("rofi -show window")),
    Key([mod], "d", lazy.spawn("/home/m/.config/rofi/scripts/rofi-websearch.sh")),
    Key([mod], "f", lazy.spawn("/home/m/.config/rofi/scripts/rofi-filebrowser.sh")),
    Key([], "XF86MonBrightnessDown", lazy.spawn("brightnessctl set 5%-")),
    Key([], "XF86MonBrightnessUp", lazy.spawn("brightnessctl set +5%")),
    Key(
        [],
        "XF86AudioLowerVolume",
        lazy.spawn("amixer set Master 5%-"),
    ),
    Key(
        [],
        "XF86AudioRaiseVolume",
        lazy.spawn("amixer set Master 5%+"),
    ),
    Key(
        [],
        "XF86AudioMicMute",
        lazy.spawn("amixer set Capture toggle"),
    ),
    Key(
        [],
        "XF86AudioMute",
        lazy.spawn("amixer set Master toggle"),
    ),
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


mouse.extend(
    [
        Drag([mod], "Button4", lazy.layout.up(), start=lazy.layout.previous()),
        Drag([mod], "Button5", lazy.layout.down(), start=lazy.layout.next()),
    ]
)


groups = [
    Group(
        name="1",
        label="󰣇",
        # matches=[],
    ),
    Group(
        name="2",
        label="",
        matches=[
            Match(wm_class="alacritty"),
            Match(wm_class="org.wezfurlong.wezterm"),
        ],
    ),
    Group(
        name="3",
        label="󰈹",
        matches=[
            Match(wm_class="firefox"),
            Match(wm_class="brave-browser"),
            Match(wm_class="zen"),
        ],
    ),
    Group(
        name="4",
        label="󰊠",
        matches=[
            Match(wm_class="VirtualBox Manager"),
            Match(wm_class="octopi"),
        ],
    ),
    Group(
        name="5",
        label="󰇮",
        matches=[
            Match(wm_class="Mail"),
        ],
    ),
    Group(
        name="6",
        label="󰉌",
        matches=[
            Match(wm_class="libreoffice"),
            Match(wm_class="libreoffice-writer"),
            Match(wm_class="calibre-gui"),
            Match(wm_class="calibre"),
            Match(wm_class="org.pwmt.zathura"),
        ],
    ),
    Group(
        name="7",
        label="󰠹",
        matches=[
            Match(wm_class="stremio"),
            Match(wm_class="mpv"),
        ],
    ),
    Group(
        name="8",
        label="󰒃",
        matches=[
            Match(wm_class="bitwarden"),
            Match(wm_class="firewall-config"),
            Match(wm_class="gnome-disks"),
            Match(wm_class="timeshift-gtk"),
        ],
    ),
    Group(
        name="9",
        label="󰌳",
        matches=[
            Match(wm_class="cider"),
            Match(wm_class="galaxybudsclient"),
            Match(wm_class="spotify"),
            Match(wm_class="easyeffects"),
            Match(wm_class="strawberry"),
        ],
    ),
]

for i in groups:
    keys.extend(
        [
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
            ),
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name, switch_group=True),
            ),
            # Key(
            #     [mod, "shift"],
            #     i.name,
            #     lazy.window.togroup(i.name),
            # ),
        ]
    )

groups.append(
    ScratchPad(
        "scratchpad",
        [
            DropDown(
                "kitty", "kitty", width=0.8, height=0.8, x=0.1, y=0.1, opacity=0.9
            ),
            DropDown(
                "arandr", "arandr", width=0.4, height=0.5, x=0.3, y=0.1, opacity=0.9
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
            # DropDown("iwgtk", "iwgtk", width=0.4, height=0.5, x=0.3, y=0.1, opacity=0.9),
            DropDown(
                "obsidian",
                "obsidian",
                width=0.8,
                height=0.8,
                x=0.1,
                y=0.1,
                opacity=1,
            ),
            DropDown(
                "octopi",
                "/usr/bin/octopi",
                width=0.8,
                height=0.8,
                x=0.1,
                y=0.1,
                opacity=1,
            ),
            DropDown(
                "cider",
                "cider",
                width=0.8,
                height=0.8,
                x=0.1,
                y=0.1,
                opacity=1,
            ),
            DropDown(
                "spotify",
                "spotify",
                width=0.8,
                height=0.8,
                x=0.1,
                y=0.1,
                opacity=1,
            ),
            DropDown(
                "helvum",
                "helvum",
                width=0.8,
                height=0.8,
                x=0.1,
                y=0.1,
                opacity=0.9,
            ),
            # DropDown(
            #     "btop",
            #     "kitty -e btop",
            #     width=0.8,
            #     height=0.8,
            #     x=0.1,
            #     y=0.1,
            #     opacity=0.9,
            # ),
            # DropDown(
            #     "yazi",
            #     "kitty -e yazi",
            #     width=0.8,
            #     height=0.8,
            #     x=0.1,
            #     y=0.1,
            #     opacity=0.9,
            # ),
            DropDown(
                "thunar", "thunar", width=0.6, height=0.6, x=0.2, y=0.1, opacity=0.9
            ),
        ],
    )
)


scratches = {
    "kitty": "x",
    "arandr": "a",
    "localsend": "l",
    # "iwgtk": "i",
    "obsidian": "n",
    "octopi": "o",
    "cider": "m",
    "spotify": "s",
    "helvum": "h",
    # "btop": "b",
    # "yazi": "y",
    "thunar": "t",
}

for name, key in scratches.items():
    keys.append(
        Key([mod, "control"], key, lazy.group["scratchpad"].dropdown_toggle(name))
    )
