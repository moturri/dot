import subprocess
import time
from typing import Any, Dict, List, Optional, Tuple, cast

from libqtile.widget.base import expose_command
from qtile_extras.widget import GenPollText

# Constants
VOLUME_STEP = 5
CACHE_TIMEOUT = 0.5
DEBOUNCE_TIMEOUT = 0.1
CMD_TIMEOUT = 1.0

# Configurable settings
VOLUME_CONFIG: Dict[str, Dict[str, Any]] = {
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


def run_cmd(cmd: List[str]) -> str:
    """Run a command and return output (fail quietly)."""
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=CMD_TIMEOUT
        ).strip()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ):
        return ""


def parse_wpctl_output(output: str) -> Tuple[int, bool]:
    """Extract volume (0–100) and mute status from wpctl."""
    try:
        parts = output.split()
        volume = int(float(parts[1]) * 100)
        muted = "[MUTED]" in output
        return volume, muted
    except (IndexError, ValueError):
        return 0, True


class AudioWidget(GenPollText):
    """Minimal volume widget for Qtile (output or input)."""

    def __init__(
        self,
        kind: str = "output",  # or "input"
        device: Optional[str] = None,
        update_interval: float = 0.5,
        **config,
    ):
        self.kind = kind
        self.config = VOLUME_CONFIG[kind]
        self.device = device or self.config["device"]

        # Explicitly cast thresholds, icons, colors to lists of expected types
        thresholds = cast(List[int], self.config["thresholds"])
        icons = cast(List[str], self.config["icons"])
        colors = cast(List[str], self.config["colors"])

        self._icon_map: List[Tuple[int, str, str]] = list(
            zip(thresholds, icons, colors)
        )
        self._icon_map.sort(key=lambda x: x[0], reverse=True)

        self._cache: Optional[Tuple[int, bool, float]] = None
        self._last_poll_time: float = 0.0

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_volume_info(self, force_refresh: bool = False) -> Tuple[int, bool]:
        """Return (volume, muted). Use cache unless forced."""
        now = time.time()

        if not force_refresh and self._cache:
            volume, muted, cache_time = self._cache
            if now - cache_time < CACHE_TIMEOUT:
                return volume, muted

        output = run_cmd(["wpctl", "get-volume", self.device])
        if output:
            volume, muted = parse_wpctl_output(output)
            self._cache = (volume, muted, now)
            return volume, muted

        return 0, True  # fallback

    def _format_display(self, volume: int, muted: bool) -> str:
        """Format text for display."""
        if volume == 0 and muted:
            return f'<span foreground="grey">{self.config["muted_icon"]}  N/A</span>'

        if muted:
            return f'<span foreground="dimgrey">{self.config["muted_icon"]} {volume:3d}%</span>'

        for threshold, icon, color in self._icon_map:
            if volume >= threshold:
                return f'<span foreground="{color}">{icon} {volume:3d}%</span>'

        # Fallback (lowest threshold)
        fallback_icon, fallback_color = self._icon_map[-1][1], self._icon_map[-1][2]
        return (
            f'<span foreground="{fallback_color}">{fallback_icon} {volume:3d}%</span>'
        )

    def _poll(self) -> str:
        now = time.time()
        if now - self._last_poll_time < DEBOUNCE_TIMEOUT:
            return self.text or ""

        self._last_poll_time = now
        volume, muted = self._get_volume_info()
        return self._format_display(volume, muted)

    def _execute_volume_cmd(self, cmd: List[str]):
        run_cmd(cmd)
        self._cache = None  # invalidate cache

    # Exposed Commands (for scripting and keybindings)

    @expose_command()
    def volume_up(self):
        volume, _ = self._get_volume_info(force_refresh=True)
        new_volume = min(100, volume + VOLUME_STEP) / 100
        self._execute_volume_cmd(
            ["wpctl", "set-volume", self.device, f"{new_volume:.2f}"]
        )

    @expose_command()
    def volume_down(self):
        volume, _ = self._get_volume_info(force_refresh=True)
        new_volume = max(0, volume - VOLUME_STEP) / 100
        self._execute_volume_cmd(
            ["wpctl", "set-volume", self.device, f"{new_volume:.2f}"]
        )

    @expose_command()
    def toggle_mute(self):
        self._execute_volume_cmd(["wpctl", "set-mute", self.device, "toggle"])

    @expose_command()
    def get_state(self) -> Dict[str, Any]:
        volume, muted = self._get_volume_info(force_refresh=True)
        return {"volume": volume, "muted": muted}


class MicWidget(AudioWidget):
    def __init__(self, **config):
        super().__init__(kind="input", **config)
