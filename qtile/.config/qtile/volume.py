import subprocess

from utils import cached, fmt

DEFAULT_SINK = "@DEFAULT_AUDIO_SINK@"

state = {"volume": 0, "muted": True}


def update_state():
    try:
        output = subprocess.check_output(
            ["wpctl", "get-volume", DEFAULT_SINK], stderr=subprocess.DEVNULL
        ).decode()

        parts = output.split()
        volume = int(float(parts[1]) * 100)
        muted = "[MUTED]" in output

        state["volume"] = volume
        state["muted"] = muted
    except Exception as e:
        print(f"[vol] Error: {e}")
        state["volume"] = 0
        state["muted"] = True


@cached(10)
def vol() -> str:
    update_state()
    icon = "󰝟" if state["muted"] else "󰕿"
    color = "dimgrey" if state["muted"] else "springgreen"

    if not state["muted"]:
        if state["volume"] >= 70:
            icon, color = "󰕾", "salmon"
        elif state["volume"] >= 40:
            icon, color = "󰖀", "mediumpurple"
        elif state["volume"] >= 15:
            icon, color = "󰕿", "springgreen"
        else:
            icon, color = "󰕿", "palegreen"

    return fmt(icon, state["volume"], color)


def set_volume(level: float):
    try:
        subprocess.run(
            ["wpctl", "set-volume", DEFAULT_SINK, f"{level:.2f}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        state["volume"] = int(level * 100)
        if level > 0:
            state["muted"] = False
    except Exception as e:
        print(f"[vol_set] Error: {e}")
    vol(force=True)


def vol_up(qtile=None, step=2):
    new_level = min(100, state["volume"] + step) / 100
    set_volume(new_level)


def vol_down(qtile=None, step=2):
    new_level = max(0, state["volume"] - step) / 100
    set_volume(new_level)


def vol_set(level: int):
    set_volume(max(0, min(level, 100)) / 100)


def vol_mute(qtile=None):
    try:
        subprocess.run(
            ["wpctl", "set-mute", DEFAULT_SINK, "toggle"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        update_state()
    except Exception as e:
        print(f"[vol_mute] Error: {e}")
    vol(force=True)
