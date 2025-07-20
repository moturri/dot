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


import logging
import os
import shutil
import subprocess
from typing import Any, List, Optional, Tuple

from libqtile.command.base import expose_command
from qtile_extras.widget import GenPollText

logger = logging.getLogger(__name__)


def run(cmd: List[str], timeout: float = 0.5) -> Optional[str]:
    try:
        return subprocess.check_output(
            cmd, text=True, timeout=timeout, env={"LC_ALL": "C.UTF-8", **os.environ}
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logger.warning(f"Command failed: {' '.join(cmd)} -> {e}")
        return None


def require(command: str) -> None:
    if shutil.which(command) is None:
        raise RuntimeError(f"Missing dependency: {command}")


def resolve_default_device(is_input: bool = False) -> Optional[str]:
    output = run(["wpctl", "status"])
    if not output:
        return None
    lines = output.splitlines()
    category = "Sources:" if is_input else "Sinks:"
    found = False
    for line in lines:
        if category in line:
            found = True
        elif found and line.strip().startswith("*"):
            return line.split()[1]
    return None


class AudioWidget(GenPollText):  # type: ignore[misc]

    LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (75, "salmon", "󰕾"),
        (50, "mediumpurple", "󰖀"),
        (25, "lightblue", "󰕿"),
        (0, "palegreen", "󰕿"),
    )
    MUTED: Tuple[str, str] = ("grey", "󰝟")

    def __init__(
        self,
        device: Optional[str] = None,
        step: int = 5,
        max_volume: int = 100,
        update_interval: float = 9999.0,
        show_icon: bool = True,
        **config: Any,
    ):
        require("wpctl")

        if device is None:
            default_sink = "@DEFAULT_AUDIO_SINK@"
            if run(["wpctl", "get-volume", default_sink]):
                device = default_sink
            else:
                device = resolve_default_device(False)

        if device is None:
            raise RuntimeError("Could not resolve a valid audio sink device.")

        self.device: str = device
        self.step = max(1, min(step, 25))
        self.max_volume = max(50, min(max_volume, 150))
        self.show_icon = show_icon

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _poll(self) -> str:
        volume, muted = self._get_state()
        color, icon = self._icon(volume, muted)
        text = f"{icon}  {volume}%" if self.show_icon else f"{volume}%"
        return f'<span foreground="{color}">{text}</span>'

    def _get_state(self) -> Tuple[int, bool]:
        output = run(["wpctl", "get-volume", self.device])
        return self._parse_state(output) if output else (0, True)

    def _parse_state(self, output: str) -> Tuple[int, bool]:
        parts = output.strip().split()
        muted = "[MUTED]" in output
        try:
            vol_float = float(parts[1])
            volume = min(150, max(0, int(vol_float * 100)))
        except (IndexError, ValueError) as e:
            logger.warning(f"Volume parse error: {output} -> {e}")
            volume = 0
        return volume, muted

    def _icon(self, vol: int, muted: bool) -> Tuple[str, str]:
        if muted:
            return self.MUTED
        for threshold, color, icon in self.LEVELS:
            if vol >= threshold:
                return color, icon
        return self.LEVELS[-1][1], self.LEVELS[-1][2]

    def _set_volume(self, vol: int) -> None:
        clamped = max(0, min(vol, self.max_volume))
        run(["wpctl", "set-volume", self.device, f"{clamped}%"])
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
        default_sink = "@DEFAULT_AUDIO_SINK@"
        if run(["wpctl", "get-volume", default_sink]):
            self.device = default_sink
        else:
            self.device = resolve_default_device(False) or self.device
        self.force_update()


class MicWidget(AudioWidget):
    LEVELS: Tuple[Tuple[int, str, str], ...] = (
        (75, "salmon", "󰍬"),
        (50, "mediumpurple", "󰍬"),
        (25, "lightblue", "󰍬"),
        (0, "palegreen", "󰍬"),
    )
    MUTED: Tuple[str, str] = ("grey", "󰍭")

    def __init__(self, **config: Any) -> None:
        device = config.get("device")
        if device is None:
            default_source = "@DEFAULT_AUDIO_SOURCE@"
            if run(["wpctl", "get-volume", default_source]):
                device = default_source
            else:
                device = resolve_default_device(True)

        if device is None:
            raise RuntimeError("Could not resolve a valid microphone device.")

        config["device"] = device
        super().__init__(**config)
