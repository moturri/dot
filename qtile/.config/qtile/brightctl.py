import os
import shutil
import subprocess
from typing import Any, List, Optional, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText

BRIGHTNESS_ICONS = (
    (80, "gold", "󰃠"),
    (60, "orange", "󰃝"),
    (40, "tan", "󰃟"),
    (20, "palegreen", "󰃞"),
    (0, "grey", "󰃜"),
)

class BrightctlWidget(GenPollText):
    """Suckless brightness widget using brightnessctl with exposed commands."""

    def __init__(
        self,
        step: int = 5,
        min_brightness: int = 1,
        update_interval: float = 30.0,
        **config: Any,
    ) -> None:
        if not shutil.which("brightnessctl"):
            raise RuntimeError("brightnessctl not found in PATH")

        self.step = max(1, min(step, 100))
        self.min_brightness = max(1, min(min_brightness, 100))
        self._brightness_before_low = 50
        self._env = {**os.environ, "LC_ALL": "C.UTF-8"}
        self._max_brightness = self._get_max_brightness()

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _run(self, args: List[str]) -> str:
        try:
            return subprocess.run(
                args,
                env=self._env,
                capture_output=True,
                text=True,
                timeout=0.5,
                check=True,
            ).stdout.strip()
        except Exception:
            return ""

    def _get_max_brightness(self) -> int:
        val = self._run(["brightnessctl", "max"])
        try:
            return max(1, int(val))
        except ValueError:
            return 100

    def _get_brightness(self) -> int:
        val = self._run(["brightnessctl", "get"])
        try:
            return (int(val) * 100) // self._max_brightness
        except (ValueError, ZeroDivisionError):
            return 0

    def _set_brightness(self, percent: int) -> None:
        p = max(self.min_brightness, min(100, percent))
        self._run(["brightnessctl", "set", f"{p}%"])
        self.force_update()

    def _get_level(self, brightness: int) -> Tuple[str, str]:
        for threshold, color, icon in BRIGHTNESS_ICONS:
            if brightness > threshold:
                return color, icon
        return BRIGHTNESS_ICONS[-1][1], BRIGHTNESS_ICONS[-1][2]

    def _poll(self) -> str:
        brightness = self._get_brightness()
        color, icon = self._get_level(brightness)
        return f'<span foreground="{color}">{icon}  {brightness}%</span>'

    # Exposed commands
    @expose_command()
    def increase(self) -> None:
        self._set_brightness(self._get_brightness() + self.step)

    @expose_command()
    def decrease(self) -> None:
        self._set_brightness(self._get_brightness() - self.step)

    @expose_command()
    def set(self, percent: int) -> None:
        self._set_brightness(percent)

    @expose_command()
    def toggle_low(self) -> None:
        current = self._get_brightness()
        if current > 15:
            self._brightness_before_low = current
            self._set_brightness(10)
        else:
            self._set_brightness(self._brightness_before_low)

    @expose_command()
    def set_max(self) -> None:
        self._set_brightness(100)

    @expose_command()
    def set_min(self) -> None:
        self._set_brightness(self.min_brightness)

    @expose_command()
    def refresh(self) -> None:
        self.force_update()
