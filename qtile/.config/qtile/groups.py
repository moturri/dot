from keys import keys, mod
from libqtile.config import Group, Key, Match
from libqtile.lazy import lazy

groups = [
    Group(
        "1",
        label="󰣇",
        matches=[
            Match(wm_class="stacer"),
            Match(wm_class="pcmanfm-qt"),
            Match(wm_class="vscodium"),
        ],
    ),
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
            Match(wm_class="soffice.bin"),
            Match(wm_class="calibre"),
            Match(wm_class="calibre-gui"),
            Match(wm_class="org.pwmt.zathura"),
            Match(wm_class="obsidian"),
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
            Match(wm_class="KeePassXC"),
            Match(wm_class="GParted"),
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
