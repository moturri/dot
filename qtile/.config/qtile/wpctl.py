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
    """Minimal PipeWire audio control widget."""

    def __init__(self, device: str = "@DEFAULT_AUDIO_SINK@", **config: Any) -> None:
        self.device = device
        super().__init__(func=self._poll, update_interval=0.5, **config)

    def _run_cmd(self, cmd: list[str]) -> str:
        """Execute wpctl command and return output."""
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1.0)
            return result.stdout.strip() if result.returncode == 0 else ""
        except subprocess.TimeoutExpired:
            return ""

    def _get_volume(self) -> Tuple[int, bool]:
        """Get current volume and mute status."""
        output = self._run_cmd(["wpctl", "get-volume", self.device])
        if not output:
            return 0, True

        parts = output.split()
        if len(parts) < 2:
            return 0, True

        try:
            volume = round(float(parts[1]) * 100)
            muted = "[MUTED]" in output
            return volume, muted
        except ValueError:
            return 0, True

    def _poll(self) -> str:
        """Poll volume and format display."""
        volume, muted = self._get_volume()

        if muted:
            color = "#666666"
            icon = "󰝟"
        elif volume >= 70:
            color = "#ff5555"
            icon = "󰕾"
        elif volume >= 40:
            color = "#bd93f9"
            icon = "󰖀"
        else:
            color = "#50fa7b"
            icon = "󰕿"

        return f'<span foreground="{color}">{icon}  {volume}%</span>'

    @expose_command()
    def volume_up(self) -> None:
        """Increase volume by 5%."""
        volume, _ = self._get_volume()
        new_vol = min(100, volume + 5)
        self._run_cmd(["wpctl", "set-volume", self.device, f"{new_vol}%"])

    @expose_command()
    def volume_down(self) -> None:
        """Decrease volume by 5%."""
        volume, _ = self._get_volume()
        new_vol = max(0, volume - 5)
        self._run_cmd(["wpctl", "set-volume", self.device, f"{new_vol}%"])

    @expose_command()
    def toggle_mute(self) -> None:
        """Toggle mute status."""
        self._run_cmd(["wpctl", "set-mute", self.device, "toggle"])


class MicWidget(AudioWidget):
    """Microphone input widget."""

    def __init__(self, **config: Any) -> None:
        super().__init__(device="@DEFAULT_AUDIO_SOURCE@", **config)

    def _poll(self) -> str:
        """Poll microphone volume with input-specific icons."""
        volume, muted = self._get_volume()

        if muted:
            color = "dimgrey"
            icon = "󰍭"
        else:
            color = "#50fa7b"
            icon = "󰍬"

        return f'<span foreground="{color}">{icon}  {volume}%</span>'
