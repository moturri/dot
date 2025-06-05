# Copyright (C) 2025, Elton Moturi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import subprocess
from typing import Any, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText


class AudioWidget(GenPollText):  # type: ignore
    """Minimal PipeWire audio control widget using wpctl."""

    COLORS = {
        "muted": "grey",
        "high": "salmon",
        "medium": "mediumpurple",
        "low": "palegreen",
    }

    ICONS = {
        "muted": "󰝟",
        "high": "󰕾",
        "medium": "󰖀",
        "low": "󰕿",
    }

    def __init__(self, device: str = "@DEFAULT_AUDIO_SINK@", **config: Any) -> None:
        self.device = device
        super().__init__(func=self._poll, update_interval=0.5, **config)

    def _run_cmd(self, cmd: list[str]) -> str:
        """Execute a command and return stdout or empty string."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=0.5)
            return result.stdout.strip() if result.returncode == 0 else ""
        except subprocess.TimeoutExpired:
            return ""

    def _get_volume(self) -> Tuple[int, bool]:
        """Get current volume and mute status."""
        output = self._run_cmd(["wpctl", "get-volume", self.device])
        if not output:
            return 0, True

        parts = output.split()
        try:
            volume = round(float(parts[1]) * 100)
            muted = "[MUTED]" in output
            return volume, muted
        except (IndexError, ValueError):
            return 0, True

    def _poll(self) -> str:
        """Poll volume and return formatted string with Nerd Font icon."""
        volume, muted = self._get_volume()

        if muted:
            color = self.COLORS["muted"]
            icon = self.ICONS["muted"]
        elif volume >= 70:
            color = self.COLORS["high"]
            icon = self.ICONS["high"]
        elif volume >= 40:
            color = self.COLORS["medium"]
            icon = self.ICONS["medium"]
        else:
            color = self.COLORS["low"]
            icon = self.ICONS["low"]

        return f'<span foreground="{color}">{icon}  {volume}%</span>'

    @expose_command()
    def volume_up(self) -> None:
        """Increase volume by 5%."""
        volume, _ = self._get_volume()
        self._run_cmd(["wpctl", "set-volume", self.device, f"{min(100, volume + 5)}%"])

    @expose_command()
    def volume_down(self) -> None:
        """Decrease volume by 5%."""
        volume, _ = self._get_volume()
        self._run_cmd(["wpctl", "set-volume", self.device, f"{max(0, volume - 5)}%"])

    @expose_command()
    def toggle_mute(self) -> None:
        """Toggle mute."""
        self._run_cmd(["wpctl", "set-mute", self.device, "toggle"])


class MicWidget(AudioWidget):
    """Microphone input widget using PipeWire."""

    def __init__(self, **config: Any) -> None:
        super().__init__(device="@DEFAULT_AUDIO_SOURCE@", **config)

    def _poll(self) -> str:
        volume, muted = self._get_volume()

        color = "grey" if muted else "green"
        icon = "󰍭" if muted else "󰍬"

        return f'<span foreground="{color}">{icon}  {volume}%</span>'
