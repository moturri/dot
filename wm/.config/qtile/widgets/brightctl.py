# Copyright (c) 2025 Elton Moturi - MIT License
#
# Brightness widget backed by `brightnessctl`.
#
# Design notes:
# - This module intentionally shells out to `brightnessctl` for portability and
#   to avoid direct sysfs handling or backend-specific APIs.
# - Output parsing and state handling are defensive by design; failures must
#   never crash the Qtile bar.
# - Brightness is presented in percentage terms, derived from hardware-reported
#   maximum values, to preserve a stable user mental model across devices.
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
from typing import Any, Final, Iterator

from libqtile.command.base import expose_command
from libqtile.widget.textbox import TextBox

logger = logging.getLogger(__name__)

ENV: Final[dict[str, str]] = {**os.environ, "LC_ALL": "C.UTF-8"}


class BrightnessError(Exception):
    """Raised when brightness operations fail."""


@dataclass(frozen=True)
class BrightnessLevel:
    """Brightness threshold configuration."""

    threshold: int
    color: str
    icon: str


@dataclass(frozen=True)
class BrightnessState:
    """Current brightness state."""

    current: int
    maximum: int

    @property
    def percentage(self) -> int:
        """Calculate brightness as percentage."""
        if self.maximum <= 0:
            return 0
        return min(100, max(0, (self.current * 100) // self.maximum))


# Default brightness display thresholds: (percentage, color, icon)
# Sorted once here to avoid repeating intent elsewhere.
DEFAULT_ICONS: Final[tuple[tuple[int, str, str], ...]] = tuple(
    sorted(
        (
            (80, "gold", "󰃠"),
            (60, "orange", "󰃝"),
            (40, "tan", "󰃟"),
            (20, "palegreen", "󰃞"),
            (0, "grey", "󰃜"),
        ),
        key=lambda x: -x[0],
    )
)


def require(command: str) -> None:
    """Ensure a required binary exists in PATH."""
    if shutil.which(command) is None:
        raise RuntimeError(f"Missing required dependency: '{command}'")


def run(cmd: list[str], timeout: float = 1.0) -> str:
    """Run an external command safely and return stripped stdout."""
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
        raise BrightnessError(f"Command timeout: {' '.join(cmd)}") from e
    except subprocess.CalledProcessError as e:
        logger.error("Command failed with exit code %s: %s", e.returncode, cmd)
        raise BrightnessError(f"Command failed: {' '.join(cmd)}") from e
    except FileNotFoundError as e:
        logger.error("Command not found: %s", cmd[0])
        raise BrightnessError(f"Command not found: {cmd[0]}") from e
    except Exception as e:
        logger.exception("Unexpected error running command: %s", cmd)
        raise BrightnessError(f"Unexpected error: {' '.join(cmd)}") from e


class BrightctlWidget(TextBox):
    """Qtile widget for controlling brightness via brightnessctl."""

    STEP_MIN: Final[int] = 1
    STEP_MAX: Final[int] = 100
    MIN_BRIGHTNESS_MIN: Final[int] = 1
    MIN_BRIGHTNESS_MAX: Final[int] = 50
    DEBOUNCE_MIN: Final[float] = 0.01
    DEBOUNCE_MAX: Final[float] = 1.0
    COMMAND_TIMEOUT: Final[float] = 0.5
    SET_COMMAND_TIMEOUT: Final[float] = 1.0

    def __init__(
        self,
        step: int = 5,
        min_brightness: int = 1,
        device: str | None = None,
        icons: tuple[tuple[int, str, str], ...] | None = None,
        debounce_interval: float = 0.1,
        **config: Any,
    ) -> None:
        require("brightnessctl")

        self.step = max(self.STEP_MIN, min(step, self.STEP_MAX))
        self.min_brightness = max(
            self.MIN_BRIGHTNESS_MIN, min(min_brightness, self.MIN_BRIGHTNESS_MAX)
        )

        # Note: device hotplug is uncommon for backlight devices; we therefore
        # treat device resolution as static for the widget lifetime.
        self.device = device

        self.debounce_interval = max(
            self.DEBOUNCE_MIN, min(debounce_interval, self.DEBOUNCE_MAX)
        )

        icon_tuples = icons or DEFAULT_ICONS
        self.levels = tuple(
            BrightnessLevel(threshold=t, color=c, icon=i) for t, c, i in icon_tuples
        )

        self._lock = threading.Lock()
        self._max_brightness_cache: int | None = None
        self._update_timer: threading.Timer | None = None
        self._cached_state: BrightnessState | None = None
        self._last_update = 0.0

        super().__init__(text=self._generate_text(), **config)  # type: ignore[no-untyped-call]

    def finalize(self) -> None:
        """Clean up resources on widget destruction."""
        if self._update_timer:
            self._update_timer.cancel()
            self._update_timer = None
        super().finalize()  # type: ignore[no-untyped-call]

    @contextmanager
    def _operation_lock(self) -> Iterator[None]:
        """Context manager for brightness operations with timeout."""
        acquired = self._lock.acquire(timeout=2.0)
        if not acquired:
            raise BrightnessError("Failed to acquire operation lock")
        try:
            yield
        finally:
            self._lock.release()

    def _build_command(self, *args: str) -> list[str]:
        """Build brightnessctl command with optional device argument."""
        cmd = ["brightnessctl"]
        if self.device:
            cmd.extend(["-d", self.device])
        cmd.extend(args)
        return cmd

    def _get_max_brightness(self) -> int:
        """Get and cache maximum brightness value."""
        if self._max_brightness_cache is not None:
            return self._max_brightness_cache

        try:
            output = run(
                self._build_command("max"),
                timeout=self.COMMAND_TIMEOUT,
            )
            max_val = int(output)

            if max_val <= 0:
                raise BrightnessError(f"Invalid max brightness: {max_val}")

            self._max_brightness_cache = max_val
            return max_val

        except (ValueError, BrightnessError) as e:
            logger.exception("Failed to get max brightness")
            raise BrightnessError("Could not determine max brightness") from e

    def _get_current_brightness(self) -> int:
        """Get current brightness raw value."""
        try:
            output = run(
                self._build_command("get"),
                timeout=self.COMMAND_TIMEOUT,
            )
            current = int(output)

            if current < 0:
                raise BrightnessError(f"Invalid brightness value: {current}")

            return current

        except (ValueError, BrightnessError) as e:
            logger.exception("Failed to get current brightness")
            raise BrightnessError("Could not read current brightness") from e

    def _get_state(self) -> BrightnessState:
        """Get current brightness state."""
        try:
            with self._operation_lock():
                current = self._get_current_brightness()
                maximum = self._get_max_brightness()
                state = BrightnessState(current=current, maximum=maximum)
                self._cached_state = state
                return state

        except BrightnessError:
            logger.exception("Failed to get brightness state")
            if self._cached_state:
                return self._cached_state
            # Explicit fallback state: visually distinguishable as error
            return BrightnessState(current=0, maximum=100)

    def _get_icon_style(self, percentage: int) -> tuple[str, str]:
        """Determine color and icon based on brightness percentage."""
        for level in self.levels:
            if percentage >= level.threshold:
                return level.color, level.icon
        return self.levels[-1].color, self.levels[-1].icon

    def _format_text(self, state: BrightnessState) -> str:
        """Format display text based on current state."""
        percentage = state.percentage

        if percentage == 0 and state.current == 0 and state.maximum == 100:
            return '<span foreground="grey">󰃜 N/A</span>'

        color, icon = self._get_icon_style(percentage)
        return f'<span foreground="{color}">{icon}  {percentage}%</span>'

    def _generate_text(self) -> str:
        state = self._get_state()
        return self._format_text(state)

    def _set_brightness_async(self, percentage: int) -> None:
        """Set brightness asynchronously without blocking the UI."""

        def set_brightness() -> None:
            try:
                with self._operation_lock():
                    run(
                        self._build_command("set", f"{percentage}%"),
                        timeout=self.SET_COMMAND_TIMEOUT,
                    )
            except BrightnessError:
                logger.exception(
                    "Failed to set brightness to %s%%",
                    percentage,
                )

        threading.Thread(
            target=set_brightness,
            daemon=True,
            name=f"Brightness-Set-{percentage}",
        ).start()

        self._debounced_update()

    def _debounced_update(self) -> None:
        """Debounce display updates to prevent rapid refreshes."""
        now = time.monotonic()

        def do_update() -> None:
            self._last_update = time.monotonic()
            self.update_display()

        if now - self._last_update >= self.debounce_interval:
            do_update()
            return

        if self._update_timer:
            self._update_timer.cancel()

        self._update_timer = threading.Timer(self.debounce_interval, do_update)
        self._update_timer.daemon = True
        self._update_timer.start()

    def update_display(self) -> None:
        """Refresh the widget display immediately."""
        self.update(self._generate_text())

    def _change_brightness(self, delta: int) -> None:
        """Change brightness by delta, respecting min/max bounds."""
        state = self._get_state()
        new_percentage = state.percentage + delta

        # Minimum brightness is enforced in percentage space by design.
        clamped = max(self.min_brightness, min(new_percentage, 100))
        self._set_brightness_async(clamped)

    # ------------------- Exposed commands -------------------

    @expose_command()
    def increase(self) -> None:
        """Increase brightness by configured step."""
        self._change_brightness(self.step)

    @expose_command()
    def decrease(self) -> None:
        """Decrease brightness by configured step."""
        self._change_brightness(-self.step)

    @expose_command()
    def set_brightness(self, percentage: int) -> None:
        """Set brightness to specific percentage."""
        clamped = max(self.min_brightness, min(percentage, 100))
        self._set_brightness_async(clamped)

    @expose_command()
    def refresh(self) -> None:
        """Manually refresh display."""
        self.update_display()

    def button_press(self, x: int, y: int, button: int) -> None:
        button_actions = {
            2: self.refresh,
            4: self.increase,
            5: self.decrease,
        }
        action = button_actions.get(button)
        if action:
            action()
