import os
import subprocess

from libqtile import bar, hook, layout, qtile
from libqtile.config import (Click, Drag, DropDown, Group, Key, Match,
                             ScratchPad, Screen)
from libqtile.lazy import lazy
from qtile_extras import widget
from qtile_extras.widget.decorations import RectDecoration

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
        matches=[],
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
        label="󰈹",
        layouts=[
            layout.MonadTall(**ldecor),
            layout.MonadThreeCol(**ldecor),
            layout.MonadWide(**ldecor),
        ],
        matches=[
            Match(wm_class="firefox"),
            Match(wm_class="brave-browser"),
            Match(wm_class="zen"),
        ],
    ),
    Group(
        name="4",
        label="󰊠",
        layouts=[layout.MonadThreeCol(**ldecor)],
        matches=[
            Match(wm_class="VirtualBox Manager"),
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
        layouts=[
            layout.MonadTall(**ldecor),
            layout.MonadThreeCol(**ldecor),
            layout.MonadWide(**ldecor),
        ],
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
        layouts=[layout.MonadThreeCol(**ldecor)],
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
        layouts=[layout.MonadThreeCol(**ldecor)],
        matches=[
            Match(wm_class="cider"),
            Match(wm_class="sayonara"),
            Match(wm_class="galaxybudsclient"),
            Match(wm_class="spotify"),
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
            # DropDown("net", "iwgtk", width=0.4, height=0.5, x=0.3, y=0.1, opacity=0.9),
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
            DropDown(
                "thunar", "thunar", width=0.6, height=0.6, x=0.2, y=0.1, opacity=0.9
            ),
        ],
    )
)


scratches = {
    "term": "e",
    "mixer": "p",
    # "net": "v",
    "btop": "b",
    "yazi": "y",
    "thunar": "d",
}

for name, key in scratches.items():
    keys.append(Key([mod], key, lazy.group["scratchpad"].dropdown_toggle(name)))


def bright():
    result = subprocess.run(["brightnessctl", "g"], capture_output=True, text=True)
    max_brightness = subprocess.run(
        ["brightnessctl", "m"], capture_output=True, text=True
    )

    if result.returncode != 0 or max_brightness.returncode != 0:
        return "👾 %"

    current_brightness = int(result.stdout.strip())
    max_brightness = int(max_brightness.stdout.strip())
    brightness_percentage = int((current_brightness / max_brightness) * 100)

    if brightness_percentage > 80:
        icon = "🌞 "
        color = "gold"
    elif brightness_percentage > 60:
        icon = "🌤️ "
        color = "darkorange"
    elif brightness_percentage > 40:
        icon = "🌥️ "
        color = "dodgerblue"
    elif brightness_percentage > 20:
        icon = "🌙 "
        color = "peru"
    else:
        icon = "🌒 "
        color = "dimgrey"

    return f'<span foreground="{color}">{icon} {brightness_percentage}%</span>'


def batt():
    result = subprocess.run(["acpi"], capture_output=True, text=True)
    if result.returncode != 0:
        return "💀 %"

    output = result.stdout.strip().split(", ")
    battery_percentage = int(output[1].replace("%", "").strip())
    battery_state = output[0].split()[-1]
    if battery_percentage > 80:
        icon = "  "
        color = "lime"
    elif battery_percentage > 60:
        icon = "  "
        color = "palegreen"
    elif battery_percentage > 40:
        icon = "  "
        color = "orange"
    elif battery_percentage > 20:
        icon = "  "
        color = "coral"
    else:
        icon = "  "
        color = "red"

    if battery_state == "Charging":
        icon = "⚡ " + icon
        color = "aqua"

    return f'<span foreground="{color}">{icon}  {battery_percentage}%</span>'


def vol():
    try:
        result = subprocess.run(
            ["amixer", "get", "Master"],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()

        volume_line = [line for line in output.splitlines() if "Playback" in line][-1]
        volume_percentage = int(volume_line.split("[")[1].split("%")[0])
        is_muted = "[off]" in volume_line

        if is_muted or volume_percentage == 0:
            icon = "  "
            color = "brown"
        elif volume_percentage > 100:
            icon = "󰕾  "
            color = "peru"
        elif volume_percentage > 80:
            icon = "󰕾  "
            color = "tomato"
        elif volume_percentage > 60:
            icon = "󰕾  "
            color = "tan"
        elif volume_percentage > 40:
            icon = "󰕾  "
            color = "dodgerblue"
        elif volume_percentage > 20:
            icon = "󰖀  "
            color = "orchid"
        else:
            icon = "󰕿  "
            color = "dimgrey"

        return f'<span foreground="{color}">{icon} {volume_percentage}%</span>'

    except subprocess.CalledProcessError:
        return "󰕿 %"


def main():
    return [
        widget.Clock(
            format="%e %b   %H:%M ",
            **wdecor,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.GenPollText(
            update_interval=0.1,
            func=vol,
            mouse_callbacks={
                "Button4": lazy.spawn("amixer set Master 5%+"),
                "Button5": lazy.spawn("amixer set Master 5%-"),
            },
            **wdecor,
        ),
        widget.Spacer(),
        widget.GroupBox(
            hide_unused=True,
            highlight_method="text",
            fontsize=18,
            disable_drag=True,
            **wdecor,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.TaskList(
            icon_size=24,
            parse_text=lambda _: "",
            highlight_method="text",
            txt_floating="󱂬 ",
            txt_maximized="󰏋 ",
            txt_minimized="󰖰 ",
        ),
        widget.Prompt(),
        widget.Net(
            interface="wlp1s0",
            format="{down:.0f}{down_suffix} ↓↑ {up:.0f}{up_suffix}",
            update_interval=2,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.GenPollText(
            func=batt,
            update_interval=1,
            **wdecor,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.Systray(
            padding=10,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.GenPollText(
            func=bright,
            update_interval=0.1,
            mouse_callbacks={
                "Button4": lazy.spawn("brightnessctl set +5%"),
                "Button5": lazy.spawn("brightnessctl set 5%-"),
            },
            **wdecor,
        ),
    ]


def misc():
    return [
        widget.Clock(
            format=" %H:%M ",
            **wdecor,
        ),
        widget.Spacer(),
        widget.GroupBox(
            hide_unused=True,
            highlight_method="text",
            fontsize=18,
            disable_drag=True,
            **wdecor,
        ),
        widget.Spacer(
            length=10,
        ),
        widget.TaskList(
            icon_size=24,
            parse_text=lambda _: "",
            highlight_method="text",
            txt_floating="󱂬 ",
            txt_maximized="󰏋 ",
            txt_minimized="󰖰 ",
        ),
    ]


widget_defaults = dict(
    font="Inter Variable Bold",
    fontsize=14,
)

lucid = "#00000000"

black = [
    "#0d0d0d",
    "#d3d3d3",
    # "#383838",
    # "#545454",
]

rangi = black

wdecor = {
    "background": rangi[0],
    "foreground": rangi[1],
    "decorations": [
        RectDecoration(use_widget_background=True, radius=12, filled=True, group=True),
    ],
    "padding": 6,
}


screens = [
    Screen(
        wallpaper="/mnt/sda2/Library/UnixImgs/arc.jpg",
        wallpaper_mode="stretch",
        top=bar.Bar(main(), 28, background=lucid, margin=[0, 8, 0, 8]),
    ),
    Screen(
        wallpaper="/mnt/sda2/Library/UnixImgs/arc.jpg",
        wallpaper_mode="stretch",
        top=bar.Bar(misc(), 28, background=lucid, margin=[0, 8, 0, 8]),
    ),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
floats_kept_above = True
cursor_warp = False
floating_layout = layout.Floating(
    border_width=0,
    float_rules=[
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),
        Match(wm_class="makebranch"),
        Match(wm_class="maketag"),
        Match(wm_class="ssh-askpass"),
        Match(title="branchdialog"),
        Match(title="pinentry"),
        Match(wm_class="arandr"),
        Match(wm_class="blueman-manager"),
        Match(wm_class="localsend"),
        Match(wm_class="firetools"),
        # Match(wm_class="iwgtk"),
        Match(wm_class="gufw.py"),
        Match(wm_class="wihotspot"),
        Match(wm_class="nm-connection-editor"),
        Match(wm_class="Thunar"),
    ],
)


auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True
auto_minimize = True
wl_input_rules = None
wl_xcursor_theme = None
wl_xcursor_size = 24

# if qtile.core.name == "x11":
#     term = "kitty"
# elif qtile.core.name == "wayland":
#     term = "wezterm"


@hook.subscribe.startup_once
def autostart():
    autostartScript = os.path.expanduser("~/.config/qtile/scripts/autostart.sh")
    monitorScript = os.path.expanduser("~/.config/qtile/scripts/monitors.sh")
    subprocess.run([autostartScript])
    subprocess.run([monitorScript])


wmname = "qtile"
