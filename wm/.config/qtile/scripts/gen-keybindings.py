#!/usr/bin/env python3
#  Qtile keybindings image generator - Dark Mode Edition  #

import getopt
import os
import sys
from typing import Any, Dict, List, Optional, Union

import cairocffi as cairo  # type: ignore
from cairocffi import Context, ImageSurface

this_dir = os.path.dirname(__file__)
base_dir = os.path.abspath(os.path.join(this_dir, ".."))
sys.path.insert(0, base_dir)

from libqtile.config import Key, KeyChord, Mouse
from libqtile.confreader import Config

BUTTON_NAME_Y: int = 65
BUTTON_NAME_X: int = 10

COMMAND_Y: int = 20
COMMAND_X: int = 10

LEGEND: List[str] = ["modifiers", "layout", "group", "window", "other"]

CUSTOM_KEYS: Dict[str, float] = {
    "Backspace": 2.0,
    "Tab": 1.5,
    "\\": 1.5,
    "Return": 2.45,
    "shift": 2.0,
    "space": 5.0,
}


class Button:
    def __init__(
        self, key: str, x: float, y: float, width: float, height: float
    ) -> None:
        self.key: str = key
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height


class Pos:
    WIDTH: int = 78
    HEIGHT: int = 70
    GAP: int = 5

    def __init__(self, x: float, y: float) -> None:
        self.x: float = x
        self.row_x: float = x
        self.y: float = y
        self.custom_width: Dict[str, float] = {}
        for i, val in CUSTOM_KEYS.items():
            self.custom_width[i] = val * self.WIDTH

    def get_pos(self, name: str) -> Button:
        width: float
        if name in self.custom_width:
            width = self.custom_width[name]
        else:
            width = float(self.WIDTH)

        info = Button(name, self.x, self.y, width, float(self.HEIGHT))

        self.x = self.x + self.GAP + width

        return info

    def skip_x(self, times: float = 1.0) -> None:
        self.x = self.x + self.GAP + times * self.WIDTH

    def next_row(self) -> None:
        self.x = self.row_x
        self.y = self.y + self.GAP + self.HEIGHT


class KInfo:
    NAME_MAP: Dict[str, str] = {
        "togroup": "to group",
        "toscreen": "to screen",
    }

    KEY_MAP: Dict[str, str] = {
        "grave": "`",
        "semicolon": ";",
        "slash": "/",
        "backslash": "\\",
        "comma": ",",
        "period": ".",
        "bracketleft": "[",
        "bracketright": "]",
        "quote": "'",
        "minus": "-",
        "equals": "=",
    }

    def __init__(self, key: Union[Key, KeyChord, Mouse]) -> None:
        key_name = getattr(key, "key", "")
        if not key_name:
            key_name = getattr(key, "button", "")

        if key_name in self.KEY_MAP:
            self.key: str = self.KEY_MAP[key_name]
        else:
            self.key = key_name
        self.command: str = self.get_command(key)
        self.scope: Optional[str] = self.get_scope(key)

    def get_command(self, key: Union[Key, KeyChord, Mouse]) -> str:
        if not isinstance(key, Mouse) and hasattr(key, "desc") and key.desc:
            return key.desc

        if isinstance(key, KeyChord):
            return ""

        if not hasattr(key, "commands") or not key.commands:
            return ""

        cmd = key.commands[0]
        command: str = cmd.name
        # Handle lazy.function
        if command == "function" and len(cmd.args) and hasattr(cmd.args[0], "__name__"):
            command = cmd.args[0].__name__
        # Handle lazy.widget
        elif len(cmd.selectors) and cmd.selectors[0][0] == "widget":
            widget_name = cmd.selectors[0][1]
            command = f"{widget_name} {command}"
        elif command in self.NAME_MAP:
            command = self.NAME_MAP[command]
        command = command.replace("_", " ")

        if len(cmd.args):
            if isinstance(cmd.args[0], str):
                command += " " + cmd.args[0]

        return command

    def get_scope(self, key: Union[Key, KeyChord, Mouse]) -> Optional[str]:
        if isinstance(key, KeyChord):
            return None

        if not hasattr(key, "commands") or not key.commands:
            return None

        selectors = key.commands[0].selectors
        if len(selectors):
            return selectors[0][0]
        return None


class MInfo(KInfo):
    def __init__(self, mouse: Mouse) -> None:
        super().__init__(mouse)


class KeyboardPNGFactory:
    def __init__(self, modifiers: str, keys: Dict[str, KInfo]) -> None:
        self.keys: Dict[str, KInfo] = keys
        self.modifiers: List[str] = modifiers.split("-")
        self.key_pos: Dict[str, Button] = self.calculate_pos(20, 140)

    def rgb_background(self, context: Context) -> None:
        """Pure OLED black background"""
        context.set_source_rgb(0.0, 0.0, 0.0)

    def rgb_text(self, context: Context) -> None:
        """Bright white text for maximum contrast"""
        context.set_source_rgb(0.95, 0.95, 0.95)

    def rgb_border(self, context: Context) -> None:
        """Medium gray borders for visibility"""
        context.set_source_rgb(0.35, 0.35, 0.35)

    def rgb_red(self, context: Context) -> None:
        """Vibrant red for modifiers - good OLED efficiency"""
        context.set_source_rgb(0.9, 0.2, 0.2)

    def rgb_green(self, context: Context) -> None:
        """Bright green for groups - OLED friendly"""
        context.set_source_rgb(0.2, 0.8, 0.3)

    def rgb_yellow(self, context: Context) -> None:
        """Bright amber/gold for windows"""
        context.set_source_rgb(1.0, 0.7, 0.0)

    def rgb_cyan(self, context: Context) -> None:
        """Bright cyan for layouts"""
        context.set_source_rgb(0.2, 0.8, 0.9)

    def rgb_violet(self, context: Context) -> None:
        """Bright magenta for other"""
        context.set_source_rgb(0.9, 0.3, 0.9)

    def calculate_pos(self, x: float, y: float) -> Dict[str, Button]:
        pos = Pos(x, y)

        key_pos: Dict[str, Button] = {}
        for c in "`1234567890-=":
            key_pos[c] = pos.get_pos(c)

        key_pos["Backspace"] = pos.get_pos("Backspace")
        pos.next_row()

        key_pos["Tab"] = pos.get_pos("Tab")
        for c in "qwertyuiop[]\\":
            key_pos[c] = pos.get_pos(c)
        pos.next_row()

        pos.skip_x(1.6)
        for c in "asdfghjkl;'":
            key_pos[c] = pos.get_pos(c)
        key_pos["Return"] = pos.get_pos("Return")
        pos.next_row()

        key_pos["shift"] = pos.get_pos("shift")
        for c in "zxcvbnm":
            key_pos[c] = pos.get_pos(c)
        key_pos["period"] = pos.get_pos("period")
        key_pos["comma"] = pos.get_pos("comma")
        key_pos["/"] = pos.get_pos("/")
        pos.next_row()

        key_pos["control"] = pos.get_pos("control")
        pos.skip_x()
        key_pos["mod4"] = pos.get_pos("mod4")
        key_pos["mod1"] = pos.get_pos("mod1")
        key_pos["space"] = pos.get_pos("space")
        key_pos["Print"] = pos.get_pos("Print")
        pos.skip_x(3)
        key_pos["Up"] = pos.get_pos("Up")

        pos.next_row()
        pos.skip_x(12.33)
        key_pos["Left"] = pos.get_pos("Left")
        key_pos["Down"] = pos.get_pos("Down")
        key_pos["Right"] = pos.get_pos("Right")

        pos.next_row()

        for legend in LEGEND:
            key_pos[legend] = pos.get_pos(legend)

        pos.skip_x(5)
        key_pos["Button1"] = pos.get_pos("Button1")
        key_pos["Button2"] = pos.get_pos("Button2")
        key_pos["Button3"] = pos.get_pos("Button3")

        pos.next_row()
        key_pos["FN_KEYS"] = pos.get_pos("FN_KEYS")

        return key_pos

    def render(self, filename: str) -> None:
        surface = ImageSurface(cairo.FORMAT_ARGB32, 1280, 800)
        context = Context(surface)

        # Set OLED black background
        with context:
            self.rgb_background(context)
            context.paint()

        # Set text color for header
        self.rgb_text(context)
        context.set_font_size(16)
        context.move_to(20, 100)

        if len([i for i in self.modifiers if i]):
            context.show_text("Modifiers: " + ", ".join(self.modifiers))
        else:
            context.show_text("No modifiers used.")

        for key_button in self.key_pos.values():
            if key_button.key in ["FN_KEYS"]:
                continue

            self.draw_button(
                context,
                key_button.key,
                key_button.x,
                key_button.y,
                key_button.width,
                key_button.height,
            )

        # draw functional
        fn = [i for i in self.keys.values() if i.key[:4] == "XF86"]
        if len(fn):
            fn_pos = self.key_pos["FN_KEYS"]
            x_pos = fn_pos.x
            for fn_key in fn:
                self.draw_button(
                    context, fn_key.key, x_pos, fn_pos.y, fn_pos.width, fn_pos.height
                )
                x_pos += Pos.GAP + Pos.WIDTH

        # draw mouse base
        context.rectangle(830, 660, 244, 90)
        self.rgb_border(context)
        context.stroke()
        context.set_font_size(28)
        self.rgb_text(context)
        context.move_to(900, 720)
        context.show_text("MOUSE")

        surface.write_to_png(filename)

    def draw_button(
        self,
        context: Context,
        key: str,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        fn = False
        if key[:4] == "XF86":
            fn = True

        if key in LEGEND:
            if key == "modifiers":
                self.rgb_red(context)
            elif key == "group":
                self.rgb_green(context)
            elif key == "layout":
                self.rgb_cyan(context)
            elif key == "window":
                self.rgb_yellow(context)
            else:
                self.rgb_violet(context)
            context.rectangle(x, y, width, height)
            context.fill()

        if key in self.modifiers:
            context.rectangle(x, y, width, height)
            self.rgb_red(context)
            context.fill()

        if key in self.keys:
            k = self.keys[key]
            context.rectangle(x, y, width, height)
            self.set_key_color(context, k)
            context.fill()

            self.show_multiline(context, x + COMMAND_X, y + COMMAND_Y, k)

        context.rectangle(x, y, width, height)
        self.rgb_border(context)
        context.stroke()

        if fn:
            key = key[4:]
            context.set_font_size(10)
        else:
            context.set_font_size(14)

        self.rgb_text(context)
        context.move_to(x + BUTTON_NAME_X, y + BUTTON_NAME_Y)
        context.show_text(self.translate(key))

    def show_multiline(self, context: Context, x: float, y: float, key: KInfo) -> None:
        """Cairo doesn't support multiline. Added with word wrapping."""
        c_width: float = 14.0
        if key.key in CUSTOM_KEYS:
            c_width *= CUSTOM_KEYS[key.key]

        context.set_font_size(10)
        self.rgb_text(context)
        context.move_to(x, y)
        words = key.command.split(" ")
        words.reverse()
        printable: str = ""
        last_word: Optional[str] = None
        if words:
            printable = last_word = words.pop()
        while len(words):
            last_word = words.pop()
            if len(printable + " " + last_word) < c_width:
                printable += " " + last_word
                continue

            context.show_text(printable)
            y += 10
            context.move_to(x, y)
            printable = last_word

        if last_word is not None:
            context.show_text(printable)

    def set_key_color(self, context: Context, key: KInfo) -> None:
        if key.scope == "group":
            self.rgb_green(context)
        elif key.scope == "layout":
            self.rgb_cyan(context)
        elif key.scope == "window":
            self.rgb_yellow(context)
        else:
            self.rgb_violet(context)

    def translate(self, text: str) -> str:
        dictionary: Dict[str, str] = {
            "period": ",",
            "comma": ".",
            "Left": "Left",
            "Down": "Down",
            "Right": "Right",
            "Up": "Up",
            "AudioRaiseVolume": "Volume up",
            "AudioLowerVolume": "Volume down",
            "AudioMute": "Audio mute",
            "AudioMicMute": "Mic mute",
            "MonBrightnessUp": "Brightness up",
            "MonBrightnessDown": "Brightness down",
        }

        if text not in dictionary:
            return text

        return dictionary[text]


def get_kb_map(config_path: Optional[str] = None) -> Dict[str, Dict[str, KInfo]]:
    c: Any = Config(config_path)  # type: ignore
    if config_path:
        c.load()

    all_keys: List[Union[Key, KeyChord]] = []
    key: Union[Key, KeyChord]
    for key in c.keys:
        if isinstance(key, KeyChord):
            key.desc = "Enter chord"
            all_keys.append(key)

            sub_key: Union[Key, KeyChord]
            for sub_key in key.submappings:
                prefix = f"Chord ({key.key}): "
                current_desc = ""
                if hasattr(sub_key, "desc") and sub_key.desc:
                    current_desc = sub_key.desc
                else:
                    if (
                        not isinstance(sub_key, KeyChord)
                        and hasattr(sub_key, "commands")
                        and sub_key.commands
                    ):
                        cmd = sub_key.commands[0]
                        command = cmd.name.replace("_", " ")
                        if len(cmd.args) and isinstance(cmd.args[0], str):
                            command += f" {cmd.args[0]}"
                        current_desc = command
                sub_key.desc = prefix + current_desc
                all_keys.append(sub_key)
        else:
            all_keys.append(key)

    kb_map: Dict[str, Dict[str, KInfo]] = {}
    key2: Union[Key, KeyChord]
    for key2 in all_keys:
        mod = "-".join(key2.modifiers)
        if mod not in kb_map:
            kb_map[mod] = {}

        info = KInfo(key2)
        kb_map[mod][info.key] = info

    mouse: Mouse
    for mouse in c.mouse:
        mod = "-".join(mouse.modifiers)
        if mod not in kb_map:
            kb_map[mod] = {}

        info = MInfo(mouse)
        kb_map[mod][info.key] = info

    return kb_map


help_doc: str = """
usage: ./gen-keybindings.py [-h] [-c CONFIGFILE] [-o OUTPUT_DIR]

Qtile keybindings image generator (Dark Mode Edition)

optional arguments:
    -h, --help          show this help message and exit
    -c CONFIGFILE, --config CONFIGFILE
                        use specified configuration file. If no presented
                        default will be used
    -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        set directory to export all images to
"""

if __name__ == "__main__":
    config_path: Optional[str] = None
    output_dir: str = ""
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "hc:o:", ["help=", "config=", "output-dir="]
        )

    except getopt.GetoptError:
        print(help_doc)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(help_doc)
            sys.exit()
        elif opt in ("-c", "--config"):
            config_path = arg
        elif opt in ("-o", "--output-dir"):
            output_dir = arg

    kb_map = get_kb_map(config_path)
    for modifier, keys in kb_map.items():
        if not modifier:
            filename = "no_modifier.png"
        else:
            filename = f"{modifier}.png"

        output_file = os.path.abspath(os.path.join(output_dir, filename))
        f = KeyboardPNGFactory(modifier, keys)
        f.render(output_file)
