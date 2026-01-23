# Copyright (c) 2025 Elton Moturi - MIT License
#
# Audio widgets backed by WirePlumber via `wpctl`.
#
# Design notes:
# - This module intentionally shells out to `wpctl` instead of using PipeWire
#   bindings to avoid ABI instability and additional dependencies.
# - Output parsing is defensive by design; unexpected formats must never crash
#   the Qtile bar.
# - Behaviour is tested against wpctl as shipped with PipeWire ≥ 0.3.x.
#
# Icon glyphs assume a Nerd Font–compatible bar font
# (e.g. JetBrainsMono Nerd Font, Iosevka Nerd Font).

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
from enum import Enum
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
    """Raised when audio device operations fail."""


class DeviceType(Enum):
    """Audio device type enumeration."""

    OUTPUT = "output"
    INPUT = "input"


@dataclass(frozen=True, slots=True)
class VolumeLevel:
    """Volume threshold configuration with validation."""

    threshold: int
    color: str
    icon: str

    def __post_init__(self) -> None:
        """Validate volume level configuration."""
        if not 0 <= self.threshold <= 150:
            raise ValueError(f"Invalid threshold: {self.threshold}")
        if not self.color or not isinstance(self.color, str):
            raise ValueError(f"Invalid color: {self.color}")
        if not self.icon or not isinstance(self.icon, str):
            raise ValueError(f"Invalid icon: {self.icon}")


@dataclass(frozen=True, slots=True)
class MutedStyle:
    """Muted state styling with validation."""

    color: str
    icon: str

    def __post_init__(self) -> None:
        """Validate muted style configuration."""
        if not self.color or not isinstance(self.color, str):
            raise ValueError(f"Invalid muted color: {self.color}")
        if not self.icon or not isinstance(self.icon, str):
            raise ValueError(f"Invalid muted icon: {self.icon}")


@dataclass(frozen=True, slots=True)
class AudioState:
    """Current audio device state with validation."""

    volume: int
    muted: bool

    def __post_init__(self) -> None:
        """Validate audio state."""
        if not 0 <= self.volume <= 150:
            object.__setattr__(self, "volume", max(0, min(150, self.volume)))


class WpctlCommand:
    """Centralized wpctl command execution with proper error handling."""

    DEFAULT_TIMEOUT: Final[float] = 1.0
    QUICK_TIMEOUT: Final[float] = 0.5

    @staticmethod
    def require() -> None:
        """Verify wpctl exists in PATH."""
        if shutil.which("wpctl") is None:
            raise RuntimeError(
                "Missing required dependency: wpctl. "
                "Install wireplumber or pipewire-utils."
            )

    @staticmethod
    def execute(args: list[str], *, timeout: float = DEFAULT_TIMEOUT) -> str:
        """Execute wpctl command with comprehensive error handling."""
        cmd = ["wpctl", *args]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=ENV,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.TimeoutExpired as e:
            logger.error("Command timed out after %.2fs: %s", timeout, cmd)
            raise AudioDeviceError(f"Command timeout: {' '.join(cmd)}") from e
        except subprocess.CalledProcessError as e:
            logger.error(
                "Command failed with exit code %d: %s\nstderr: %s",
                e.returncode,
                cmd,
                e.stderr,
            )
            raise AudioDeviceError(
                f"Command failed (exit {e.returncode}): {' '.join(cmd)}"
            ) from e
        except FileNotFoundError as e:
            logger.error("wpctl not found in PATH")
            raise AudioDeviceError("wpctl executable not found") from e
        except Exception as e:
            logger.exception("Unexpected error executing command: %s", cmd)
            raise AudioDeviceError(f"Unexpected error: {' '.join(cmd)}") from e

    @classmethod
    def get_status(cls) -> str:
        """Get wpctl status output."""
        return cls.execute(["status"], timeout=2.0)

    @classmethod
    def get_volume(cls, device: str) -> str:
        """Get volume for specified device."""
        return cls.execute(["get-volume", device], timeout=cls.QUICK_TIMEOUT)

    @classmethod
    def set_volume(cls, device: str, value: str) -> None:
        """Set volume for specified device."""
        cls.execute(["set-volume", device, value], timeout=cls.QUICK_TIMEOUT)

    @classmethod
    def set_mute(cls, device: str, state: Literal["0", "1", "toggle"]) -> None:
        """Set mute state for specified device."""
        cls.execute(["set-mute", device, state], timeout=cls.QUICK_TIMEOUT)


class DeviceResolver:
    """Resolves default audio device IDs from wpctl status."""

    # Regex pattern for device ID extraction: matches numbers followed by optional period
    DEVICE_ID_PATTERN: Final[re.Pattern[str]] = re.compile(r"\b(\d+)\.\s")

    @classmethod
    def resolve_default(cls, device_type: DeviceType) -> str | None:
        """
        Resolve default audio device ID.

        Args:
            device_type: Type of device to resolve (input/output)

        Returns:
            Device ID string or None if not found
        """
        try:
            status = WpctlCommand.get_status()
        except AudioDeviceError:
            logger.exception("Failed to get wpctl status")
            return None

        return cls._parse_status_output(status, device_type)

    @classmethod
    def _parse_status_output(cls, output: str, device_type: DeviceType) -> str | None:
        """Parse wpctl status output to find default device."""
        section_header = "Sources:" if device_type == DeviceType.INPUT else "Sinks:"
        in_target_section = False

        for line in output.splitlines():
            stripped = line.strip()

            # Detect target section
            if section_header in stripped:
                in_target_section = True
                continue

            # Exit when we hit another top-level section
            if in_target_section and line and not line[0].isspace():
                break

            # Look for default device (marked with asterisk)
            if in_target_section and "*" in line:
                match = cls.DEVICE_ID_PATTERN.search(line)
                if match:
                    device_id = match.group(1)
                    logger.debug(
                        "Resolved default %s device: %s",
                        device_type.value,
                        device_id,
                    )
                    return device_id

        logger.warning("No default %s device found", device_type.value)
        return None


class VolumeParser:
    """Parses wpctl volume output into structured state."""

    # Regex for volume value: matches decimal numbers (e.g., 0.75, 1.00)
    VOLUME_PATTERN: Final[re.Pattern[str]] = re.compile(r"\b\d+\.\d+\b")

    @classmethod
    def parse(cls, output: str) -> AudioState:
        """
        Parse wpctl get-volume output.

        Example outputs:
            "Volume: 0.75"
            "Volume: 0.75 [MUTED]"
            "Volume: 1.00 MUTED"

        Args:
            output: Raw wpctl get-volume output

        Returns:
            Parsed AudioState
        """
        muted = "[MUTED]" in output or "MUTED" in output

        match = cls.VOLUME_PATTERN.search(output)
        if match:
            volume_float = float(match.group())
            volume_pct = int(volume_float * 100)
            return AudioState(volume=volume_pct, muted=muted)

        logger.warning("Failed to parse volume from output: %r", output)
        return AudioState(volume=0, muted=muted)


class ProcessManager:
    """Manages subprocess lifecycle with proper cleanup."""

    TERMINATE_TIMEOUT: Final[float] = 0.8
    KILL_TIMEOUT: Final[float] = 0.2

    @classmethod
    def terminate(cls, proc: subprocess.Popen[str]) -> None:
        """Gracefully terminate a subprocess with fallback to kill."""
        if proc.poll() is not None:
            return  # Already terminated

        try:
            proc.terminate()
            proc.wait(timeout=cls.TERMINATE_TIMEOUT)
            logger.debug("Process terminated gracefully")
        except subprocess.TimeoutExpired:
            logger.warning("Process did not terminate, forcing kill")
            try:
                proc.kill()
                proc.wait(timeout=cls.KILL_TIMEOUT)
            except subprocess.TimeoutExpired:
                logger.error("Failed to kill process (PID: %s)", proc.pid)
            except Exception:
                logger.exception("Error during force kill")
        except Exception:
            logger.exception("Error during process termination")


class BaseAudioWidget(base._TextBox):
    """Base widget for audio device control via WirePlumber."""

    orientations = base.ORIENTATION_HORIZONTAL

    # Device identifiers for wpctl
    DEFAULT_OUTPUT: Final[str] = "@DEFAULT_AUDIO_SINK@"
    DEFAULT_INPUT: Final[str] = "@DEFAULT_AUDIO_SOURCE@"

    # Timing constants
    RECONNECT_DELAY: Final[float] = 2.0
    DEBOUNCE_DELAY: Final[float] = 0.05
    USER_DEBOUNCE_DELAY: Final[float] = 0.02
    LOCK_TIMEOUT: Final[float] = 1.0
    THREAD_JOIN_TIMEOUT: Final[float] = 1.0

    # Configuration limits
    STEP_MIN: Final[int] = 1
    STEP_MAX: Final[int] = 25
    MAXVOL_MIN: Final[int] = 50
    MAXVOL_MAX: Final[int] = 150

    # wpctl subscribe event keys to monitor
    SUBSCRIBE_KEYS: Final[tuple[str, ...]] = ("default-node", "volume", "mute")

    def __init__(
        self,
        *,
        device_type: DeviceType,
        device: str | None = None,
        step: int = 5,
        max_volume: int = 100,
        show_icon: bool = True,
        levels: tuple[tuple[int, str, str], ...] | None = None,
        muted: tuple[str, str] | None = None,
        **config: Any,
    ) -> None:
        """
        Initialize audio widget.

        Args:
            device_type: Type of audio device (input/output)
            device: Specific device ID or None for default
            step: Volume change step size (1-25)
            max_volume: Maximum allowed volume (50-150)
            show_icon: Whether to display icon
            levels: Volume level thresholds with colors and icons
            muted: Muted state (color, icon) tuple
            **config: Additional widget configuration
        """
        WpctlCommand.require()

        self.device_type = device_type
        self.step = max(self.STEP_MIN, min(step, self.STEP_MAX))
        self.max_volume = max(self.MAXVOL_MIN, min(max_volume, self.MAXVOL_MAX))
        self.show_icon = show_icon

        # Initialize and validate volume levels
        self.levels = self._init_levels(levels, device_type)
        self.muted_style = self._init_muted_style(muted, device_type)

        # Resolve device ID
        self.device = self._resolve_device(device, device_type)

        super().__init__("", **config)

        # Thread synchronization
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._proc_lock = threading.Lock()

        # State management
        self._last_update = 0.0
        self._timer: threading.Timer | None = None
        self._thread: threading.Thread | None = None
        self._proc: subprocess.Popen[str] | None = None
        self._cached_state: AudioState | None = None
        self._consecutive_errors = 0
        self._max_consecutive_errors = 5

        # Initial update
        self._update()

    def _init_levels(
        self,
        levels: tuple[tuple[int, str, str], ...] | None,
        device_type: DeviceType,
    ) -> tuple[VolumeLevel, ...]:
        """Initialize and validate volume levels."""
        default_levels = (
            (75, "salmon", "󰕾"),
            (50, "mediumpurple", "󰖀"),
            (25, "lightblue", "󰕿"),
            (0, "palegreen", "󰕿"),
        )

        if device_type == DeviceType.INPUT:
            default_levels = (
                (75, "salmon", "󰍬"),
                (50, "mediumpurple", "󰍬"),
                (25, "lightblue", "󰍬"),
                (0, "palegreen", "󰍬"),
            )

        level_tuples = levels or default_levels

        try:
            return tuple(
                VolumeLevel(threshold=t, color=c, icon=i) for t, c, i in level_tuples
            )
        except (ValueError, TypeError) as e:
            logger.error("Invalid volume levels configuration: %s", e)
            raise

    def _init_muted_style(
        self,
        muted: tuple[str, str] | None,
        device_type: DeviceType,
    ) -> MutedStyle:
        """Initialize and validate muted style."""
        default_muted = (
            ("grey", "󰍭") if device_type == DeviceType.INPUT else ("grey", "󰝟")
        )

        muted_tuple = muted or default_muted

        try:
            return MutedStyle(color=muted_tuple[0], icon=muted_tuple[1])
        except (ValueError, TypeError, IndexError) as e:
            logger.error("Invalid muted style configuration: %s", e)
            raise

    def _resolve_device(self, device: str | None, device_type: DeviceType) -> str:
        """Resolve device ID with fallback to default."""
        if device:
            return device

        resolved = DeviceResolver.resolve_default(device_type)
        if resolved:
            return resolved

        # Fallback to wpctl symbolic name
        default_device = (
            self.DEFAULT_INPUT
            if device_type == DeviceType.INPUT
            else self.DEFAULT_OUTPUT
        )
        logger.warning(
            "Could not resolve default %s device, using symbolic: %s",
            device_type.value,
            default_device,
        )
        return default_device

    def finalize(self) -> None:
        """Clean up resources on widget destruction."""
        logger.debug("Finalizing %s widget", self.device_type.value)

        self._stop.set()

        # Cancel pending timer
        if self._timer:
            self._timer.cancel()
            self._timer = None

        # Terminate subprocess
        with self._proc_lock:
            if self._proc:
                ProcessManager.terminate(self._proc)
                self._proc = None

        # Wait for monitor thread
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.THREAD_JOIN_TIMEOUT)
            if self._thread.is_alive():
                logger.warning(
                    "%s monitor thread did not terminate cleanly",
                    self.device_type.value,
                )
            self._thread = None

        super().finalize()

    def _configure(self, qtile: Qtile, bar: Bar) -> None:
        """Configure widget and start monitoring thread."""
        super()._configure(qtile, bar)

        if self._thread is None:
            self._thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name=f"AudioWidget-{self.device_type.value.capitalize()}",
            )
            self._thread.start()
            logger.debug("Started monitor thread for %s", self.device_type.value)

    def _monitor_loop(self) -> None:
        """Main monitoring loop for wpctl subscribe events."""
        while not self._stop.is_set():
            try:
                self._listen_to_events()
                self._consecutive_errors = 0  # Reset on successful run
            except Exception as e:
                self._consecutive_errors += 1
                logger.error(
                    "wpctl subscribe crashed for %s device (%s: %s), " "attempt %d/%d",
                    self.device_type.value,
                    type(e).__name__,
                    e,
                    self._consecutive_errors,
                    self._max_consecutive_errors,
                )

                # Check if device changed
                new_device = DeviceResolver.resolve_default(self.device_type)
                if new_device and new_device != self.device:
                    logger.info(
                        "Switching %s device: %s -> %s",
                        self.device_type.value,
                        self.device,
                        new_device,
                    )
                    self.device = new_device
                    self._update()

                # Back off if too many consecutive errors
                if self._consecutive_errors >= self._max_consecutive_errors:
                    logger.error(
                        "Too many consecutive errors, stopping monitor for %s",
                        self.device_type.value,
                    )
                    break

            if not self._stop.is_set():
                self._stop.wait(self.RECONNECT_DELAY)

    def _listen_to_events(self) -> None:
        """Listen to wpctl subscribe events and trigger updates."""
        proc = subprocess.Popen(
            ["wpctl", "subscribe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
            env=ENV,
        )

        with self._proc_lock:
            self._proc = proc

        try:
            if proc.stdout is None:
                raise AudioDeviceError("Failed to capture wpctl subscribe output")

            for line in proc.stdout:
                if self._stop.is_set():
                    break

                # Check if line contains relevant event
                if any(key in line for key in self.SUBSCRIBE_KEYS):
                    self._debounce(self._update)

        finally:
            with self._proc_lock:
                self._proc = None
            ProcessManager.terminate(proc)

    def _debounce(self, fn: Callable[[], None], delay: float | None = None) -> None:
        """
        Debounce function calls to avoid excessive updates.

        Args:
            fn: Function to call
            delay: Debounce delay in seconds (uses default if None)
        """
        delay = delay or self.DEBOUNCE_DELAY
        now = time.monotonic()

        def invoke() -> None:
            self._last_update = time.monotonic()
            try:
                self.qtile.call_soon_threadsafe(fn)
            except Exception:
                logger.exception("Error in debounced callback")

        # Execute immediately if enough time has passed
        if now - self._last_update >= delay:
            invoke()
            return

        # Otherwise, schedule for later
        if self._timer:
            self._timer.cancel()

        self._timer = threading.Timer(delay, invoke)
        self._timer.daemon = True
        self._timer.start()

    @contextmanager
    def _device_lock(self) -> Iterator[None]:
        """Context manager for device operations with timeout."""
        acquired = self._lock.acquire(timeout=self.LOCK_TIMEOUT)
        if not acquired:
            raise AudioDeviceError(
                f"Failed to acquire device lock after {self.LOCK_TIMEOUT}s"
            )
        try:
            yield
        finally:
            self._lock.release()

    def _get_state(self) -> AudioState:
        """
        Get current audio device state.

        Returns:
            Current AudioState or cached state on error
        """
        try:
            with self._device_lock():
                raw_output = WpctlCommand.get_volume(self.device)

            state = VolumeParser.parse(raw_output)
            self._cached_state = state
            return state

        except AudioDeviceError:
            logger.exception("Failed reading volume for device %s", self.device)
            # Return cached state or safe default
            return self._cached_state or AudioState(volume=0, muted=True)

    def _get_icon_style(self, state: AudioState) -> tuple[str, str]:
        """
        Determine icon color and glyph based on state.

        Args:
            state: Current audio state

        Returns:
            Tuple of (color, icon)
        """
        if state.muted:
            return self.muted_style.color, self.muted_style.icon

        # Highlight amplification above 100% to prevent clipping
        if state.volume > 100:
            return "gold", self.levels[0].icon

        # Find matching threshold level
        for level in self.levels:
            if state.volume >= level.threshold:
                return level.color, level.icon

        return self.levels[-1].color, self.levels[-1].icon

    def _format_text(self, state: AudioState) -> str:
        """
        Format widget text with color and icon.

        Args:
            state: Current audio state

        Returns:
            Formatted HTML string
        """
        color, icon = self._get_icon_style(state)

        if self.show_icon:
            text = f"{icon}  {state.volume}%"
        else:
            text = f"{state.volume}%"

        return f'<span foreground="{color}">{text}</span>'

    def _update(self) -> None:
        """Update widget display with current state."""
        state = self._get_state()
        self.update(self._format_text(state))

    def button_press(self, x: int, y: int, button: int) -> None:
        """
        Handle mouse button presses.

        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button number
        """
        button_actions: dict[int, Callable[[], None]] = {
            2: self.refresh,  # Middle click: refresh
            3: self.toggle_mute,  # Right click: toggle mute
            4: self.volume_up,  # Scroll up: increase volume
            5: self.volume_down,  # Scroll down: decrease volume
        }

        action = button_actions.get(button)
        if action:
            try:
                action()
            except Exception:
                logger.exception("Error handling button press: button=%d", button)

    def _set_volume(self, value: int) -> None:
        """
        Set volume to specific value.

        Args:
            value: Target volume percentage
        """
        value = max(0, min(value, self.max_volume))

        try:
            with self._device_lock():
                WpctlCommand.set_volume(self.device, f"{value}%")

            self._debounce(self._update, self.USER_DEBOUNCE_DELAY)

        except AudioDeviceError:
            logger.exception("Failed to set volume for device %s", self.device)

    @expose_command()
    def volume_up(self) -> None:
        """Increase volume by step amount."""
        state = self._get_state()
        self._set_volume(state.volume + self.step)

    @expose_command()
    def volume_down(self) -> None:
        """Decrease volume by step amount."""
        state = self._get_state()
        self._set_volume(state.volume - self.step)

    @expose_command()
    def set_volume(self, value: int) -> None:
        """
        Set volume to absolute value.

        Args:
            value: Target volume percentage (0-max_volume)
        """
        self._set_volume(value)

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

    def _set_mute(self, state: Literal["0", "1", "toggle"]) -> None:
        """
        Set mute state.

        Args:
            state: Mute state ("0", "1", or "toggle")
        """
        try:
            with self._device_lock():
                WpctlCommand.set_mute(self.device, state)

            self._debounce(self._update, self.USER_DEBOUNCE_DELAY)

        except AudioDeviceError:
            logger.exception("Mute operation failed for device %s", self.device)

    @expose_command()
    def refresh(self) -> None:
        """Manually refresh widget state."""
        self._update()


class AudioWidget(BaseAudioWidget):
    """Widget for controlling audio output volume."""

    def __init__(self, **config: Any) -> None:
        """
        Initialize audio output widget.

        Args:
            **config: Widget configuration options
        """
        super().__init__(device_type=DeviceType.OUTPUT, **config)


class MicWidget(BaseAudioWidget):
    """Widget for controlling microphone input volume."""

    def __init__(self, **config: Any) -> None:
        """
        Initialize microphone input widget.

        Args:
            **config: Widget configuration options
        """
        super().__init__(device_type=DeviceType.INPUT, **config)
