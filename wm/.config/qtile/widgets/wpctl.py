# Copyright (c) 2025 Elton Moturi - MIT License
#
# Audio widgets backed by WirePlumber via `wpctl`.
#
# Enhancements:
# - Dynamic profile change detection and updates
# - Better Pipewire integration with proper event handling
# - Improved error recovery and state management
# - Reduced latency for volume changes
# - Better thread safety and resource cleanup

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
    device_id: str


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
    """Find default device ID from wpctl status with improved parsing."""
    try:
        output = run(["wpctl", "status"], timeout=2)
    except AudioDeviceError:
        return None

    # Look for the Audio section first
    section = "Sources:" if is_input else "Sinks:"
    in_audio_section = False
    in_target_section = False

    for line in output.splitlines():
        stripped = line.strip()

        # Check if we're in the Audio section
        if "Audio" in stripped:
            in_audio_section = True
            continue

        # Check if we've left the Audio section
        if (
            in_audio_section
            and stripped
            and not line[0].isspace()
            and "├" not in line
            and "└" not in line
        ):
            # We've hit a new major section
            if "Video" in stripped or "Settings" in stripped:
                break

        # Look for our target subsection
        if in_audio_section and section in stripped:
            in_target_section = True
            continue

        # If we're in the target section, look for the default device
        if in_target_section:
            # Check if we've left this subsection
            if (
                stripped
                and not line[0].isspace()
                and "├" not in line
                and "└" not in line
            ):
                if any(
                    s in stripped
                    for s in [
                        "Sinks:",
                        "Sources:",
                        "Sink endpoints:",
                        "Source endpoints:",
                    ]
                ):
                    break

            # Look for the default device (marked with *)
            if "* " in line or "*." in line:
                # Extract device ID - matches patterns like "  * 123. Device Name"
                match = re.search(r"\*\s*(\d+)\.", line)
                if match:
                    return match.group(1)

    return None


def parse_volume(output: str) -> tuple[int, bool]:
    """Parse 'wpctl get-volume' output."""
    muted = "MUTED" in output
    match = re.search(r"\b\d+\.\d+\b", output)
    volume = int(float(match.group()) * 100) if match else 0
    return max(0, min(150, volume)), muted


class BaseAudioWidget(base._TextBox):
    """Enhanced audio widget with dynamic device tracking."""

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
        update_interval: float = 0.1,
        **config: Any,
    ) -> None:
        if shutil.which("wpctl") is None:
            raise RuntimeError("wpctl not found - install wireplumber")

        self.is_input = is_input
        self.step = max(1, min(step, 25))
        self.max_volume = max(50, min(max_volume, 150))
        self.show_icon = show_icon
        self.update_interval = update_interval

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

        # Track device dynamically
        self._static_device = device
        self._current_device_id: str | None = None
        self._resolve_device()

        super().__init__("", **config)

        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last_update = 0.0
        self._timer: threading.Timer | None = None
        self._thread: threading.Thread | None = None
        self._proc: subprocess.Popen[str] | None = None
        self._cached_state: AudioState | None = None
        self._reconnect_attempts = 0
        self._max_reconnect_attempts = 5

        self._update()

    def _resolve_device(self) -> None:
        """Resolve the current device ID."""
        if self._static_device:
            self._current_device_id = self._static_device
        else:
            resolved = resolve_default_device(self.is_input)
            default = (
                "@DEFAULT_AUDIO_SOURCE@" if self.is_input else "@DEFAULT_AUDIO_SINK@"
            )
            self._current_device_id = resolved or default

    @property
    def device(self) -> str:
        """Get current device ID."""
        return self._current_device_id or (
            "@DEFAULT_AUDIO_SOURCE@" if self.is_input else "@DEFAULT_AUDIO_SINK@"
        )

    def finalize(self) -> None:
        """Clean up on widget destruction."""
        self._stop.set()

        if self._timer:
            self._timer.cancel()
            self._timer = None

        if self._proc:
            try:
                self._proc.terminate()
                self._proc.wait(timeout=0.5)
            except Exception:
                try:
                    self._proc.kill()
                except Exception:
                    pass
            finally:
                self._proc = None

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
        """Monitor wpctl subscribe for changes with automatic reconnection."""
        while not self._stop.is_set():
            try:
                self._listen()
                self._reconnect_attempts = 0  # Reset on successful connection
            except Exception as e:
                self._reconnect_attempts += 1
                logger.error(
                    "wpctl subscribe failed (attempt %d/%d): %s",
                    self._reconnect_attempts,
                    self._max_reconnect_attempts,
                    e,
                )

                # Check for device changes
                if not self._static_device:
                    old_device = self._current_device_id
                    self._resolve_device()
                    if old_device != self._current_device_id:
                        logger.info(
                            "Device changed: %s -> %s",
                            old_device,
                            self._current_device_id,
                        )
                        self._update()

            if not self._stop.is_set():
                # Exponential backoff for reconnection
                delay = min(2.0 ** min(self._reconnect_attempts, 4), 16.0)
                self._stop.wait(delay)

    def _listen(self) -> None:
        """Subscribe to wpctl events with improved event filtering."""
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

                    # Filter relevant events
                    if any(
                        keyword in line
                        for keyword in (
                            "default-node",
                            "volume",
                            "mute",
                            "node",
                            "profile",
                        )
                    ):
                        # Check if device changed (profile switch, device hotplug)
                        if "default-node" in line or "profile" in line:
                            if not self._static_device:
                                old_device = self._current_device_id
                                self._resolve_device()
                                if old_device != self._current_device_id:
                                    logger.info(
                                        "Default device changed: %s -> %s",
                                        old_device,
                                        self._current_device_id,
                                    )

                        self._debounce(self._update, delay=self.update_interval)
        finally:
            self._proc = None
            try:
                proc.terminate()
                proc.wait(timeout=0.5)
            except Exception:
                try:
                    proc.kill()
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
            volume, muted = parse_volume(output)
            state = AudioState(volume=volume, muted=muted, device_id=self.device)
            self._cached_state = state
            return state
        except AudioDeviceError as e:
            logger.debug("Failed to read volume for %s: %s", self.device, e)
            # Try to update device before returning cached state
            if not self._static_device:
                self._resolve_device()
            return self._cached_state or AudioState(0, True, self.device)

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
        except AudioDeviceError as e:
            logger.error("Failed to set volume for %s: %s", self.device, e)

    def _set_mute(self, state: Literal["0", "1", "toggle"]) -> None:
        """Set mute state."""
        try:
            with self._device_lock():
                run(["wpctl", "set-mute", self.device, state], timeout=0.5)
            self._debounce(self._update, delay=0.02)
        except AudioDeviceError as e:
            logger.error("Failed to set mute for %s: %s", self.device, e)

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
        """Refresh display and re-detect device."""
        if not self._static_device:
            self._resolve_device()
        self._update()


class AudioWidget(BaseAudioWidget):
    """Widget for audio output control."""

    def __init__(self, **config: Any) -> None:
        super().__init__(is_input=False, **config)


class MicWidget(BaseAudioWidget):
    """Widget for microphone input control."""

    def __init__(self, **config: Any) -> None:
        super().__init__(is_input=True, **config)
