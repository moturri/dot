# from bars import rangi
from libqtile import layout
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
    Key([mod], "e", lazy.spawn(terminal)),
    Key([mod], "Tab", lazy.next_layout()),
    Key([mod], "w", lazy.window.kill()),
    Key([mod], "f", lazy.window.toggle_fullscreen()),
    Key([mod], "t", lazy.window.toggle_floating()),
    Key([mod, "control"], "r", lazy.reload_config()),
    Key([mod, "control"], "q", lazy.shutdown()),
    Key([mod], "r", lazy.spawncmd()),
    Key([mod], "a", lazy.spawn("rofi -show run")),
    Key([mod], "period", lazy.next_screen()),
    Key([mod], "comma", lazy.prev_screen()),
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


ldecor = {
    "margin": 8,
    "border_width": 0,
    # "border_focus": rangi[2],
    # "border_normal": rangi[0],
}


layouts = [
    layout.MonadTall(**ldecor),
    layout.MonadWide(**ldecor),
    layout.MonadThreeCol(**ldecor),
    layout.Max(**ldecor),
]


groups = [
    Group(
        name="1",
        label="󰣇",
        layouts=[
            layout.MonadThreeCol(**ldecor),
            layout.MonadTall(**ldecor),
            layout.MonadWide(**ldecor),
        ],
        matches=[Match(wm_class="firefox")],
    ),
    Group(
        name="2",
        label="",
        layouts=[
            layout.MonadThreeCol(**ldecor),
            layout.MonadTall(**ldecor),
        ],
        matches=[
            Match(wm_class="alacritty"),
            Match(wm_class="org.wezfurlong.wezterm"),
        ],
    ),
    Group(
        name="3",
        label="",
        layouts=[layout.MonadThreeCol(**ldecor)],
        matches=[
            Match(wm_class="VirtualBox Manager"),
        ],
    ),
    Group(
        name="4",
        label="󰊠",
        layouts=[layout.MonadThreeCol(**ldecor)],
        matches=[
            Match(wm_class="octopi"),
        ],
    ),
    Group(
        name="5",
        label="󰇮",
        layouts=[layout.MonadTall(**ldecor)],
        matches=[
            Match(wm_class="Mail"),
        ],
    ),
    Group(
        name="6",
        label="󰉌",
        layouts=[layout.MonadWide(**ldecor)],
        matches=[
            Match(wm_class="libreoffice"),
        ],
    ),
    Group(
        name="7",
        label="󰃽",
    ),
    Group(
        name="8",
        label="󰒃",
        layouts=[layout.MonadThreeCol(**ldecor)],
        matches=[
            Match(wm_class="bitwarden"),
        ],
    ),
    Group(
        name="9",
        label="󰌳",
        layouts=[layout.MonadThreeCol(**ldecor)],
        matches=[
            Match(wm_class="cider"),
            Match(wm_class="sayonara"),
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
            DropDown("term", "kitty", width=0.8, height=0.8, x=0.1, y=0.1, opacity=0.9),
            DropDown(
                "mixer", "pavucontrol", width=0.4, height=0.5, x=0.3, y=0.1, opacity=0.9
            ),
            DropDown(
                "btop",
                "kitty -e btop",
                width=0.8,
                height=0.8,
                x=0.1,
                y=0.1,
                opacity=0.9,
            ),
            DropDown(
                "yazi",
                "kitty -e yazi",
                width=0.8,
                height=0.8,
                x=0.1,
                y=0.1,
                opacity=0.9,
            ),
        ],
    )
)


scratches = {
    "term": "g",
    "mixer": "u",
    "btop": "b",
    "yazi": "y",
}

for name, key in scratches.items():
    keys.append(Key([mod], key, lazy.group["scratchpad"].dropdown_toggle(name)))
