# Copyright (c) 2025 Elton Moturi - MIT License
#
# Audio widgets backed by WirePlumber via `wpctl`.
#
# Design philosophy:
# - Do one thing well: control audio via wpctl, nothing more
# - No external dependencies beyond stdlib and qtile
# - Shell out to wpctl for simplicity and stability
# - Minimal abstraction - code should be obvious
# - Fail gracefully, never crash the bar
#
# Icon glyphs assume a Nerd Font (JetBrainsMono, Iosevka, etc.)

from __future__ import annotations

import logging
import os
import re
import shutil
import subprocess
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Callable, Final, Iterator, Literal, cast

from libqtile import qtile as _qtile
from libqtile.bar import Bar
from libqtile.command.base import expose_command
from libqtile.core.manager import Qtile
from libqtile.widget import base

qtile: Qtile = cast(Qtile, _qtile)
logger = logging.getLogger(__name__)

ENV: Final[dict[str, str]] = {**os.environ, "LC_ALL": "C.UTF-8"}


class AudioDeviceError(Exception):
    """Audio operation failed."""


@dataclass(frozen=True, slots=True)
class VolumeLevel:
    """Volume threshold configuration."""

    threshold: int
    color: str
    icon: str


@dataclass(frozen=True, slots=True)
class AudioState:
    """Current device state."""

    volume: int
    muted: bool


def run(cmd: list[str], timeout: float = 1.0) -> str:
    """Execute command, return output or raise AudioDeviceError."""
    try:
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=ENV,
            check=True,
        ).stdout.strip()
    except (
        subprocess.TimeoutExpired,
        subprocess.CalledProcessError,
        FileNotFoundError,
    ) as e:
        raise AudioDeviceError(f"{' '.join(cmd)}: {e}") from e


def resolve_default_device(is_input: bool) -> str | None:
    """Find default device ID from wpctl status."""
    try:
        output = run(["wpctl", "status"], timeout=2)
    except AudioDeviceError:
        return None

    section = "Sources:" if is_input else "Sinks:"
    active = False

    for line in output.splitlines():
        if section in line.strip():
            active = True
            continue
        if active:
            if "*" in line:
                match = re.search(r"\b(\d+)\.", line)
                if match:
                    return match.group(1)
            if line and not line[0].isspace():
                break
    return None


def parse_volume(output: str) -> AudioState:
    """Parse 'wpctl get-volume' output."""
    muted = "MUTED" in output
    match = re.search(r"\b\d+\.\d+\b", output)
    volume = int(float(match.group()) * 100) if match else 0
    return AudioState(volume=max(0, min(150, volume)), muted=muted)


class BaseAudioWidget(base._TextBox):
    """Minimal audio widget - monitors wpctl, displays volume."""

    orientations = base.ORIENTATION_HORIZONTAL

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
        if shutil.which("wpctl") is None:
            raise RuntimeError("wpctl not found - install wireplumber")

        self.is_input = is_input
        self.step = max(1, min(step, 25))
        self.max_volume = max(50, min(max_volume, 150))
        self.show_icon = show_icon

        # Default levels
        default_levels = (
            (75, "salmon", "󰕾"),
            (50, "mediumpurple", "󰖀"),
            (25, "lightblue", "󰕿"),
            (0, "palegreen", "󰕿"),
        )
        if is_input:
            default_levels = (
                (75, "salmon", "󰍬"),
                (50, "mediumpurple", "󰍬"),
                (25, "lightblue", "󰍬"),
                (0, "palegreen", "󰍬"),
            )

        self.levels = tuple(
            VolumeLevel(t, c, i) for t, c, i in (levels or default_levels)
        )

        muted_tuple = muted or (("grey", "󰍭") if is_input else ("grey", "󰝟"))
        self.muted_color, self.muted_icon = muted_tuple

        # Resolve device
        resolved = resolve_default_device(is_input)
        default = "@DEFAULT_AUDIO_SOURCE@" if is_input else "@DEFAULT_AUDIO_SINK@"
        self.device = device or resolved or default

        super().__init__("", **config)

        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last_update = 0.0
        self._timer: threading.Timer | None = None
        self._thread: threading.Thread | None = None
        self._proc: subprocess.Popen[str] | None = None
        self._cached_state: AudioState | None = None

        self._update()

    def finalize(self) -> None:
        """Clean up on widget destruction."""
        self._stop.set()

        if self._timer:
            self._timer.cancel()

        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=0.5)
            except Exception:
                pass

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

        super().finalize()

    def _configure(self, qtile: Qtile, bar: Bar) -> None:
        super()._configure(qtile, bar)
        if self._thread is None:
            name = f"AudioWidget-{'Input' if self.is_input else 'Output'}"
            self._thread = threading.Thread(
                target=self._monitor, daemon=True, name=name
            )
            self._thread.start()

    def _monitor(self) -> None:
        """Monitor wpctl subscribe for changes."""
        while not self._stop.is_set():
            try:
                self._listen()
            except Exception as e:
                logger.error("wpctl subscribe failed: %s", e)
                # Try to recover by checking for new default device
                new = resolve_default_device(self.is_input)
                if new and new != self.device:
                    self.device = new
                    self._update()

            if not self._stop.is_set():
                self._stop.wait(2.0)

    def _listen(self) -> None:
        """Subscribe to wpctl events."""
        proc = subprocess.Popen(
            ["wpctl", "subscribe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            env=ENV,
        )
        self._proc = proc

        try:
            if proc.stdout:
                for line in proc.stdout:
                    if self._stop.is_set():
                        break
                    if any(k in line for k in ("default-node", "volume", "mute")):
                        self._debounce(self._update)
        finally:
            self._proc = None
            try:
                proc.terminate()
                proc.wait(timeout=0.5)
            except Exception:
                pass

    def _debounce(self, fn: Callable[[], None], delay: float = 0.05) -> None:
        """Debounce updates to avoid spam."""
        now = time.monotonic()

        def invoke() -> None:
            self._last_update = time.monotonic()
            try:
                self.qtile.call_soon_threadsafe(fn)
            except Exception as e:
                logger.error("Debounce callback failed: %s", e)

        if now - self._last_update >= delay:
            invoke()
            return

        if self._timer:
            self._timer.cancel()

        self._timer = threading.Timer(delay, invoke)
        self._timer.daemon = True
        self._timer.start()

    @contextmanager
    def _device_lock(self) -> Iterator[None]:
        """Lock for device operations."""
        if not self._lock.acquire(timeout=1.0):
            raise AudioDeviceError("Lock timeout")
        try:
            yield
        finally:
            self._lock.release()

    def _get_state(self) -> AudioState:
        """Get current volume and mute state."""
        try:
            with self._device_lock():
                output = run(["wpctl", "get-volume", self.device], timeout=0.5)
            state = parse_volume(output)
            self._cached_state = state
            return state
        except AudioDeviceError:
            logger.error("Failed to read volume for %s", self.device)
            return self._cached_state or AudioState(0, True)

    def _format_text(self, state: AudioState) -> str:
        """Format display text with color and icon."""
        if state.muted:
            color, icon = self.muted_color, self.muted_icon
        elif state.volume > 100:
            color, icon = "gold", self.levels[0].icon
        else:
            for level in self.levels:
                if state.volume >= level.threshold:
                    color, icon = level.color, level.icon
                    break
            else:
                color, icon = self.levels[-1].color, self.levels[-1].icon

        text = f"{icon}  {state.volume}%" if self.show_icon else f"{state.volume}%"
        return f'<span foreground="{color}">{text}</span>'

    def _update(self) -> None:
        """Update widget display."""
        state = self._get_state()
        self.update(self._format_text(state))

    def button_press(self, x: int, y: int, button: int) -> None:
        """Handle mouse clicks."""
        actions = {
            2: self.refresh,
            3: self.toggle_mute,
            4: self.volume_up,
            5: self.volume_down,
        }
        if button in actions:
            actions[button]()

    def _set_volume(self, value: int) -> None:
        """Set volume to specific value."""
        value = max(0, min(value, self.max_volume))
        try:
            with self._device_lock():
                run(["wpctl", "set-volume", self.device, f"{value}%"], timeout=0.5)
            self._debounce(self._update, delay=0.02)
        except AudioDeviceError:
            logger.error("Failed to set volume for %s", self.device)

    def _set_mute(self, state: Literal["0", "1", "toggle"]) -> None:
        """Set mute state."""
        try:
            with self._device_lock():
                run(["wpctl", "set-mute", self.device, state], timeout=0.5)
            self._debounce(self._update, delay=0.02)
        except AudioDeviceError:
            logger.error("Failed to set mute for %s", self.device)

    @expose_command()
    def volume_up(self) -> None:
        """Increase volume."""
        self._set_volume(self._get_state().volume + self.step)

    @expose_command()
    def volume_down(self) -> None:
        """Decrease volume."""
        self._set_volume(self._get_state().volume - self.step)

    @expose_command()
    def set_volume(self, value: int) -> None:
        """Set absolute volume."""
        self._set_volume(value)

    @expose_command()
    def toggle_mute(self) -> None:
        """Toggle mute."""
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
        """Refresh display."""
        self._update()


class AudioWidget(BaseAudioWidget):
    """Widget for audio output control."""

    def __init__(self, **config: Any) -> None:
        super().__init__(is_input=False, **config)


class MicWidget(BaseAudioWidget):
    """Widget for microphone input control."""

    def __init__(self, **config: Any) -> None:
        super().__init__(is_input=True, **config)
