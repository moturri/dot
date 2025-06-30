# MIT License
#
# Copyright (c) 2025 Elton Moturi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import subprocess
from typing import Any, List, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText


class AudioWidget(GenPollText):  # type: ignore
    """Suckless PipeWire audio widget using wpctl."""

    _LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (75, "salmon", "󰕾"),
        (50, "mediumpurple", "󰖀"),
        (25, "lightblue", "󰕿"),
        (0, "palegreen", "󰕿"),
    )
    _MUTED: Tuple[str, str] = ("grey", "󰝟")

    def __init__(
        self,
        device: str = "@DEFAULT_AUDIO_SINK@",
        step: int = 5,
        max_volume: int = 100,
        update_interval: float = 9999.0,
        show_icon: bool = True,
        **config: Any,
    ) -> None:
        self.device = device
        self.step = max(1, min(step, 25))
        self.max_volume = max(50, min(max_volume, 150))
        self.show_icon = show_icon
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _run(self, args: List[str]) -> str:
        try:
            return subprocess.check_output(
                args, text=True, timeout=0.5, env={"LC_ALL": "C.UTF-8", **os.environ}
            ).strip()
        except Exception:
            return ""

    def _get_state(self) -> Tuple[int, bool]:
        output = self._run(["wpctl", "get-volume", self.device])
        try:
            vol = round(float(output.split()[1]) * 100)
        except (IndexError, ValueError):
            vol = 0
        muted = "[MUTED]" in output
        return vol, muted

    def _icon_color(self, vol: int, muted: bool) -> Tuple[str, str]:
        if muted:
            return self._MUTED
        for threshold, color, icon in self._LEVELS:
            if vol >= threshold:
                return color, icon
        return self._LEVELS[-1][1], self._LEVELS[-1][2]

    def _poll(self) -> str:
        vol, muted = self._get_state()
        color, icon = self._icon_color(vol, muted)
        text = f"{icon}  {vol}%" if self.show_icon else f"{vol}%"
        return f'<span foreground="{color}">{text}</span>'

    def _set_volume(self, value: int) -> None:
        vol = max(0, min(value, self.max_volume))
        self._run(["wpctl", "set-volume", self.device, f"{vol}%"])
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
        if "@DEFAULT_AUDIO" in self.device:
            self.force_update()


class MicWidget(AudioWidget):
    """Suckless PipeWire microphone widget using wpctl."""

    _LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (75, "salmon", "󰍬"),
        (50, "mediumpurple", "󰍬"),
        (25, "lightblue", "󰍬"),
        (0, "palegreen", "󰍬"),
    )
    _MUTED: Tuple[str, str] = ("grey", "󰍭")

    def __init__(self, **config: Any) -> None:
        config.setdefault("device", "@DEFAULT_AUDIO_SOURCE@")
        super().__init__(**config)
