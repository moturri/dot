import logging
import subprocess
import time
from typing import Any, Dict, Final, List, Optional, Tuple, TypedDict

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText

logger = logging.getLogger(__name__)

# Constants
VOLUME_STEP: Final[int] = 5
CACHE_TIMEOUT: Final[float] = 0.5
DEBOUNCE_TIMEOUT: Final[float] = 0.1
CMD_TIMEOUT: Final[float] = 1.0


class VolumeSettings(TypedDict):
    device: str
    thresholds: List[int]
    colors: List[str]
    icons: List[str]
    muted_icon: str


VOLUME_CONFIG: Dict[str, VolumeSettings] = {
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
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=CMD_TIMEOUT
        ).strip()
    except (
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
        FileNotFoundError,
    ) as e:
        logger.debug(f"Command {cmd} failed: {e}")
        return ""


def parse_wpctl_output(output: str) -> Tuple[int, bool]:
    try:
        parts = output.split()
        volume = round(float(parts[1]) * 100)
        muted = "[MUTED]" in output
        return volume, muted
    except (IndexError, ValueError):
        return 0, True


class AudioWidget(GenPollText):  # type: ignore[misc]
    def __init__(
        self,
        kind: str = "output",
        device: Optional[str] = None,
        update_interval: float = 0.5,
        **config: Any,
    ) -> None:
        self.kind = kind
        self.config = VOLUME_CONFIG[kind]
        self.device = device or self.config["device"]

        thresholds = self.config["thresholds"]
        icons = self.config["icons"]
        colors = self.config["colors"]

        self._icon_map = sorted(
            zip(thresholds, icons, colors), key=lambda x: x[0], reverse=True
        )
        self._cache: Optional[Tuple[int, bool, float]] = None
        self._last_poll_time = 0.0

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_volume_info(self, force_refresh: bool = False) -> Tuple[int, bool]:
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

        return 0, True

    def _format_display(self, volume: int, muted: bool) -> str:
        if volume == 0 and muted:
            return f'<span foreground="grey">{self.config["muted_icon"]}  N/A</span>'
        if muted:
            return f'<span foreground="dimgrey">{self.config["muted_icon"]} {volume:3d}%</span>'

        for threshold, icon, color in self._icon_map:
            if volume >= threshold:
                return f'<span foreground="{color}">{icon} {volume:3d}%</span>'

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

    def _execute_volume_cmd(self, cmd: List[str]) -> None:
        run_cmd(cmd)
        self._cache = None

    @expose_command()
    def volume_up(self) -> None:
        """Increase volume by VOLUME_STEP."""
        volume, _ = self._get_volume_info(force_refresh=True)
        new_volume = min(100, volume + VOLUME_STEP) / 100
        self._execute_volume_cmd(
            ["wpctl", "set-volume", self.device, f"{new_volume:.2f}"]
        )

    @expose_command()
    def volume_down(self) -> None:
        """Decrease volume by VOLUME_STEP."""
        volume, _ = self._get_volume_info(force_refresh=True)
        new_volume = max(0, volume - VOLUME_STEP) / 100
        self._execute_volume_cmd(
            ["wpctl", "set-volume", self.device, f"{new_volume:.2f}"]
        )

    @expose_command()
    def toggle_mute(self) -> None:
        """Toggle mute state."""
        self._execute_volume_cmd(["wpctl", "set-mute", self.device, "toggle"])

    @expose_command()
    def get_state(self) -> Dict[str, Any]:
        """Return current volume and mute state."""
        volume, muted = self._get_volume_info(force_refresh=True)
        return {"volume": volume, "muted": muted}


class MicWidget(AudioWidget):
    def __init__(self, **config: Any) -> None:
        super().__init__(kind="input", **config)

