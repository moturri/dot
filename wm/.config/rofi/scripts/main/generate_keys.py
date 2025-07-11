import sys
from typing import List, Optional, Tuple

sys.path.append("/home/m/.config/qtile/")

from libqtile.config import Key, KeyChord
from libqtile.lazy import LazyCall

MODIFIER_ICONS = {
    "mod4": " ",
    "shift": "⇧ ",
    "control": "Ctrl",
    "mod1": "Alt",
}


def format_modifier(mod: str) -> str:
    return MODIFIER_ICONS.get(mod, mod.capitalize())


def describe_lazy(
    commands: List[LazyCall], fallback_desc: Optional[str] = None
) -> str:
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


def format_keybinding(key_obj: Key, display_string: str, max_len: int = 30) -> str:
    desc = describe_lazy(list(key_obj.commands))
    combo = display_string.ljust(max_len)
    return f"{combo}: {desc}"


def collect_keybindings() -> str:
    from keys import keys  # type: ignore

    lines: List[str] = []
    max_len = 0
    flat_keys: List[Tuple[Key, str, str]] = []

    for key in keys:
        if isinstance(key, Key):
            mods = "+".join(format_modifier(mod) for mod in key.modifiers)
            key_str = str(key.key)
            combo = f"{mods}+{key_str}" if mods else key_str
            flat_keys.append((key, combo, combo))
            max_len = max(max_len, len(combo))
        elif isinstance(key, KeyChord):
            chord_mods = "+".join(format_modifier(mod) for mod in key.modifiers)
            key_str = str(key.key)
            chord_combo_prefix = f"{chord_mods}+{key_str}" if chord_mods else key_str
            max_len = max(max_len, len(chord_combo_prefix))
            for subkey in key.submappings:
                if isinstance(subkey, Key):
                    sub_mods = "+".join(
                        format_modifier(mod) for mod in subkey.modifiers
                    )
                    sub_combo = f"{sub_mods}+{subkey.key}" if sub_mods else subkey.key
                    display_string = f"{chord_combo_prefix} → {sub_combo}"
                    sort_string = f"{chord_combo_prefix}{sub_combo}"
                    flat_keys.append((subkey, display_string, sort_string))
                    max_len = max(max_len, len(display_string))

    # Sort keys by combo string
    flat_keys.sort(key=lambda x: x[2])

    for key_obj, display_string, _ in flat_keys:
        if key_obj.commands:
            lines.append(format_keybinding(key_obj, display_string, max_len))

    return "\n".join(lines)


if __name__ == "__main__":
    print(collect_keybindings())
