import importlib.util
import sys
from typing import Any, List, Optional, Tuple, cast

from libqtile.config import Key, KeyChord
from libqtile.lazy import LazyCall

sys.path.append("/home/m/.config/qtile/")

MODIFIER_ICONS = {
    "mod4": " ",
    "shift": "⇧ ",
    "control": "Ctrl",
    "mod1": "Alt",
}


def format_modifier(mod: str) -> str:
    return MODIFIER_ICONS.get(mod, mod.capitalize())


def describe_lazy(commands: List[LazyCall], fallback_desc: Optional[str] = None) -> str:
    if not commands:
        return fallback_desc or "No description"

    descs: List[str] = []
    for cmd in commands:
        try:
            name = getattr(cmd, "name", None)
            attr = getattr(cmd, "attr", "")
            if name == "spawn":
                if hasattr(cmd, "args") and cmd.args:
                    descs.append(f"Run: {cmd.args[0]}")
                else:
                    descs.append("Run shell command")
            elif name:
                if attr:
                    descs.append(f"{name}.{attr}()")
                else:
                    descs.append(name)
            else:
                descs.append(str(cmd))
        except Exception:
            descs.append(str(cmd))
    return ", ".join(descs)


def format_keybinding(key_obj: Key, display_string: str, pad_len: int) -> str:
    desc = describe_lazy(list(key_obj.commands))
    combo = display_string.ljust(pad_len)
    return f"{combo} : {desc}"


def collect_keybindings() -> str:
    # Dynamically import keys.py safely
    spec = importlib.util.spec_from_file_location(
        "keys", "/home/m/.config/qtile/keys.py"
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("Failed to import keys.py")

    keys_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(keys_module)

    keys: List[Any] = getattr(keys_module, "keys", [])

    bindings: List[Tuple[Key, str, str]] = []
    pad_len = 0

    for key in keys:
        if isinstance(key, Key):
            mods = "+".join(format_modifier(m) for m in key.modifiers)
            key_str = str(key.key)
            combo = f"{mods}+{key_str}" if mods else key_str
            bindings.append((key, combo, combo))
            pad_len = max(pad_len, len(combo))

        elif isinstance(key, KeyChord):
            chord_mods = "+".join(format_modifier(m) for m in key.modifiers)
            chord_prefix = (
                f"{chord_mods}+{str(key.key)}" if chord_mods else str(key.key)
            )
            pad_len = max(pad_len, len(chord_prefix))

            # Explicitly cast to List[Key] for type safety
            submap = cast(List[Key], getattr(key, "submappings", []))
            for subkey in submap:
                if isinstance(subkey, Key):
                    sub_mods = "+".join(format_modifier(m) for m in subkey.modifiers)
                    sub_combo = (
                        f"{sub_mods}+{str(subkey.key)}" if sub_mods else str(subkey.key)
                    )
                    display = f"{chord_prefix} → {sub_combo}"
                    sort_key = f"{chord_prefix}.{sub_combo}"
                    bindings.append((subkey, display, sort_key))
                    pad_len = max(pad_len, len(display))

    bindings.sort(key=lambda x: x[2])
    lines = [format_keybinding(k, d, pad_len) for k, d, _ in bindings]
    return "\n".join(lines)


if __name__ == "__main__":
    print(collect_keybindings())
