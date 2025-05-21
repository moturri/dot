from utils import cached, fmt, run_command

DEFAULT_SINK = "@DEFAULT_AUDIO_SINK@"
DEFAULT_SOURCE = "@DEFAULT_AUDIO_SOURCE@"
VOLUME_STEP = 5


class AudioDevice:
    def __init__(self, device_type="sink", device_id=None):
        self.device_type = device_type
        self.device_id = device_id or (
            DEFAULT_SOURCE if device_type == "source" else DEFAULT_SINK
        )
        self.state = {"volume": 0, "muted": True}
        self.is_mic = device_type == "source"
        self.muted_icon = "󰍭" if self.is_mic else "󰝟"
        self.icons = [
            (70, "󰍬" if self.is_mic else "󰕾", "salmon"),
            (40, "󰍬" if self.is_mic else "󰖀", "mediumpurple"),
            (15, "󰍬" if self.is_mic else "󰕿", "springgreen"),
            (0, "󰍬" if self.is_mic else "󰕿", "palegreen"),
        ]

    def update_state(self):
        output = run_command(["wpctl", "get-volume", self.device_id], get_output=True)
        if output:
            parts = output.split()
            if len(parts) >= 2:
                self.state["volume"] = int(float(parts[1]) * 100)
                self.state["muted"] = "[MUTED]" in output

    def format(self):
        self.update_state()
        if self.state["muted"]:
            return fmt(self.muted_icon, self.state["volume"], "dimgrey")
        for level, icon, color in self.icons:
            if self.state["volume"] >= level:
                return fmt(icon, self.state["volume"], color)
        return fmt(self.icons[-1][1], self.state["volume"], self.icons[-1][2])

    def set_volume(self, level: float):
        level = max(0.0, min(level, 1.0))
        run_command(["wpctl", "set-volume", self.device_id, f"{level:.2f}"])
        self.state["volume"] = int(level * 100)
        self.state["muted"] = False if level > 0 else self.state["muted"]
        (mic if self.is_mic else vol)(force=True)

    def volume_up(self, step=VOLUME_STEP):
        self.set_volume(min(100, self.state["volume"] + step) / 100)

    def volume_down(self, step=VOLUME_STEP):
        self.set_volume(max(0, self.state["volume"] - step) / 100)

    def volume_set(self, level: int):
        self.set_volume(max(0, min(level, 100)) / 100)

    def toggle_mute(self):
        run_command(["wpctl", "set-mute", self.device_id, "toggle"])
        self.update_state()
        (mic if self.is_mic else vol)(force=True)


speaker = AudioDevice("sink")
microphone = AudioDevice("source")


@cached(10)
def vol() -> str:
    return speaker.format()


@cached(10)
def mic() -> str:
    return microphone.format()


def vol_up(qtile=None):
    speaker.volume_up()


def vol_down(qtile=None):
    speaker.volume_down()


def vol_set(level: int):
    speaker.volume_set(level)


def vol_mute(qtile=None):
    speaker.toggle_mute()


def mic_up(qtile=None):
    microphone.volume_up()


def mic_down(qtile=None):
    microphone.volume_down()


def mic_set(level: int):
    microphone.volume_set(level)


def mic_mute(qtile=None):
    microphone.toggle_mute()
