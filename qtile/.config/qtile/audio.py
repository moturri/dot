import subprocess
import time
from typing import List, Optional, Tuple

from libqtile.widget.base import expose_command
from qtile_extras.widget import GenPollText

# Volume change step (in percent)
VOLUME_STEP = 5


def run(cmd: List[str], timeout: float = 1.0) -> str:
    """Execute command with error handling and timeout."""
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=timeout
        ).strip()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return ""


def parse_volume(output: str) -> Tuple[int, bool]:
    """Parse wpctl volume output into volume level and mute status."""
    try:
        parts = output.split()
        if len(parts) < 2:
            return 0, True
        volume = round(float(parts[1]) * 100)
        muted = "[MUTED]" in output
        return volume, muted
    except (IndexError, ValueError):
        return 0, True


def format_output(icon: str, volume: int, color: str) -> str:
    """Format widget output with icon, volume, and color."""
    return f'<span foreground="{color}">{icon} {volume:3d}%</span>'


class AudioWidget(GenPollText):
    """Audio device widget for both input (mic) and output (volume)."""

    DEFAULTS = {
        "output": {
            "device": "@DEFAULT_AUDIO_SINK@",
            "thresholds": [70, 40, 0],
            "colors": ["salmon", "mediumpurple", "springgreen"],
            "icons": ["󰕾", "󰖀", "󰕿"],
            "muted_icon": "󰝟",
        },
        "input": {
            "device": "@DEFAULT_AUDIO_SOURCE@",
            "thresholds": [70, 40, 0],
            "colors": ["salmon", "mediumpurple", "springgreen"],
            "icons": ["󰍬", "󰍬", "󰍬"],
            "muted_icon": "󰍭",
        },
    }

    def __init__(
        self,
        kind: str = "output",  # "input" for mic, "output" for volume
        device: Optional[str] = None,
        thresholds: Optional[List[int]] = None,
        colors: Optional[List[str]] = None,
        icons: Optional[List[str]] = None,
        muted_icon: Optional[str] = None,
        update_interval: float = 0.5,
        debounce_time: float = 0.1,
        **config,
    ):
        self.kind = kind
        defaults = self.DEFAULTS[kind]

        self.device = device or defaults["device"]
        thresholds = thresholds or defaults["thresholds"]
        colors = colors or defaults["colors"]
        icons = icons or defaults["icons"]
        self.muted_icon = muted_icon or defaults["muted_icon"]

        # Icons, colors paired with thresholds sorted descending for correct matching
        self.icons = sorted(
            zip(thresholds, icons, colors), key=lambda x: x[0], reverse=True
        )
        self.debounce_time = debounce_time

        self._last_output = ""
        self._last_check = 0.0
        self._cached_volume_info: Optional[Tuple[int, bool]] = None
        self._cache_time = 0.0

        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def _get_volume_info(self, use_cache: bool = True) -> Tuple[int, bool]:
        now = time.time()
        if use_cache and self._cached_volume_info and (now - self._cache_time) < 0.5:
            return self._cached_volume_info

        output = run(["wpctl", "get-volume", self.device])
        volume_info = parse_volume(output) if output else (0, True)

        self._cached_volume_info = volume_info
        self._cache_time = now
        return volume_info

    def poll(self) -> str:
        now = time.time()
        if now - self._last_check < self.debounce_time:
            return self._last_output

        self._last_check = now
        volume, muted = self._get_volume_info()

        if volume == 0 and muted:
            result = f'<span foreground="grey">{self.muted_icon}  N/A</span>'
        elif muted:
            result = format_output(self.muted_icon, volume, "dimgrey")
        else:
            icon, color = self.icons[-1][1], self.icons[-1][2]  # Default to lowest
            for threshold, vol_icon, vol_color in self.icons:
                if volume >= threshold:
                    icon, color = vol_icon, vol_color
                    break
            result = format_output(icon, volume, color)

        self._last_output = result
        return result

    def _get_volume(self) -> int:
        volume, _ = self._get_volume_info(use_cache=False)
        return volume

    def _set_volume(self, value: float):
        value = max(0.0, min(value, 1.0))
        run(["wpctl", "set-volume", self.device, f"{value:.2f}"])
        self._cached_volume_info = None

    @expose_command()
    def volume_up(self):
        current = self._get_volume()
        self._set_volume((current + VOLUME_STEP) / 100)

    @expose_command()
    def volume_down(self):
        current = self._get_volume()
        self._set_volume((current - VOLUME_STEP) / 100)

    @expose_command()
    def toggle_mute(self):
        run(["wpctl", "set-mute", self.device, "toggle"])
        self._cached_volume_info = None


class MicWidget(AudioWidget):
    """Mic widget based on AudioWidget but for input devices."""

    def __init__(self, **config):
        super().__init__(kind="input", **config)
