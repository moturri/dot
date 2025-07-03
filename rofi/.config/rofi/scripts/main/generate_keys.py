import sys

sys.path.append("/home/m/.config/qtile/")

from keys import keys
from libqtile.config import Key, KeyChord

MODIFIER_ICONS = {
    "mod4": " ",
    "shift": "⇧ ",
    "control": "Ctrl",
    "mod1": "Alt",
}


def format_modifier(mod: str) -> str:
    return MODIFIER_ICONS.get(mod, mod.capitalize())


def describe_lazy(cmds):
    desc = []
    for cmd in cmds:
        if cmd.name == "spawn":
            desc.append(f"Run '{cmd.args[0]}'")
        elif cmd.name == "layout":
            desc.append(f"Layout.{cmd.attr}()")
        elif cmd.name == "window":
            desc.append(f"Window.{cmd.attr}()")
        elif cmd.name == "group":
            desc.append(f"Group.{cmd.attr}()")
        elif cmd.name == "widget":
            desc.append(f"Widget: {cmd.attr}")
        else:
            desc.append(cmd.name)
    return ", ".join(desc)


def format_keybinding(key_obj, display_string, max_len=30, indent=0):
    desc = describe_lazy(key_obj.commands)

    # Adjust spacing with padding
    combo = display_string.ljust(max_len)
    spacing = " " * indent
    return f"{spacing}{combo}  {desc}"


def collect_keybindings():
    lines = []
    max_len = 0
    flat_keys = []

    # Flatten keys and compute max_len
    for key in keys:
        if isinstance(key, Key):
            mods = "+".join(format_modifier(mod) for mod in key.modifiers)
            combo = f"{mods}+{key.key}" if mods else key.key
            flat_keys.append((key, combo, combo))  # (key_obj, display_string, sort_string)
            max_len = max(max_len, len(combo))
        elif isinstance(key, KeyChord):
            chord_mods = "+".join(format_modifier(mod) for mod in key.modifiers)
            chord_combo_prefix = f"{chord_mods}+{key.key}" if chord_mods else key.key
            max_len = max(max_len, len(chord_combo_prefix))
            for subkey in key.submappings:
                sub_mods = "+".join(format_modifier(mod) for mod in subkey.modifiers)
                sub_combo = f"{sub_mods}+{subkey.key}" if sub_mods else subkey.key
                display_string = f"{chord_combo_prefix} → {sub_combo}"
                sort_string = f"{chord_combo_prefix}{sub_combo}" # For sorting, remove the arrow
                flat_keys.append((subkey, display_string, sort_string))
                max_len = max(max_len, len(display_string))

    # Format and sort
    for key_obj, display_string, sort_string in sorted(flat_keys, key=lambda x: x[2]):
        lines.append(format_keybinding(key_obj, display_string, max_len))

    return "\n".join(lines)


# Output
if __name__ == "__main__":
    print(collect_keybindings())
