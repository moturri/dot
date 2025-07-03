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


def format_keybinding(key, max_len=30, indent=0):
    mods = "+".join(format_modifier(mod) for mod in key.modifiers)
    key_combo = f"{mods}+{key.key}" if mods else key.key
    desc = describe_lazy(key.commands)

    # Adjust spacing with padding
    combo = key_combo.ljust(max_len)
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
            flat_keys.append((key, combo))
            max_len = max(max_len, len(combo))
        elif isinstance(key, KeyChord):
            chord_combo = (
                "+".join(format_modifier(mod) for mod in key.modifiers) + f"+{key.key}"
            )
            max_len = max(max_len, len(chord_combo))
            for subkey in key.submappings:
                mods = "+".join(format_modifier(mod) for mod in subkey.modifiers)
                combo = f"{mods}+{subkey.key}" if mods else subkey.key
                full_combo = f"{chord_combo} → {combo}"
                flat_keys.append((subkey, full_combo))
                max_len = max(max_len, len(full_combo))

    # Format and sort
    for key, combo in sorted(flat_keys, key=lambda x: x[1]):
        lines.append(format_keybinding(key, max_len))

    return "\n".join(lines)


# Output
if __name__ == "__main__":
    print(collect_keybindings())
