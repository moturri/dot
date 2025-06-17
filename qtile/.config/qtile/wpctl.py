import logging
import os
import re
import subprocess
from typing import Any, List, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText

logger = logging.getLogger(__name__)


class AudioWidget(GenPollText):  # type: ignore
    """Minimal PipeWire audio widget using wpctl."""

    _LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (70, "salmon", "󰕾"),
        (40, "mediumpurple", "󰖀"),
        (0, "palegreen", "󰕿"),
    )
    _MUTED: Tuple[str, str] = ("grey", "󰝟")

    _REGEX_VOLUME = re.compile(r"\d+(\.\d+)?")
    _REGEX_MUTED = re.compile(r"\[MUTED\]")

    def __init__(
        self,
        device: str = "@DEFAULT_AUDIO_SINK@",
        step: int = 5,
        max_volume: int = 100,
        update_interval: float = 60.0,
        **config: Any,
    ) -> None:
        self.device = device
        self.step = max(1, min(step, 25))
        self.max_volume = max(50, min(max_volume, 150))
        self._env = {"LC_ALL": "C.UTF-8", **os.environ}
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _run(self, args: List[str]) -> str:
        try:
            return subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=0.5,
                check=True,
                env=self._env,
            ).stdout.strip()
        except subprocess.SubprocessError as e:
            logger.warning("wpctl command failed: %s", e)
            return ""

    def _get_state(self) -> Tuple[int, bool]:
        output = self._run(["wpctl", "get-volume", self.device])
        match = self._REGEX_VOLUME.search(output)
        vol = round(float(match.group()) * 100) if match else 0
        muted = bool(self._REGEX_MUTED.search(output))
        return vol, muted

    def _icon_color(self, vol: int, muted: bool) -> Tuple[str, str]:
        if muted:
            return self._MUTED
        for threshold, color, icon in reversed(self._LEVELS):
            if vol >= threshold:
                return color, icon
        return self._LEVELS[-1][1], self._LEVELS[-1][2]

    def _poll(self) -> str:
        try:
            vol, muted = self._get_state()
        except Exception as e:
            logger.error("Audio state error: %s", e)
            return '<span foreground="grey">󰖁  N/A</span>'
        color, icon = self._icon_color(vol, muted)
        vol_str = f"{vol}%!" if vol > 100 else f"{vol}%"
        return f'<span foreground="{color}">{icon}  {vol_str}</span>'

    def _set_volume(self, target: int) -> None:
        val = max(0, min(target, self.max_volume))
        self._run(["wpctl", "set-volume", self.device, f"{val}%"])
        self.force_update()

    @expose_command()
    def volume_up(self) -> None:
        vol, _ = self._get_state()
        self._set_volume(vol + self.step)

    @expose_command()
    def volume_down(self) -> None:
        vol, _ = self._get_state()
        self._set_volume(vol - self.step)

    @expose_command()
    def toggle_mute(self) -> None:
        self._run(["wpctl", "set-mute", self.device, "toggle"])
        self.force_update()

    @expose_command()
    def mute(self) -> None:
        self._run(["wpctl", "set-mute", self.device, "1"])
        self.force_update()

    @expose_command()
    def unmute(self) -> None:
        self._run(["wpctl", "set-mute", self.device, "0"])
        self.force_update()

    @expose_command()
    def refresh(self) -> None:
        self.force_update()

    @expose_command()
    def refresh_device(self) -> None:
        """Force-refresh the device state in case default device changes."""
        if "@DEFAULT_AUDIO" in self.device:
            self.force_update()


class MicWidget(AudioWidget):
    """Minimal PipeWire microphone widget using wpctl."""

    _LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (90, "red", "󰍬"),
        (0, "palegreen", "󰍬"),
    )
    _MUTED: Tuple[str, str] = ("grey", "󰍭")

    def __init__(self, **config: Any) -> None:
        config.setdefault("device", "@DEFAULT_AUDIO_SOURCE@")
        super().__init__(**config)
