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
import threading
from typing import Any, List, Optional, TextIO, Tuple, cast

from libqtile import qtile as _qtile
from libqtile.command.base import expose_command
from libqtile.core.manager import Qtile
from libqtile.widget import base

qtile: Qtile = cast(Qtile, _qtile)
logger = logging.getLogger(__name__)


def run(cmd: List[str]) -> Optional[str]:
    """Run a shell command and return stdout, or None on error."""
    try:
        return subprocess.check_output(
            cmd,
            text=True,
            env={"LC_ALL": "C.UTF-8", **os.environ},
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        logger.warning("Command failed: %s -> %s", " ".join(cmd), e)
        return None


def require(command: str) -> None:
    """Raise if the required binary is not available."""
    if shutil.which(command) is None:
        raise RuntimeError(f"Missing dependency: {command}")


def resolve_default_device(is_input: bool = False) -> Optional[str]:
    """Return the default sink or source from wpctl status output."""
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
            parts = line.strip().split()
            if len(parts) >= 2:
                return parts[1]
    return None


class BaseAudioWidget(base._TextBox):
    """Event-driven PipeWire audio widget using wpctl subscribe."""

    orientations = base.ORIENTATION_HORIZONTAL

    def __init__(
        self,
        is_input: bool = False,
        device: Optional[str] = None,
        step: int = 5,
        max_volume: int = 100,
        show_icon: bool = True,
        levels: Optional[Tuple[Tuple[int, str, str], ...]] = None,
        muted: Optional[Tuple[str, str]] = None,
        **config: Any,
    ) -> None:
        require("wpctl")

        if device is None:
            default = "@DEFAULT_AUDIO_SOURCE@" if is_input else "@DEFAULT_AUDIO_SINK@"
            if run(["wpctl", "get-volume", default]):
                device = default
            else:
                device = resolve_default_device(is_input)
        if device is None:
            raise RuntimeError("Could not resolve a valid audio device.")

        self.is_input: bool = is_input
        self.device: str = device
        self.step: int = max(1, min(step, 25))
        self.max_volume: int = max(50, min(max_volume, 150))
        self.show_icon: bool = show_icon

        self.LEVELS: Tuple[Tuple[int, str, str], ...] = levels or (
            (75, "salmon", "󰕾"),
            (50, "mediumpurple", "󰖀"),
            (25, "lightblue", "󰕿"),
            (0, "palegreen", "󰕿"),
        )
        self.MUTED: Tuple[str, str] = muted or ("grey", "󰝟")

        super().__init__("", **config)  # type: ignore[no-untyped-call]

        self._stop_event = threading.Event()
        self._last_volume: int = -1
        self._last_muted: bool = False

        # Skip launching threads when qtile check/import stage
        if not hasattr(qtile, "call_soon_threadsafe"):
            self._update_text()
            return

        # Spawn PipeWire event listener
        self._thread = threading.Thread(target=self._subscribe, daemon=True)
        self._thread.start()

        qtile.call_soon_threadsafe(self._update_text)

    def finalize(self) -> None:
        """Terminate background subscription thread safely on shutdown."""
        self._stop_event.set()
        super().finalize()  # type: ignore[no-untyped-call]

    def _subscribe(self) -> None:
        """Listen for PipeWire events and update on volume or node changes."""
        proc: Optional[subprocess.Popen[str]] = None
        try:
            proc = subprocess.Popen(
                ["wpctl", "subscribe"],
                stdout=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
            assert proc.stdout is not None
            for line in cast(TextIO, proc.stdout):
                if self._stop_event.is_set():
                    break
                if not line or not ("default-node" in line or "volume" in line):
                    continue
                qtile.call_soon_threadsafe(self._update_text)
        except Exception as e:
            logger.error("wpctl subscribe failed: %s", e)
        finally:
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    proc.kill()

    def _get_state(self) -> Tuple[int, bool]:
        """Return (volume, muted) state."""
        output = run(["wpctl", "get-volume", self.device])
        return self._parse_state(output) if output else (0, True)

    def _parse_state(self, output: str) -> Tuple[int, bool]:
        """Extract volume percentage and mute flag from wpctl output."""
        muted = "[MUTED]" in output
        tokens = [
            t for t in output.replace("%", "").split() if any(c.isdigit() for c in t)
        ]
        try:
            vol_float = float(tokens[0]) if tokens else 0.0
            volume = min(150, max(0, int(vol_float * 100)))
        except Exception as e:
            logger.warning("Volume parse error: %s -> %s", output, e)
            volume = 0
        return volume, muted

    def _icon(self, vol: int, muted: bool) -> Tuple[str, str]:
        if muted:
            return self.MUTED
        for threshold, color, icon in self.LEVELS:
            if vol >= threshold:
                return color, icon
        return self.LEVELS[-1][1], self.LEVELS[-1][2]

    def _update_text(self) -> None:
        """Recompute and render the widget label."""
        volume, muted = self._get_state()
        if volume == self._last_volume and muted == self._last_muted:
            return
        self._last_volume, self._last_muted = volume, muted
        color, icon = self._icon(volume, muted)
        text = f"{icon}  {volume}%" if self.show_icon else f"{volume}%"
        self.update(f'<span foreground="{color}">{text}</span>')  # type: ignore[no-untyped-call]

    def _set_volume(self, vol: int) -> None:
        clamped = max(0, min(vol, self.max_volume))
        run(["wpctl", "set-volume", self.device, f"{clamped}%"])
        self._update_text()

    # Exposed Qtile commands
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
        self._update_text()

    @expose_command()
    def mute(self) -> None:
        run(["wpctl", "set-mute", self.device, "1"])
        self._update_text()

    @expose_command()
    def unmute(self) -> None:
        run(["wpctl", "set-mute", self.device, "0"])
        self._update_text()

    @expose_command()
    def refresh(self) -> None:
        self._update_text()


class AudioWidget(BaseAudioWidget):
    """Output device (sink) volume indicator."""

    def __init__(self, **config: Any) -> None:
        super().__init__(is_input=False, **config)


class MicWidget(BaseAudioWidget):
    """Input device (source) volume indicator."""

    def __init__(self, **config: Any) -> None:
        levels: Tuple[Tuple[int, str, str], ...] = (
            (75, "salmon", "󰍬"),
            (50, "mediumpurple", "󰍬"),
            (25, "lightblue", "󰍬"),
            (0, "palegreen", "󰍬"),
        )
        muted: Tuple[str, str] = ("grey", "󰍭")
        super().__init__(is_input=True, levels=levels, muted=muted, **config)
