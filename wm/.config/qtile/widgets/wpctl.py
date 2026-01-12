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
    """Raised when audio device operations fail."""


@dataclass(frozen=True)
class VolumeLevel:
    """Volume threshold configuration."""

    threshold: int
    color: str
    icon: str


@dataclass(frozen=True)
class MutedStyle:
    """Muted state styling."""

    color: str
    icon: str


@dataclass(frozen=True)
class AudioState:
    """Current audio device state."""

    volume: int
    muted: bool


def require(cmd: str) -> None:
    """Verify required command exists in PATH."""
    if shutil.which(cmd) is None:
        raise RuntimeError(f"Missing required dependency: {cmd}")


def run(cmd: list[str], *, timeout: float = 1.0) -> str:
    """Execute command and return output."""
    try:
        return subprocess.check_output(
            cmd,
            text=True,
            timeout=timeout,
            stderr=subprocess.DEVNULL,
            env=ENV,
        ).strip()
    except subprocess.TimeoutExpired as e:
        logger.error("Command timed out after %ss: %s", timeout, cmd)
        raise AudioDeviceError(f"Command timeout: {' '.join(cmd)}") from e
    except subprocess.CalledProcessError as e:
        logger.error("Command failed with exit code %s: %s", e.returncode, cmd)
        raise AudioDeviceError(f"Command failed: {' '.join(cmd)}") from e
    except Exception as e:
        logger.exception("Unexpected error running command: %s", cmd)
        raise AudioDeviceError(f"Unexpected error: {' '.join(cmd)}") from e


def resolve_default_device(is_input: bool) -> str | None:
    """Resolve default audio device ID from wpctl status."""
    try:
        out = run(["wpctl", "status"], timeout=2)
    except AudioDeviceError:
        logger.exception("wpctl status failed")
        return None

    target = "Sources:" if is_input else "Sinks:"
    active = False

    for line in out.splitlines():
        line_stripped = line.strip()

        if target in line_stripped:
            active = True
            continue

        if active:
            if "*" in line:
                for token in line.split():
                    t = token.strip(".")
                    if t.isdigit():
                        return t
            # Exit section when indentation ends (next top-level header)
            if line and not line.startswith(" "):
                break

    return None


def parse_volume_output(output: str) -> AudioState:
    """Parse wpctl volume output into AudioState."""
    muted = "[MUTED]" in output

    for token in output.split():
        if token.replace(".", "", 1).isdigit():
            vol = int(float(token) * 100)
            vol = max(0, min(150, vol))
            return AudioState(volume=vol, muted=muted)

    return AudioState(volume=0, muted=muted)


class BaseAudioWidget(base._TextBox):
    """Base widget for audio device control via WirePlumber."""

    orientations = base.ORIENTATION_HORIZONTAL

    DEFAULT_OUTPUT: Final[str] = "@DEFAULT_AUDIO_SINK@"
    DEFAULT_INPUT: Final[str] = "@DEFAULT_AUDIO_SOURCE@"

    RECONNECT_DELAY: Final[float] = 2.0
    STEP_MIN: Final[int] = 1
    STEP_MAX: Final[int] = 25
    MAXVOL_MIN: Final[int] = 50
    MAXVOL_MAX: Final[int] = 150

    SUBSCRIBE_KEYS: Final[tuple[str, ...]] = ("default-node", "volume", "mute")
    DEBOUNCE_DELAY: Final[float] = 0.05
    USER_DEBOUNCE_DELAY: Final[float] = 0.02

    PROCESS_TERMINATE_TIMEOUT: Final[float] = 0.8
    THREAD_JOIN_TIMEOUT: Final[float] = 1.0

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
        self.step = max(self.STEP_MIN, min(step, self.STEP_MAX))
        self.max_volume = max(self.MAXVOL_MIN, min(max_volume, self.MAXVOL_MAX))
        self.show_icon = show_icon

        self.levels = tuple(
            VolumeLevel(threshold=t, color=c, icon=i)
            for t, c, i in (
                levels
                or (
                    (75, "salmon", "󰕾"),
                    (50, "mediumpurple", "󰖀"),
                    (25, "lightblue", "󰕿"),
                    (0, "palegreen", "󰕿"),
                )
            )
        )

        muted_tuple = muted or ("grey", "󰝟")
        self.muted_style = MutedStyle(color=muted_tuple[0], icon=muted_tuple[1])

        resolved = resolve_default_device(is_input)
        self.device = (
            device
            or resolved
            or (self.DEFAULT_INPUT if is_input else self.DEFAULT_OUTPUT)
        )

        super().__init__("", **config)  # type: ignore[no-untyped-call]

        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last_update = 0.0
        self._timer: threading.Timer | None = None
        self._thread: threading.Thread | None = None
        self._proc: subprocess.Popen[str] | None = None
        self._proc_lock = threading.Lock()
        self._cached_state: AudioState | None = None

        self._update()

    def finalize(self) -> None:
        self._stop.set()

        if self._timer:
            self._timer.cancel()
            self._timer = None

        with self._proc_lock:
            if self._proc:
                self._terminate_process(self._proc)

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=self.THREAD_JOIN_TIMEOUT)
            if self._thread.is_alive():
                logger.warning("Monitor thread did not terminate cleanly")
            self._thread = None

        super().finalize()  # type: ignore[no-untyped-call]

    def _configure(self, qtile: Qtile, bar: Bar) -> None:
        super()._configure(qtile, bar)  # type: ignore[no-untyped-call]
        if self._thread is None:
            self._thread = threading.Thread(
                target=self._loop,
                daemon=True,
                name=f"AudioWidget-{'Input' if self.is_input else 'Output'}",
            )
            self._thread.start()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._listen()
            except Exception as e:
                logger.error(
                    "wpctl subscribe crashed for %s device (%s: %s), attempting recovery",
                    "input" if self.is_input else "output",
                    type(e).__name__,
                    e,
                )
                new = resolve_default_device(self.is_input)
                if new and new != self.device:
                    logger.info("Switching to new default device: %s", new)
                    self.device = new
                    self._update()

            if not self._stop.is_set():
                self._stop.wait(self.RECONNECT_DELAY)

    def _listen(self) -> None:
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
                logger.error("Failed to capture wpctl subscribe output")
                return

            for line in proc.stdout:
                if self._stop.is_set():
                    break
                if any(key in line for key in self.SUBSCRIBE_KEYS):
                    self._debounce(self._update)
        finally:
            with self._proc_lock:
                self._proc = None
            self._terminate_process(proc)

    def _terminate_process(self, proc: subprocess.Popen[str]) -> None:
        try:
            proc.terminate()
            proc.wait(timeout=self.PROCESS_TERMINATE_TIMEOUT)
        except subprocess.TimeoutExpired:
            logger.warning("Process did not terminate, killing forcefully")
            proc.kill()
            try:
                proc.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                logger.error("Failed to kill process")
        except Exception:
            logger.debug("Exception during process termination", exc_info=True)

    def _debounce(self, fn: Callable[[], None], delay: float | None = None) -> None:
        delay = delay or self.DEBOUNCE_DELAY
        now = time.monotonic()

        def invoke() -> None:
            self._last_update = time.monotonic()
            self.qtile.call_soon_threadsafe(fn)

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
        acquired = self._lock.acquire(timeout=1.0)
        if not acquired:
            raise AudioDeviceError("Failed to acquire device lock")
        try:
            yield
        finally:
            self._lock.release()

    def _get_state(self) -> AudioState:
        try:
            with self._device_lock():
                raw = run(["wpctl", "get-volume", self.device], timeout=0.5)
            state = parse_volume_output(raw)
            self._cached_state = state
            return state
        except AudioDeviceError:
            logger.exception("Failed reading volume for %s", self.device)
            return self._cached_state or AudioState(volume=0, muted=True)

    def _get_icon_style(self, state: AudioState) -> tuple[str, str]:
        if state.muted:
            return self.muted_style.color, self.muted_style.icon

        # PipeWire allows amplification above 100%;
        # visually distinguish this to avoid accidental clipping.
        if state.volume > 100:
            return "gold", self.levels[0].icon

        for level in self.levels:
            if state.volume >= level.threshold:
                return level.color, level.icon

        return self.levels[-1].color, self.levels[-1].icon

    def _format_text(self, state: AudioState) -> str:
        color, icon = self._get_icon_style(state)

        if self.show_icon:
            text = f"{icon}  {state.volume}%"
        else:
            text = f"{state.volume}%"

        return f'<span foreground="{color}">{text}</span>'

    def _update(self) -> None:
        state = self._get_state()
        self.update(self._format_text(state))  # type: ignore[no-untyped-call]

    def button_press(self, x: int, y: int, button: int) -> None:
        button_actions: dict[int, Callable[[], None]] = {
            2: self.refresh,
            3: self.toggle_mute,
            4: self.volume_up,
            5: self.volume_down,
        }
        action = button_actions.get(button)
        if action:
            action()

    def _set_volume(self, value: int) -> None:
        value = max(0, min(value, self.max_volume))
        try:
            with self._device_lock():
                run(
                    ["wpctl", "set-volume", self.device, f"{value}%"],
                    timeout=0.5,
                )
            self._debounce(self._update, self.USER_DEBOUNCE_DELAY)
        except AudioDeviceError:
            logger.exception("Failed to set volume for %s", self.device)

    @expose_command()
    def volume_up(self) -> None:
        state = self._get_state()
        self._set_volume(state.volume + self.step)

    @expose_command()
    def volume_down(self) -> None:
        state = self._get_state()
        self._set_volume(state.volume - self.step)

    @expose_command()
    def set_volume(self, value: int) -> None:
        self._set_volume(value)

    @expose_command()
    def toggle_mute(self) -> None:
        self._set_mute("toggle")

    @expose_command()
    def mute(self) -> None:
        self._set_mute("1")

    @expose_command()
    def unmute(self) -> None:
        self._set_mute("0")

    def _set_mute(self, state: Literal["0", "1", "toggle"]) -> None:
        try:
            with self._device_lock():
                run(
                    ["wpctl", "set-mute", self.device, state],
                    timeout=0.5,
                )
            self._debounce(self._update, self.USER_DEBOUNCE_DELAY)
        except AudioDeviceError:
            logger.exception("Mute operation failed for %s", self.device)

    @expose_command()
    def refresh(self) -> None:
        self._update()


class AudioWidget(BaseAudioWidget):
    """Widget for controlling audio output volume."""

    def __init__(self, **config: Any) -> None:
        super().__init__(is_input=False, **config)


class MicWidget(BaseAudioWidget):
    """Widget for controlling microphone input volume."""

    def __init__(self, **config: Any) -> None:
        levels = (
            (75, "salmon", "󰍬"),
            (50, "mediumpurple", "󰍬"),
            (25, "lightblue", "󰍬"),
            (0, "palegreen", "󰍬"),
        )
        super().__init__(
            is_input=True,
            levels=levels,
            muted=("grey", "󰍭"),
            **config,
        )
