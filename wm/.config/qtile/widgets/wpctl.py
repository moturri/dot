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
import time
from typing import Any, Final, cast

from libqtile import qtile as _qtile
from libqtile.command.base import expose_command
from libqtile.core.manager import Qtile
from libqtile.widget import base

qtile: Qtile = cast(Qtile, _qtile)
logger = logging.getLogger(__name__)


class AudioDeviceError(Exception):
    """Raised when audio device operations fail."""

    pass


def require(cmd: str) -> None:
    """Ensure a binary exists in $PATH."""
    if shutil.which(cmd) is None:
        raise RuntimeError(f"Missing required dependency: {cmd}")


def run(cmd: list[str], *, timeout: float = 1.0) -> str:
    """Run command and return stripped stdout."""
    return subprocess.check_output(
        cmd,
        text=True,
        timeout=timeout,
        env={**os.environ, "LC_ALL": "C.UTF-8"},
    ).strip()


def resolve_default_device(is_input: bool) -> str | None:
    """Return default sink/source ID via wpctl."""
    try:
        output = run(["wpctl", "status"], timeout=2)
    except subprocess.SubprocessError:
        logger.exception("wpctl status failed")
        return None

    lines = output.splitlines()
    target = "Sources:" if is_input else "Sinks:"
    parsing = False

    for line in lines:
        if target in line:
            parsing = True
            continue
        if parsing:
            if line.startswith(" "):
                if "*" in line:
                    # Extract device ID from line like "    * 123. Device Name"
                    parts = line.split()
                    for part in parts:
                        if part.rstrip(".").isdigit():
                            return part.rstrip(".")
            else:
                # Exited the target section
                break

    return None


# ------------------------------------------------------------
# Base widget
# ------------------------------------------------------------
class BaseAudioWidget(base._TextBox):
    """Lightweight PipeWire widget via wpctl subscribe."""

    orientations = base.ORIENTATION_HORIZONTAL

    DEFAULT_OUTPUT_DEVICE: Final[str] = "@DEFAULT_AUDIO_SINK@"
    DEFAULT_INPUT_DEVICE: Final[str] = "@DEFAULT_AUDIO_SOURCE@"

    RECONNECT_DELAY: Final[float] = 3.0
    MIN_STEP: Final[int] = 1
    MAX_STEP: Final[int] = 25
    MIN_MAX_VOLUME: Final[int] = 50
    MAX_MAX_VOLUME: Final[int] = 150

    SUBSCRIBE_KEYWORDS: Final[tuple[str, ...]] = ("default-node", "volume", "mute")

    def __init__(
        self,
        *,
        is_input: bool = False,
        device: str | None = None,
        step: int = 5,
        max_volume: int = 100,
        show_icon: bool = True,
        levels: tuple[tuple[int, str, str], ...] | None = None,
        muted: tuple[str, str] | None = None,
        **config: Any,
    ) -> None:
        require("wpctl")

        self.is_input = is_input
        self.step = max(self.MIN_STEP, min(step, self.MAX_STEP))
        self.max_volume = max(self.MIN_MAX_VOLUME, min(max_volume, self.MAX_MAX_VOLUME))
        self.show_icon = show_icon

        # Use provided theme or default
        self.levels = levels or (
            (75, "salmon", "󰕾"),
            (50, "mediumpurple", "󰖀"),
            (25, "lightblue", "󰕿"),
            (0, "palegreen", "󰕿"),
        )
        self.muted_style = muted or ("grey", "󰝟")

        # Resolve device
        self.device = self._resolve_device(device)

        super().__init__("", **config)  # type: ignore[no-untyped-call]

        # Thread state
        self._stop_event = threading.Event()
        self._last_update: float = 0.0
        self._lock = threading.Lock()

        self._thread = threading.Thread(target=self._subscribe_loop, daemon=True)
        self._thread.start()

        self._update_text()

    def _resolve_device(self, device: str | None) -> str:
        """Resolve device string, with fallback logic."""
        if device:
            return device

        resolved = resolve_default_device(self.is_input)
        if resolved:
            return resolved

        return (
            self.DEFAULT_INPUT_DEVICE if self.is_input else self.DEFAULT_OUTPUT_DEVICE
        )

    def finalize(self) -> None:
        """Cleanup background thread."""
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=1)
        super().finalize()  # type: ignore[no-untyped-call]

    # ------------------------------------------------------------
    # Subscription
    # ------------------------------------------------------------
    def _subscribe_loop(self) -> None:
        """Main event subscriber loop."""
        while not self._stop_event.is_set():
            try:
                self._listen_events()
            except Exception:
                logger.exception("wpctl subscribe crashed")
                # Attempt to resolve device again on failure
                with self._lock:
                    resolved = resolve_default_device(self.is_input)
                    if resolved:
                        self.device = resolved
                        logger.info(f"Resolved new device: {self.device}")

            if not self._stop_event.is_set():
                time.sleep(self.RECONNECT_DELAY)

    def _listen_events(self) -> None:
        """Blocking event stream from `wpctl subscribe`."""
        proc = subprocess.Popen(
            ["wpctl", "subscribe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )

        assert proc.stdout is not None

        try:
            for line in proc.stdout:
                if self._stop_event.is_set():
                    break
                if any(k in line for k in self.SUBSCRIBE_KEYWORDS):
                    self._debounced_update()
        finally:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    proc.kill()

    def _debounced_update(self, delay: float = 0.1) -> None:
        """Debounce updates to prevent excessive redraws."""
        now = time.monotonic()
        if now - self._last_update >= delay:
            self._last_update = now
            if hasattr(qtile, "call_soon_threadsafe"):
                qtile.call_soon_threadsafe(self._update_text)
            else:
                # Fallback for when running outside of a real qtile session
                self._update_text()

    # ------------------------------------------------------------
    # State parsing
    # ------------------------------------------------------------
    def _get_state(self) -> tuple[int, bool]:
        """Get current volume and mute state."""
        try:
            with self._lock:
                out = run(["wpctl", "get-volume", self.device])
            return self._parse_state(out)
        except subprocess.SubprocessError:
            logger.exception("Failed to read volume for device: %s", self.device)
            return 0, True

    @staticmethod
    def _parse_state(output: str) -> tuple[int, bool]:
        """Parse wpctl get-volume output."""
        muted = "[MUTED]" in output
        vol = 0

        # Find first token containing digits
        for token in output.split():
            if any(ch.isdigit() for ch in token):
                try:
                    vol = int(float(token) * 100)
                    vol = max(0, min(150, vol))
                    break
                except ValueError:
                    logger.warning("Failed to parse volume from token: %s", token)
                    continue

        return vol, muted

    def _icon_color(self, volume: int, muted: bool) -> tuple[str, str]:
        """Determine icon and color based on volume and mute state."""
        if muted:
            return self.muted_style
        if volume > 100:
            return "gold", self.levels[0][2]
        for threshold, color, icon in self.levels:
            if volume >= threshold:
                return color, icon
        return self.levels[-1][1:]

    def _update_text(self) -> None:
        """Update widget display text."""
        volume, muted = self._get_state()
        color, icon = self._icon_color(volume, muted)

        label = f"{icon}  {volume}%" if self.show_icon else f"{volume}%"
        self.update(f'<span foreground="{color}">{label}</span>')  # type: ignore[no-untyped-call]

    # ------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------
    def _set_volume(self, value: int) -> None:
        """Set volume to specified percentage."""
        clamped = max(0, min(value, self.max_volume))
        try:
            with self._lock:
                run(["wpctl", "set-volume", self.device, f"{clamped}%"])
            self._update_text()
        except subprocess.SubprocessError:
            logger.exception("set-volume failed for device: %s", self.device)

    @expose_command()
    def volume_up(self) -> None:
        """Increase volume by step amount."""
        volume, _ = self._get_state()
        self._set_volume(volume + self.step)

    @expose_command()
    def volume_down(self) -> None:
        """Decrease volume by step amount."""
        volume, _ = self._get_state()
        self._set_volume(volume - self.step)

    def _set_mute(self, state: str) -> None:
        """Set mute state (0, 1, or toggle)."""
        try:
            with self._lock:
                run(["wpctl", "set-mute", self.device, state])
            self._update_text()
        except subprocess.SubprocessError:
            logger.exception("set-mute failed for device: %s", self.device)

    @expose_command()
    def toggle_mute(self) -> None:
        """Toggle mute state."""
        self._set_mute("toggle")

    @expose_command()
    def mute(self) -> None:
        """Mute audio."""
        self._set_mute("1")

    @expose_command()
    def unmute(self) -> None:
        """Unmute audio."""
        self._set_mute("0")

    @expose_command()
    def refresh(self) -> None:
        """Manually refresh widget state."""
        self._update_text()


# ------------------------------------------------------------
# Specializations
# ------------------------------------------------------------
class AudioWidget(BaseAudioWidget):
    """Output sink widget for system audio."""

    def __init__(self, **config: Any) -> None:
        super().__init__(is_input=False, **config)


class MicWidget(BaseAudioWidget):
    """Input source widget for microphone."""

    def __init__(self, **config: Any) -> None:
        mic_levels = (
            (75, "salmon", "󰍬"),
            (50, "mediumpurple", "󰍬"),
            (25, "lightblue", "󰍬"),
            (0, "palegreen", "󰍬"),
        )
        super().__init__(
            is_input=True,
            levels=mic_levels,
            muted=("grey", "󰍭"),
            **config,
        )
