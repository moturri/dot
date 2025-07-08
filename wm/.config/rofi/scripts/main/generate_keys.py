import sys

sys.path.append("/home/m/.config/qtile/")


MODIFIER_ICONS = {
    "mod4": " ",
    "shift": "⇧ ",
    "control": "Ctrl",
    "mod1": "Alt",
}


def format_modifier(mod: str) -> str:
    return MODIFIER_ICONS.get(mod, mod.capitalize())


def describe_lazy(commands, fallback_desc=None):
    if not commands:
        return fallback_desc or "No description"

    descriptions = []
    for cmd in commands:
        try:
            name = getattr(cmd, "name", None)
            attr = getattr(cmd, "attr", "")
            if name == "spawn":
                if hasattr(cmd, "args") and cmd.args:
                    descriptions.append(f"Run '{cmd.args[0]}'")
                else:
                    descriptions.append("Run command")
            elif name:
                if attr:
                    descriptions.append(f"{name.capitalize()}.{attr}()")
                else:
                    descriptions.append(f"{name.capitalize()}")
            else:
                descriptions.append(str(cmd))
        except Exception:
            descriptions.append(str(cmd))
    return ", ".join(descriptions)


def format_keybinding(key_obj, display_string, max_len=30):
    desc = describe_lazy(key_obj.commands)
    combo = display_string.ljust(max_len)
    return f"{combo}: {desc}"


def collect_keybindings():
    from keys import keys
    from libqtile.config import Key, KeyChord

    lines = []
    max_len = 0
    flat_keys = []

    for key in keys:
        if isinstance(key, Key):
            mods = "+".join(format_modifier(mod) for mod in key.modifiers)
            combo = f"{mods}+{key.key}" if mods else key.key
            flat_keys.append((key, combo, combo))
            max_len = max(max_len, len(combo))
        elif isinstance(key, KeyChord):
            chord_mods = "+".join(format_modifier(mod) for mod in key.modifiers)
            chord_combo_prefix = f"{chord_mods}+{key.key}" if chord_mods else key.key
            max_len = max(max_len, len(chord_combo_prefix))
            for subkey in key.submappings:
                sub_mods = "+".join(format_modifier(mod) for mod in subkey.modifiers)
                sub_combo = f"{sub_mods}+{subkey.key}" if sub_mods else subkey.key
                display_string = f"{chord_combo_prefix} → {sub_combo}"
                sort_string = f"{chord_combo_prefix}{sub_combo}"
                flat_keys.append((subkey, display_string, sort_string))
                max_len = max(max_len, len(display_string))

    # Sort keys by combo string
    flat_keys.sort(key=lambda x: x[2])

    for key_obj, display_string, _ in flat_keys:
        lines.append(format_keybinding(key_obj, display_string, max_len))

    return "\n".join(lines)


if __name__ == "__main__":
    print(collect_keybindings())
