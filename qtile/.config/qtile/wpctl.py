# Copyright (C) 2025, Elton Moturi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import re
import subprocess
from typing import Any, Callable, Dict, List, Optional, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText

_ENV: Dict[str, str] = {"LC_ALL": "C.UTF-8", **os.environ}


class AudioWidget(GenPollText):  # type: ignore
    """Minimal and efficient PipeWire audio widget using wpctl."""

    _LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (70, "salmon", "󰕾"),
        (40, "mediumpurple", "󰖀"),
        (0, "palegreen", "󰕿"),
    )
    _MUTED: Tuple[str, str] = ("grey", "󰝟")
    _REGEX_VOLUME = re.compile(r"\d+(\.\d+)?")
    _REGEX_STATUS = re.compile(r"\[MUTED\]")

    def __init__(
        self,
        device: str = "@DEFAULT_AUDIO_SINK@",
        step: int = 5,
        max_volume: int = 100,
        update_interval: float = 60.0,
        **config: Any,
    ) -> None:
        self.device = device
        self.step = max(1, min(25, step))
        self.max_volume = max(50, min(150, max_volume))

        self._vol: int = -1
        self._muted: bool = False
        self._device_hash: str = ""
        self._last_text: str = ""

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _cmd(self, args: List[str]) -> str:
        try:
            return subprocess.run(
                args, capture_output=True, text=True, timeout=0.3, check=True, env=_ENV
            ).stdout.strip()
        except Exception:
            return ""

    def _get_state(self) -> Tuple[int, bool, Optional[str]]:
        output = self._cmd(["wpctl", "get-volume", self.device])
        if not output:
            return 0, True, None

        vol_match = self._REGEX_VOLUME.search(output)
        vol = round(float(vol_match.group()) * 100) if vol_match else 0
        muted = bool(self._REGEX_STATUS.search(output))
        node_id = output.split(":")[0].strip() if ":" in output else None
        return vol, muted, node_id

    def _icon_color(self, vol: int, muted: bool) -> Tuple[str, str]:
        if muted:
            return self._MUTED
        for threshold, color, icon in self._LEVELS:
            if vol >= threshold:
                return color, icon
        return self._LEVELS[-1][1], self._LEVELS[-1][2]

    def _poll(self) -> str:
        vol, muted, node_id = self._get_state()
        state_hash = f"{vol}-{muted}-{node_id}"
        if state_hash == self._device_hash:
            return self._last_text

        self._device_hash = state_hash
        self._vol, self._muted = vol, muted

        color, icon = self._icon_color(vol, muted)
        vol_str = f"{vol}%!" if vol > 100 else f"{vol}%"
        self._last_text = f'<span foreground="{color}">{icon}  {vol_str}</span>'
        return self._last_text

    def _set_volume(self, val: int) -> None:
        vol = max(0, min(self.max_volume, val))
        self._cmd(["wpctl", "set-volume", self.device, f"{vol}%"])
        self.refresh()

    @expose_command()
    def volume_up(self) -> None:
        vol, _, _ = self._get_state()
        self._set_volume(vol + self.step)

    @expose_command()
    def volume_down(self) -> None:
        vol, _, _ = self._get_state()
        self._set_volume(vol - self.step)

    @expose_command()
    def set_volume(self, percent: int) -> None:
        self._set_volume(percent)

    @expose_command()
    def toggle_mute(self) -> None:
        self._cmd(["wpctl", "set-mute", self.device, "toggle"])
        self.refresh()

    @expose_command()
    def mute(self) -> None:
        self._cmd(["wpctl", "set-mute", self.device, "1"])
        self.refresh()

    @expose_command()
    def unmute(self) -> None:
        self._cmd(["wpctl", "set-mute", self.device, "0"])
        self.refresh()

    @expose_command()
    def refresh(self) -> None:
        self.force_update()


class MicWidget(AudioWidget):
    """Optimized PipeWire microphone widget."""

    _LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (90, "red", "󰍬"),
        (0, "palegreen", "󰍬"),
    )
    _MUTED: Tuple[str, str] = ("grey", "󰍭")

    def __init__(self, **config: Any) -> None:
        config.setdefault("device", "@DEFAULT_AUDIO_SOURCE@")
        super().__init__(**config)


class AudioManager:
    """Audio device management via wpctl."""

    _SECTION_HEADERS = {"sink": "Sinks:", "source": "Sources:"}
    _REGEX_DEVICE_LINE = re.compile(r"^\s*[│├└]\s*(\d+)\.\s+(.+)$")
    _REGEX_ID = re.compile(r"^(\d+)\.")

    @staticmethod
    def get_devices(kind: str = "sink") -> List[str]:
        try:
            output = subprocess.run(
                ["wpctl", "status"],
                capture_output=True,
                text=True,
                timeout=1.0,
                check=True,
                env=_ENV,
            ).stdout
        except Exception:
            return []

        section = AudioManager._SECTION_HEADERS.get(kind, "")
        lines = output.splitlines()
        found = False
        devices: List[str] = []

        for line in lines:
            if section in line:
                found = True
                continue
            if found and not line.startswith(" "):
                break
            match = AudioManager._REGEX_DEVICE_LINE.match(line)
            if match:
                devices.append(f"{match.group(1)}. {match.group(2)}")

        return devices

    @staticmethod
    def switch_device(
        device_id: str, on_success: Optional[Callable[[], None]] = None
    ) -> bool:
        try:
            subprocess.run(
                ["wpctl", "set-default", device_id],
                capture_output=True,
                timeout=0.5,
                check=True,
                env=_ENV,
            )
            if on_success:
                on_success()
            return True
        except Exception:
            return False

    @staticmethod
    def get_default_device(kind: str = "sink") -> Optional[str]:
        for device in AudioManager.get_devices(kind):
            if "*" in device:
                match = AudioManager._REGEX_ID.match(device)
                if match:
                    return match.group(1)
        return None
