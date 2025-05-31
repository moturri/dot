import logging
import shutil
import subprocess
import time
from typing import Any, Dict, Final, List, NamedTuple, Optional, Tuple, TypedDict

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText

# Fail-fast check for wpctl binary
if not shutil.which("wpctl"):
    raise RuntimeError("wpctl not found in PATH")

# Logger setup (disabled unless set to DEBUG/INFO externally)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)  # Adjust externally as needed

# Constants
DEFAULT_VOLUME_STEP: Final[int] = 5
CACHE_TIMEOUT: Final[float] = 0.5
CMD_TIMEOUT: Final[float] = 1.0


class VolumeSettings(TypedDict):
    """Configuration schema for audio devices."""

    device: str
    thresholds: List[int]
    colors: List[str]
    icons: List[str]
    muted_icon: str


VOLUME_CONFIG: Dict[str, VolumeSettings] = {
    "output": {
        "device": "@DEFAULT_AUDIO_SINK@",
        "thresholds": [70, 40, 0],
        "colors": ["#ff5555", "#bd93f9", "#50fa7b"],
        "icons": ["󰕾", "󰖀", "󰕿"],
        "muted_icon": "󰝟",
    },
    "input": {
        "device": "@DEFAULT_AUDIO_SOURCE@",
        "thresholds": [70, 40, 0],
        "colors": ["#ff5555", "#bd93f9", "#50fa7b"],
        "icons": ["󰍬", "󰍬", "󰍬"],
        "muted_icon": "󰍭",
    },
}


class VolumeCache(NamedTuple):
    """Internal cache for volume status."""

    volume: int
    muted: bool
    timestamp: float


def run_cmd(cmd: List[str]) -> str:
    """Run a shell command safely and return output or empty string if it fails."""
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.PIPE, timeout=CMD_TIMEOUT
        ).strip()
    except subprocess.CalledProcessError as e:
        logger.warning(f"[audio.py] Command failed: {cmd} - {e}")
    except subprocess.TimeoutExpired:
        logger.warning(f"[audio.py] Command timed out: {cmd}")
    except Exception as e:
        logger.error(f"[audio.py] Unexpected error: {cmd} - {e}")
    return ""


def parse_wpctl_output(output: str) -> Tuple[int, bool]:
    """Parse wpctl command output to extract volume and mute status."""
    try:
        parts = output.split()
        volume = round(float(parts[1]) * 100)
        muted = "[MUTED]" in output
        return volume, muted
    except (IndexError, ValueError):
        logger.error(f"Failed to parse wpctl output: {output}")
        return 0, True


def format_span(icon: str, color: str, volume: int) -> str:
    """Format a Pango markup span for display."""
    return f'<span foreground="{color}">{icon} {volume:3d}%</span>'


class AudioWidget(GenPollText):  # type: ignore[misc]
    """Base audio widget for system output/input using wpctl."""

    def __init__(
        self,
        kind: str = "output",
        device: Optional[str] = None,
        update_interval: float = 0.5,
        volume_step: int = DEFAULT_VOLUME_STEP,
        **config: Any,
    ) -> None:
        self.kind = kind
        self.config = VOLUME_CONFIG[kind]
        self.device = device or self.config["device"]
        self.volume_step = volume_step
        self._cache: Optional[VolumeCache] = None

        thresholds = self.config["thresholds"]
        icons = self.config["icons"]
        colors = self.config["colors"]
        self._icon_map = sorted(
            zip(thresholds, icons, colors), key=lambda x: x[0], reverse=True
        )

        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _get_volume_info(self, force_refresh: bool = False) -> Tuple[int, bool]:
        now = time.time()
        if not force_refresh and self._cache:
            if now - self._cache.timestamp < CACHE_TIMEOUT:
                return self._cache.volume, self._cache.muted

        output = run_cmd(["wpctl", "get-volume", self.device])
        if output:
            volume, muted = parse_wpctl_output(output)
            self._cache = VolumeCache(volume, muted, now)
            return volume, muted

        return self._cache[:2] if self._cache else (0, True)

    def _format_display(self, volume: int, muted: bool) -> str:
        if muted:
            return format_span(self.config["muted_icon"], "#666666", volume)
        for threshold, icon, color in self._icon_map:
            if volume >= threshold:
                return format_span(icon, color, volume)
        return format_span(self._icon_map[-1][1], self._icon_map[-1][2], volume)

    def _poll(self) -> str:
        volume, muted = self._get_volume_info()
        return self._format_display(volume, muted)

    def _execute_volume_cmd(self, cmd: List[str]) -> None:
        run_cmd(cmd)
        self._cache = None

    @expose_command()
    def volume_up(self) -> None:
        """Increase volume by configured step."""
        volume, _ = self._get_volume_info(force_refresh=True)
        new_volume = f"{min(100, volume + self.volume_step)}%"
        self._execute_volume_cmd(["wpctl", "set-volume", self.device, new_volume])

    @expose_command()
    def volume_down(self) -> None:
        """Decrease volume by configured step."""
        volume, _ = self._get_volume_info(force_refresh=True)
        new_volume = f"{max(0, volume - self.volume_step)}%"
        self._execute_volume_cmd(["wpctl", "set-volume", self.device, new_volume])

    @expose_command()
    def toggle_mute(self) -> None:
        """Toggle mute state."""
        self._execute_volume_cmd(["wpctl", "set-mute", self.device, "toggle"])

    @expose_command()
    def get_state(self) -> Dict[str, Any]:
        """Get current volume and mute state."""
        volume, muted = self._get_volume_info(force_refresh=True)
        return {"volume": volume, "muted": muted}

    @expose_command()
    def refresh(self) -> None:
        """Manually refresh widget display."""
        self._cache = None
        self.poll()


class MicWidget(AudioWidget):
    """Microphone widget inheriting from AudioWidget."""

    def __init__(self, **config: Any) -> None:
        super().__init__(kind="input", **config)
