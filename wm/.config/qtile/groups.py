from keys import keys, mod
from libqtile.config import DropDown, Group, Key, Match, ScratchPad
from libqtile.lazy import lazy

group_definitions = [
    (
        "1",
        "󰣇",
        [
            "octopi",
            "plasma-discover",
            "com.github.tchx84.Flatseal",
        ],
    ),
    (
        "2",
        "󰚩",
        [
            "org.wezfurlong.wezterm",
            "alacritty",
            "code-oss",
            "discord",
        ],
    ),
    (
        "3",
        "󰆋",
        [
            "firefox",
            "zen",
            "qbittorrent",
            "brave-browser",
        ],
    ),
    (
        "4",
        "󰖺",
        [
            "steam_app_291550",
            "CombatMaster.x86_64",
            "steam_app_2281730",
        ],
    ),
    (
        "5",
        "",
        [
            "VirtualBox Manager",
            "virt-manager",
            "steam",
            "retroarch",
        ],
    ),
    (
        "6",
        "󱉟",
        [
            "soffice.bin",
            "calibre",
            "calibre-gui",
            "org.pwmt.zathura",
            "obsidian",
            "Zotero",
            "Pdfarranger",
            "xournalpp",
        ],
    ),
    (
        "7",
        "󰔂",
        [
            "stremio",
            "stremio-enhanced",
            "upscayl",
            "mpv",
            "mpvk",
        ],
    ),
    (
        "8",
        "󰒃",
        [
            "bitwarden",
            "Bleachbit",
            "firewall-config",
            "timeshift-gtk",
            "kapitano",
            "KeePassXC",
            "GParted",
            "org.gnome.DiskUtility",
            "stacer",
            "wireshark",
        ],
    ),
    (
        "9",
        "󰝚",
        [
            "cider",
            "jamesdsp",
            "galaxybudsclient",
            "GalaxyBudsClient",
            "strawberry",
            "audacity",
        ],
    ),
    ("0", "󰶍", ["Mail"]),
]

groups = [
    Group(name, label=label, matches=[Match(wm_class=cls) for cls in classes])
    for name, label, classes in group_definitions
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


scratchpad = ScratchPad(
    "scratchpad",
    [
        DropDown(
            "arandr",
            "arandr",
            width=0.4,
            height=0.4,
            x=0.3,
            y=0.1,
            opacity=0.9,
        ),
        DropDown(
            "bluetui",
            "alacritty -e bluetui",
            width=0.4,
            height=0.5,
            x=0.3,
            y=0.1,
            opacity=1,
        ),
        # DropDown(
        #     "impala",
        #     "alacritty -e impala",
        #     width=0.6,
        #     height=0.7,
        #     x=0.2,
        #     y=0.1,
        #     opacity=1,
        # ),
        DropDown(
            "kitty",
            "kitty",
            width=0.8,
            height=0.8,
            x=0.1,
            y=0.1,
            opacity=1,
            on_focus_lost_hide=True,
        ),
        DropDown(
            "localsend",
            "localsend",
            width=0.5,
            height=0.5,
            x=0.25,
            y=0.1,
            opacity=0.9,
        ),
        DropDown(
            "obsidian",
            "obsidian",
            width=0.8,
            height=0.8,
            x=0.1,
            y=0.1,
            opacity=1,
            on_focus_lost_hide=True,
        ),
        DropDown(
            "pavucontrol-qt",
            "pavucontrol-qt",
            width=0.5,
            height=0.5,
            x=0.25,
            y=0.1,
            opacity=1,
        ),
        DropDown(
            "pcmanfm-qt",
            "pcmanfm-qt",
            width=0.7,
            height=0.7,
            x=0.15,
            y=0.1,
            opacity=1,
        ),
    ],
)

groups.append(scratchpad)

scratch_keys = {
    "arandr": "a",
    "bluetui": "b",
    # "impala": "i",
    "kitty": "x",
    "localsend": "l",
    "obsidian": "o",
    "pavucontrol-qt": "v",
    "pcmanfm-qt": "f",
}

keys.extend(
    [
        Key([mod, "control"], key, lazy.group["scratchpad"].dropdown_toggle(name))
        for name, key in scratch_keys.items()
    ]
)
