from typing import List, Tuple

from utils import cached, fmt, run_command

VOLUME_STEP = 5


class AudioDevice:
    def __init__(self, device_type: str = "sink"):
        self.device_id = (
            "@DEFAULT_AUDIO_SOURCE@"
            if device_type == "source"
            else "@DEFAULT_AUDIO_SINK@"
        )
        self.is_mic = device_type == "source"
        self.muted_icon = "󰍭" if self.is_mic else "󰝟"
        self.volume = 0
        self.muted = True

        self.icons: List[Tuple[int, str, str]] = [
            (70, "󰍬" if self.is_mic else "󰕾", "salmon"),
            (40, "󰍬" if self.is_mic else "󰖀", "mediumpurple"),
            (0, "󰍬" if self.is_mic else "󰕿", "springgreen"),
        ]

    def update(self) -> None:
        output = run_command(["wpctl", "get-volume", self.device_id], True)
        if output:
            parts = output.split()
            try:
                self.volume = int(float(parts[1]) * 100)
                self.muted = "[MUTED]" in output
            except (IndexError, ValueError):
                pass

    def format(self) -> str:
        self.update()
        if self.muted:
            return fmt(self.muted_icon, self.volume, "dimgrey")
        for level, icon, color in self.icons:
            if self.volume >= level:
                return fmt(icon, self.volume, color)
        return fmt(self.icons[-1][1], self.volume, self.icons[-1][2])

    def set_volume(self, level: float) -> None:
        level = max(0.0, min(1.0, level))
        run_command(["wpctl", "set-volume", self.device_id, f"{level:.2f}"])
        self.update()

    def volume_up(self, step: int = VOLUME_STEP) -> None:
        self.set_volume((self.volume + step) / 100)

    def volume_down(self, step: int = VOLUME_STEP) -> None:
        self.set_volume((self.volume - step) / 100)

    def toggle_mute(self) -> None:
        run_command(["wpctl", "set-mute", self.device_id, "toggle"])
        self.update()


# Qtile Callbacks
speaker = AudioDevice("sink")
microphone = AudioDevice("source")


@cached(0.5)
def vol() -> str:
    return speaker.format()


@cached(0.5)
def mic() -> str:
    return microphone.format()


def vol_up(qtile=None):
    speaker.volume_up()


def vol_down(qtile=None):
    speaker.volume_down()


def vol_mute(qtile=None):
    speaker.toggle_mute()


def vol_set(level: int):
    speaker.set_volume(max(0, min(level, 100)) / 100)


def mic_up(qtile=None):
    microphone.volume_up()


def mic_down(qtile=None):
    microphone.volume_down()


def mic_mute(qtile=None):
    microphone.toggle_mute()


def mic_set(level: int):
    microphone.set_volume(max(0, min(level, 100)) / 100)
