from groups import groups
from keys import keys, mod
from libqtile.config import DropDown, Key, ScratchPad
from libqtile.lazy import lazy

groups.append(
    ScratchPad(
        "scratchpad",
        [
            DropDown(
                "calcurse",
                "kitty -e calcurse",
                width=0.7,
                height=0.7,
                x=0.15,
                y=0.1,
                opacity=1,
            ),
            DropDown(
                "iwgtk", "iwgtk", width=0.4, height=0.6, x=0.3, y=0.1, opacity=0.9
            ),
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
                "obsidian", "obsidian", width=0.8, height=0.8, x=0.1, y=0.1, opacity=1
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
                on_focus_lost_hide=True,
            ),
        ],
    )
)


scratches = {
    "calcurse": "c",
    "iwgtk": "i",
    "kitty": "x",
    "localsend": "l",
    "obsidian": "o",
    "pavucontrol-qt": "v",
    "pcmanfm-qt": "p",
}


for name, key in scratches.items():
    keys.append(
        Key([mod, "control"], key, lazy.group["scratchpad"].dropdown_toggle(name))
    )
