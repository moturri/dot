import logging

from utils import cached, fmt, run_command

# Create a logger for audio widgets
logger = logging.getLogger(__name__)

# Default device names
DEFAULT_SINK = "@DEFAULT_AUDIO_SINK@"
DEFAULT_SOURCE = "@DEFAULT_AUDIO_SOURCE@"

# Global volume step in percent
VOLUME_STEP = 5


class AudioDevice:
    """
    A class to manage audio devices (sink or source) with shared functionality.
    """

    def __init__(self, device_type="sink", device_id=None):
        self.device_type = device_type
        self.device_id = device_id or (
            DEFAULT_SOURCE if device_type == "source" else DEFAULT_SINK
        )
        self.state = {"volume": 0, "muted": True}
        self.is_mic = device_type == "source"

        # Define icon states based on device type
        if self.is_mic:
            self.muted_icon = "󰍭"
            self.icons = [
                (70, "󰍬", "salmon"),
                (40, "󰍬", "mediumpurple"),
                (15, "󰍬", "springgreen"),
                (0, "󰍬", "palegreen"),
            ]
        else:
            self.muted_icon = "󰝟"
            self.icons = [
                (70, "󰕾", "salmon"),
                (40, "󰖀", "mediumpurple"),
                (15, "󰕿", "springgreen"),
                (0, "󰕿", "palegreen"),
            ]

    def update_state(self):
        """Update volume and mute state."""
        try:
            output = run_command(
                ["wpctl", "get-volume", self.device_id], get_output=True
            )
            if not output:
                raise ValueError("Empty output")

            parts = output.split()
            if len(parts) < 2:
                raise ValueError(f"Malformed output: '{output}'")

            self.state["volume"] = int(float(parts[1]) * 100)
            self.state["muted"] = "[MUTED]" in output
        except Exception as e:
            logger.error(f"[{self.device_type}] Error reading volume: {e}")
            self.state = {"volume": 0, "muted": True}

    def format(self):
        """Return Qtile-formatted markup string."""
        self.update_state()

        if self.state["muted"]:
            return fmt(self.muted_icon, self.state["volume"], "dimgrey")

        for level, icon, color in self.icons:
            if self.state["volume"] >= level:
                return fmt(icon, self.state["volume"], color)

        return fmt(self.icons[-1][1], self.state["volume"], self.icons[-1][2])

    def set_volume(self, level: float):
        """Set volume from 0.0 to 1.0"""
        try:
            run_command(["wpctl", "set-volume", self.device_id, f"{level:.2f}"])
            self.state["volume"] = int(level * 100)
            if level > 0:
                self.state["muted"] = False
        except Exception as e:
            logger.error(f"[{self.device_type}_set_volume] {e}")
        self._refresh_widget()

    def volume_up(self, step=VOLUME_STEP):
        new_level = min(100, self.state["volume"] + step) / 100
        self.set_volume(new_level)

    def volume_down(self, step=VOLUME_STEP):
        new_level = max(0, self.state["volume"] - step) / 100
        self.set_volume(new_level)

    def volume_set(self, level: int):
        self.set_volume(max(0, min(level, 100)) / 100)

    def toggle_mute(self):
        try:
            run_command(["wpctl", "set-mute", self.device_id, "toggle"])
            self.update_state()
        except Exception as e:
            logger.error(f"[{self.device_type}_mute] {e}")
        self._refresh_widget()

    def _refresh_widget(self):
        if self.is_mic:
            mic(force=True)
        else:
            vol(force=True)


# === Instances ===
speaker = AudioDevice("sink")
microphone = AudioDevice("source")


# === Cached widget strings ===
@cached(10)
def vol() -> str:
    return speaker.format()


@cached(10)
def mic() -> str:
    return microphone.format()


# === Optional control shortcuts (e.g. key bindings) ===
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

