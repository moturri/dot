# Copyright (c) 2025 Elton Moturi
# MIT License

import logging
import os
import shutil
import subprocess
from typing import Any, List, Optional, Tuple

from libqtile.command.base import expose_command
from libqtile.widget.textbox import TextBox

logger = logging.getLogger(__name__)

# Thresholds for brightness display: (percentage, color, icon)
DEFAULT_ICONS: Tuple[Tuple[int, str, str], ...] = (
    (80, "gold", "󰃠"),
    (60, "orange", "󰃝"),
    (40, "tan", "󰃟"),
    (20, "palegreen", "󰃞"),
    (0, "grey", "󰃜"),
)


def require(command: str) -> None:
    """Ensure a required binary exists in PATH."""
    if shutil.which(command) is None:
        raise RuntimeError(f"Missing required dependency: '{command}'")


def run(cmd: List[str], timeout: float = 1.0) -> Optional[str]:
    """Run an external command safely and return stripped stdout."""
    try:
        return subprocess.check_output(
            cmd,
            text=True,
            timeout=timeout,
            env={"LC_ALL": "C.UTF-8", **os.environ},
        ).strip()
    except FileNotFoundError:
        logger.error("Command not found: %s", cmd[0])
        return None
    except subprocess.TimeoutExpired:
        logger.warning("Command timed out: %s", " ".join(cmd))
        return None
    except subprocess.SubprocessError as e:
        logger.warning("Command failed: %s -> %s", " ".join(cmd), e)
        return None


class BrightctlWidget(TextBox):
    """Qtile widget for controlling brightness via brightnessctl."""

    def __init__(
        self,
        step: int = 5,
        min_brightness: int = 1,
        device: Optional[str] = None,
        icons: Tuple[Tuple[int, str, str], ...] = DEFAULT_ICONS,
        **config: Any,
    ) -> None:
        require("brightnessctl")
        self.step: int = max(1, min(step, 100))
        self.min_brightness: int = max(1, min(min_brightness, 100))
        self.device: Optional[str] = device
        self.icons: Tuple[Tuple[int, str, str], ...] = icons

        super().__init__(text=self._generate_text(), **config)  # type: ignore[no-untyped-call]

    # ------------------- Core command -------------------
    def _run_brightctl(self, *args: str) -> Optional[str]:
        """Run brightnessctl with optional device argument."""
        cmd: List[str] = ["brightnessctl"]
        if self.device:
            cmd += ["-d", self.device]
        return run(cmd + list(args))

    def _get_brightness(self) -> Optional[int]:
        """Return brightness as a percentage between 0 and 100."""
        current = self._run_brightctl("get")
        maximum = self._run_brightctl("max")
        try:
            cur: int = int(current or 0)
            max_: int = int(maximum or 1)
            if max_ <= 0:
                return None
            return min(100, max(self.min_brightness, (cur * 100) // max_))
        except (TypeError, ValueError):
            return None

    def _set_brightness(self, percent: int) -> None:
        """Clamp brightness and apply it."""
        pct = max(self.min_brightness, min(percent, 100))
        self._run_brightctl("set", f"{pct}%")
        self.update_display()

    def _generate_text(self) -> str:
        """Return the widget display text with icon and percentage."""
        brightness = self._get_brightness()
        if brightness is None:
            return '<span foreground="grey">󰃜 N/A</span>'
        color, icon = next(
            ((c, i) for t, c, i in self.icons if brightness >= t),
            ("grey", "󰃜"),
        )
        return f'<span foreground="{color}">{icon}  {brightness}%</span>'

    def update_display(self) -> None:
        """Refresh the widget display."""
        self.update(self._generate_text())

    def _change_brightness(self, delta: int) -> None:
        """Increase or decrease brightness by delta."""
        current = self._get_brightness()
        if current is not None:
            self._set_brightness(current + delta)

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
    def refresh(self) -> None:
        """Manually refresh display."""
        self.update_display()
