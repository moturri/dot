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
import shutil
import subprocess
from typing import Any, List, Optional, Tuple

from libqtile.command.base import expose_command
from qtile_extras.widget import GenPollText


def run(cmd: List[str], timeout: float = 0.5) -> Optional[str]:
    try:
        return subprocess.check_output(
            cmd, text=True, timeout=timeout, env={"LC_ALL": "C.UTF-8", **os.environ}
        ).strip()
    except Exception:
        return None


def require(command: str) -> None:
    if not shutil.which(command):
        raise RuntimeError(f"Missing dependency: {command}")


class AudioWidget(GenPollText):  # type: ignore[misc]
    """Suckless PipeWire audio widget using wpctl."""

    LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (75, "salmon", "󰕾"),
        (50, "mediumpurple", "󰖀"),
        (25, "lightblue", "󰕿"),
        (0, "palegreen", "󰕿"),
    )
    MUTED: Tuple[str, str] = ("grey", "󰝟")

    def __init__(
        self,
        device: str = "@DEFAULT_AUDIO_SINK@",
        step: int = 5,
        max_volume: int = 100,
        update_interval: float = 9999.0,
        show_icon: bool = True,
        **config: Any,
    ):
        require("wpctl")
        self.device = device
        self.step = max(1, min(step, 25))
        self.max_volume = max(50, min(max_volume, 150))
        self.show_icon = show_icon
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_state(self) -> Tuple[int, bool]:
        out = run(["wpctl", "get-volume", self.device])
        if not out:
            return 0, True
        return self._parse_state(out)

    def _parse_state(self, output: str) -> Tuple[int, bool]:
        muted = "[MUTED]" in output
        try:
            vol = int(float(output.split()[1]) * 100)
        except Exception:
            vol = 0
        return vol, muted

    def _poll(self) -> str:
        vol, muted = self._get_state()
        color, icon = self._icon(vol, muted)
        text = f"{icon}  {vol}%" if self.show_icon else f"{vol}%"
        return f'<span foreground="{color}">{text}</span>'

    def _icon(self, vol: int, muted: bool) -> Tuple[str, str]:
        if muted:
            return self.MUTED
        return next(
            ((c, i) for t, c, i in self.LEVELS if vol >= t), self.LEVELS[-1][1:]
        )

    def _set_volume(self, vol: int) -> None:
        pct = max(0, min(vol, self.max_volume))
        run(["wpctl", "set-volume", self.device, f"{pct}%"])
        self.force_update()

    @expose_command()
    def volume_up(self) -> None:
        v, _ = self._get_state()
        self._set_volume(v + self.step)

    @expose_command()
    def volume_down(self) -> None:
        v, _ = self._get_state()
        self._set_volume(v - self.step)

    @expose_command()
    def toggle_mute(self) -> None:
        run(["wpctl", "set-mute", self.device, "toggle"])
        self.force_update()

    @expose_command()
    def mute(self) -> None:
        run(["wpctl", "set-mute", self.device, "1"])
        self.force_update()

    @expose_command()
    def unmute(self) -> None:
        run(["wpctl", "set-mute", self.device, "0"])
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

    LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (75, "salmon", "󰍬"),
        (50, "mediumpurple", "󰍬"),
        (25, "lightblue", "󰍬"),
        (0, "palegreen", "󰍬"),
    )
    MUTED: Tuple[str, str] = ("grey", "󰍭")

    def __init__(self, **config: Any) -> None:
        config.setdefault("device", "@DEFAULT_AUDIO_SOURCE@")
        super().__init__(**config)
