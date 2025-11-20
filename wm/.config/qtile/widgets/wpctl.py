# Copyright (c) 2025 Elton Moturi
# MIT License

import logging
import os
import shutil
import subprocess
import threading
import time
from typing import Any, Callable, Final, cast

from libqtile import qtile as _qtile
from libqtile.bar import Bar
from libqtile.command.base import expose_command
from libqtile.core.manager import Qtile
from libqtile.widget import base

qtile: Qtile = cast(Qtile, _qtile)
logger = logging.getLogger(__name__)


class AudioDeviceError(Exception):
    pass


def require(cmd: str) -> None:
    if shutil.which(cmd) is None:
        raise RuntimeError(f"Missing required dependency: {cmd}")


def run(cmd: list[str], *, timeout: float = 1.0) -> str:
    return subprocess.check_output(
        cmd,
        text=True,
        timeout=timeout,
        env={**os.environ, "LC_ALL": "C.UTF-8"},
    ).strip()


def resolve_default_device(is_input: bool) -> str | None:
    try:
        output = run(["wpctl", "status"], timeout=2)
    except Exception:
        logger.exception("wpctl status failed")
        return None

    lines = output.splitlines()
    target = "Sources:" if is_input else "Sinks:"
    active = False

    for line in lines:
        if target in line:
            active = True
            continue
        if active:
            if not line.startswith(" "):
                break
            if "*" in line:
                for part in line.split():
                    token = part.rstrip(".")
                    if token.isdigit():
                        return token
    return None


class BaseAudioWidget(base._TextBox):

    orientations = base.ORIENTATION_HORIZONTAL

    DEFAULT_OUTPUT: Final[str] = "@DEFAULT_AUDIO_SINK@"
    DEFAULT_INPUT: Final[str] = "@DEFAULT_AUDIO_SOURCE@"

    RECONNECT: Final[float] = 2.5
    STEP_MIN: Final[int] = 1
    STEP_MAX: Final[int] = 25
    MAXVOL_MIN: Final[int] = 50
    MAXVOL_MAX: Final[int] = 150

    SUBSCRIBE_KEYS: Final[tuple[str, ...]] = ("default-node", "volume", "mute")
    DEBOUNCE: Final[float] = 0.05
    USER_DEBOUNCE: Final[float] = 0.02

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

        self.levels = levels or (
            (75, "salmon", "󰕾"),
            (50, "mediumpurple", "󰖀"),
            (25, "lightblue", "󰕿"),
            (0, "palegreen", "󰕿"),
        )
        self.muted_style = muted or ("grey", "󰝟")

        self.device = (
            device
            or resolve_default_device(is_input)
            or (self.DEFAULT_INPUT if is_input else self.DEFAULT_OUTPUT)
        )

        super().__init__("", **config)  # type: ignore[no-untyped-call]

        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._last = 0.0
        self._timer: threading.Timer | None = None

        self._thread: threading.Thread | None = None

        self._update()

    def finalize(self) -> None:

        self._stop.set()

        if self._timer:
            self._timer.cancel()

        if self._thread is not None:
            self._thread.join(timeout=1.0)

        super().finalize()  # type: ignore[no-untyped-call]

    def _configure(self, qtile: Qtile, bar: "Bar") -> None:
        super()._configure(qtile, bar)  # type: ignore[no-untyped-call]
        if self._thread is None:
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                self._listen()
            except Exception:
                logger.exception("wpctl subscribe crashed")
                new = resolve_default_device(self.is_input)
                if new:
                    self.device = new
            if not self._stop.wait(self.RECONNECT):
                continue

    def _listen(self) -> None:
        proc = subprocess.Popen(
            ["wpctl", "subscribe"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )

        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                if self._stop.is_set():
                    break
                if any(k in line for k in self.SUBSCRIBE_KEYS):
                    self._debounce(self._update)
        finally:
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except Exception:
                pass

    def _debounce(self, fn: Callable[[], None], delay: float | None = None) -> None:
        if delay is None:
            delay = self.DEBOUNCE
        now = time.monotonic()

        if now - self._last >= delay:
            self._last = now
            self.qtile.call_soon_threadsafe(fn)
            return

        if self._timer:
            self._timer.cancel()

        def call() -> None:
            self._last = time.monotonic()
            self.qtile.call_soon_threadsafe(fn)

        self._timer = threading.Timer(delay, call)
        self._timer.daemon = True
        self._timer.start()

    def _get_state(self) -> tuple[int, bool]:
        try:
            with self._lock:
                out = run(["wpctl", "get-volume", self.device], timeout=0.6)
        except Exception:
            logger.exception("Failed reading volume for %s", self.device)
            return 0, True
        return self._parse(out)

    @staticmethod
    def _parse(output: str) -> tuple[int, bool]:
        muted = "[MUTED]" in output
        vol = 0
        for token in output.split():
            if any(ch.isdigit() for ch in token):
                try:
                    vol = int(float(token) * 100)
                    break
                except Exception:
                    continue
        vol = max(0, min(150, vol))
        return vol, muted

    def _icon(self, volume: int, muted: bool) -> tuple[str, str]:
        if muted:
            return self.muted_style
        if volume > 100:
            return "gold", self.levels[0][2]
        for threshold, color, icon in self.levels:
            if volume >= threshold:
                return color, icon
        return self.levels[-1][1:]

    def _update(self) -> None:
        volume, muted = self._get_state()
        color, icon = self._icon(volume, muted)
        label = f"{icon}  {volume}%" if self.show_icon else f"{volume}%"
        self.update(f'<span foreground="{color}">{label}</span>')  # type: ignore[no-untyped-call]

    def _set_volume(self, value: int) -> None:
        value = max(0, min(value, self.max_volume))
        try:
            with self._lock:
                run(["wpctl", "set-volume", self.device, f"{value}%"], timeout=0.6)
        except Exception:
            logger.exception("Failed to set volume for %s", self.device)
            return
        self._debounce(self._update, self.USER_DEBOUNCE)

    @expose_command()
    def volume_up(self) -> None:
        vol, _ = self._get_state()
        self._set_volume(vol + self.step)

    @expose_command()
    def volume_down(self) -> None:
        vol, _ = self._get_state()
        self._set_volume(vol - self.step)

    @expose_command()
    def set_volume(self, value: int) -> None:
        self._set_volume(value)

    @expose_command()
    def toggle_mute(self) -> None:
        self._mute("toggle")

    @expose_command()
    def mute(self) -> None:
        self._mute("1")

    @expose_command()
    def unmute(self) -> None:
        self._mute("0")

    def _mute(self, state: str) -> None:
        try:
            with self._lock:
                run(["wpctl", "set-mute", self.device, state], timeout=0.6)
        except Exception:
            logger.exception("mute op failed for %s", self.device)
            return
        self._debounce(self._update, self.USER_DEBOUNCE)

    @expose_command()
    def refresh(self) -> None:
        self._update()


class AudioWidget(BaseAudioWidget):
    def __init__(self, **config: Any) -> None:
        super().__init__(is_input=False, **config)


class MicWidget(BaseAudioWidget):
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
