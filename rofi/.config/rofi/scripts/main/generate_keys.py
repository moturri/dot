import sys
sys.path.append('/home/m/.config/qtile/')
from keys import keys  # Adjust this path if needed
from libqtile.config import Key, KeyChord


def format_modifier(mod: str) -> str:
    return {
        "mod4": "",  # Windows/Super
        "shift": "󰘶",  # Shift symbol
        "control": "Ctrl",
        "mod1": "Alt",  # Alt key
    }.get(mod, mod)


def format_keybinding(key, max_len):
    mods = "+".join(format_modifier(mod) for mod in key.modifiers)
    key_str = f"{mods}+{key.key}"
    return f"{key_str:<{max_len}} → {describe_lazy(key.commands)}"


def describe_lazy(cmds):
    desc = []
    for cmd in cmds:
        if cmd.name == "spawn":
            desc.append(f"Run: {cmd.args[0]}")
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


def collect_keybindings():
    bindings = []
    for key in keys:
        if isinstance(key, Key):
            mods = "+".join(format_modifier(mod) for mod in key.modifiers)
            key_str = f"{mods}+{key.key}"
            bindings.append((key, key_str))
        elif isinstance(key, KeyChord):
            chord_mods = "+".join(format_modifier(mod) for mod in key.modifiers)
            chord = f"{chord_mods}+{key.key}"
            for subkey in key.submappings:
                submods = "+".join(format_modifier(mod) for mod in subkey.modifiers)
                full_key_str = (
                    f"{chord} then {submods}+{subkey.key}"
                    if submods
                    else f"{chord} then {subkey.key}"
                )
                bindings.append((subkey, full_key_str))
    return bindings


def main():
    keybindings_raw = collect_keybindings()
    max_len = 0
    for key, _ in keybindings_raw:
        mods = "+".join(format_modifier(mod) for mod in key.modifiers)
        key_str = f"{mods}+{key.key}"
        if len(key_str) > max_len:
            max_len = len(key_str)

    keybindings = []
    for key, key_str in keybindings_raw:
        keybindings.append(f"{key_str:<{max_len}} → {describe_lazy(key.commands)}")

    for line in sorted(keybindings):
        print(line)


if __name__ == "__main__":
    main()
