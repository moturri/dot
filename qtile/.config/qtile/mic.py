import subprocess

from utils import cached, fmt

DEFAULT_SOURCE = "@DEFAULT_AUDIO_SOURCE@"

MUTED_ICON = "󰍭"
ACTIVE_ICON = "󰍬"

MIC_VOLUME_STATES = [
    (70, "salmon"),
    (40, "mediumpurple"),
    (15, "springgreen"),
    (0, "palegreen"),
]

mic_state = {"volume": 0, "muted": True}


def update_mic_state():
    try:
        output = (
            subprocess.check_output(
                ["wpctl", "get-volume", DEFAULT_SOURCE],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )

        parts = output.split()
        volume = int(float(parts[1]) * 100)
        muted = "[MUTED]" in output

        mic_state["volume"] = volume
        mic_state["muted"] = muted
    except Exception as e:
        print(f"[mic] update error: {e}")
        mic_state["volume"] = 0
        mic_state["muted"] = True


@cached(10)
def mic() -> str:
    update_mic_state()

    icon = MUTED_ICON if mic_state["muted"] else ACTIVE_ICON
    color = (
        "dimgrey"
        if mic_state["muted"]
        else next(
            (
                col
                for level, col in sorted(MIC_VOLUME_STATES, reverse=True)
                if mic_state["volume"] >= level
            ),
            MIC_VOLUME_STATES[-1][1],
        )
    )
    return fmt(icon, mic_state["volume"], color)


def set_mic_volume(level: float):
    try:
        subprocess.run(
            ["wpctl", "set-volume", DEFAULT_SOURCE, f"{level:.2f}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        new_volume = int(level * 100)
        if mic_state["volume"] != new_volume:
            mic_state["volume"] = new_volume
            if level > 0:
                mic_state["muted"] = False
            mic(force=True)
    except Exception as e:
        print(f"[mic_set] Error: {e}")


def mic_up(qtile=None, step=2):
    new_level = min(100, mic_state["volume"] + step) / 100
    set_mic_volume(new_level)


def mic_down(qtile=None, step=2):
    new_level = max(0, mic_state["volume"] - step) / 100
    set_mic_volume(new_level)


def mic_set(level: int):
    set_mic_volume(max(0, min(level, 100)) / 100)


def mic_mute(qtile=None):
    try:
        subprocess.run(
            ["wpctl", "set-mute", DEFAULT_SOURCE, "toggle"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        mic_state["muted"] = not mic_state["muted"]
        mic(force=True)
    except Exception as e:
        print(f"[mic_mute] Error: {e}")
