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

    def __init__(
        self,
        device: str = "@DEFAULT_AUDIO_SINK@",
        step: int = 5,
        max_volume: int = 100,
        **config: Any,
    ) -> None:
        self.device = device
        self.step = max(1, min(25, step))  # Reasonable step bounds
        self.max_volume = max(50, min(150, max_volume))  # Allow up to 150% but cap it
        super().__init__(func=self._poll, update_interval=0.5, **config)

    def _run_cmd(self, cmd: list[str]) -> str:
        """Execute wpctl command with error handling."""
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=1.0, check=False
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except (subprocess.TimeoutExpired, OSError):
            return ""

    def _get_volume(self) -> Tuple[int, bool]:
        """Get current volume percentage and mute status."""
        output = self._run_cmd(["wpctl", "get-volume", self.device])
        if not output:
            return 0, True

        try:
            parts = output.split()
            if len(parts) < 2:
                return 0, True

            # wpctl returns volume as 0.XX format
            volume = round(float(parts[1]) * 100)
            muted = "[MUTED]" in output

            # Clamp volume to reasonable range
            volume = max(0, min(200, volume))

            return volume, muted

        except (IndexError, ValueError, TypeError):
            return 0, True

    def _get_volume_level(self, volume: int, muted: bool) -> Tuple[str, str]:
        """Determine appropriate color and icon for volume level."""
        if muted:
            return self.COLORS["muted"], self.ICONS["muted"]
        elif volume >= 70:
            return self.COLORS["high"], self.ICONS["high"]
        elif volume >= 40:
            return self.COLORS["medium"], self.ICONS["medium"]
        else:
            return self.COLORS["low"], self.ICONS["low"]

    def _poll(self) -> str:
        """Poll volume and return formatted display string."""
        volume, muted = self._get_volume()
        color, icon = self._get_volume_level(volume, muted)

        # Show visual indicator if volume is over 100%
        volume_display = f"{volume}%" if volume <= 100 else f"{volume}%!"

        return f'<span foreground="{color}">{icon}  {volume_display}</span>'

    def _set_volume(self, target_volume: int) -> bool:
        """Set volume to specific percentage with bounds checking."""
        target_volume = max(0, min(self.max_volume, target_volume))

        # Use wpctl's percentage format
        result = self._run_cmd(
            ["wpctl", "set-volume", self.device, f"{target_volume}%"]
        )

        # Return success if command executed (wpctl doesn't return output on success)
        return result == "" or "%" in result

    @expose_command()
    def volume_up(self) -> None:
        """Increase volume by step amount."""
        volume, _ = self._get_volume()
        self._set_volume(volume + self.step)

    @expose_command()
    def volume_down(self) -> None:
        """Decrease volume by step amount."""
        volume, _ = self._get_volume()
        self._set_volume(volume - self.step)

    @expose_command()
    def toggle_mute(self) -> None:
        """Toggle mute status."""
        self._run_cmd(["wpctl", "set-mute", self.device, "toggle"])

    @expose_command()
    def set_volume(self, percent: int) -> None:
        """Set volume to specific percentage."""
        self._set_volume(percent)

    @expose_command()
    def mute(self) -> None:
        """Mute audio."""
        self._run_cmd(["wpctl", "set-mute", self.device, "1"])

    @expose_command()
    def unmute(self) -> None:
        """Unmute audio."""
        self._run_cmd(["wpctl", "set-mute", self.device, "0"])


class MicWidget(AudioWidget):
    """Microphone input widget using PipeWire."""

    MIC_COLORS = {
        "muted": "grey",
        "active": "palegreen",
        "hot": "red",  # For high input levels
    }

    MIC_ICONS = {
        "muted": "󰍭",
        "active": "󰍬",
        "hot": "󰍬",
    }

    def __init__(self, **config: Any) -> None:
        # Override default device for microphone
        config.setdefault("device", "@DEFAULT_AUDIO_SOURCE@")
        super().__init__(**config)

    def _get_volume_level(self, volume: int, muted: bool) -> Tuple[str, str]:
        """Determine appropriate color and icon for microphone level."""
        if muted:
            return self.MIC_COLORS["muted"], self.MIC_ICONS["muted"]
        elif volume >= 90:  # High input levels might cause distortion
            return self.MIC_COLORS["hot"], self.MIC_ICONS["hot"]
        else:
            return self.MIC_COLORS["active"], self.MIC_ICONS["active"]

    def _poll(self) -> str:
        """Poll microphone and return formatted display string."""
        volume, muted = self._get_volume()
        color, icon = self._get_volume_level(volume, muted)

        return f'<span foreground="{color}">{icon}  {volume}%</span>'


class AudioManager:
    """Helper class for managing multiple audio devices."""

    @staticmethod
    def get_devices(device_type: str = "sink") -> list[str]:
        """Get list of available audio devices."""
        try:
            cmd = ["wpctl", "status"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=2.0)

            if result.returncode != 0:
                return []

            lines = result.stdout.split("\n")
            devices = []
            in_section = False

            section_name = "Sinks:" if device_type == "sink" else "Sources:"

            for line in lines:
                if section_name in line:
                    in_section = True
                    continue
                elif line.strip() and not line.startswith(" ") and in_section:
                    break
                elif in_section and "│" in line:
                    # Extract device info from wpctl status output
                    parts = line.split("│")
                    if len(parts) >= 2:
                        device_info = parts[1].strip()
                        if (
                            device_info
                            and not device_info.startswith("├")
                            and not device_info.startswith("└")
                        ):
                            devices.append(device_info)

            return devices

        except (subprocess.TimeoutExpired, OSError):
            return []

    @staticmethod
    def switch_device(device_id: str) -> bool:
        """Switch to a specific audio device."""
        try:
            result = subprocess.run(
                ["wpctl", "set-default", device_id], capture_output=True, timeout=1.0
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, OSError):
            return False
