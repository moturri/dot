import logging
import shutil
import subprocess
import time
from typing import Any, Dict, Final, List, NamedTuple, Optional, Tuple, TypedDict

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText

# Check for wpctl only once (fail fast if missing)
if not shutil.which("wpctl"):
    raise RuntimeError("wpctl not found in PATH")

# Setup logger (disabled unless manually enabled)
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)  # Change to DEBUG for verbose logs

# Constants
DEFAULT_VOLUME_STEP: Final[int] = 5
CACHE_TIMEOUT: Final[float] = 0.5
CMD_TIMEOUT: Final[float] = 1.0


# Volume config schema
class VolumeSettings(TypedDict):
    device: str
    thresholds: List[int]
    colors: List[str]
    icons: List[str]
    muted_icon: str


# Color/Icon/Threshold settings (can be made externally configurable later)
VOLUME_CONFIG: Dict[str, VolumeSettings] = {
    "output": {
        "device": "@DEFAULT_AUDIO_SINK@",
        "thresholds": [70, 40, 0],
        "colors": ["#ff5555", "#bd93f9", "#50fa7b"],  # Red, Purple, Green
        "icons": ["󰕾", "󰖀", "󰕿"],  # High, Medium, Low
        "muted_icon": "󰝟",
    },
    "input": {
        "device": "@DEFAULT_AUDIO_SOURCE@",
        "thresholds": [70, 40, 0],
        "colors": ["#ff5555", "#bd93f9", "#50fa7b"],
        "icons": ["󰍬", "󰍬", "󰍬"],  # Same mic icon
        "muted_icon": "󰍭",
    },
}


# Internal volume cache
class VolumeCache(NamedTuple):
    volume: int
    muted: bool
    timestamp: float


# Minimal shell runner
def run_cmd(cmd: List[str]) -> str:
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.PIPE, timeout=CMD_TIMEOUT
        ).strip()
    except Exception as e:
        logger.debug(f"[audio.py] Failed cmd {cmd}: {e}")
        return ""


# Parse output from wpctl
def parse_wpctl_output(output: str) -> Tuple[int, bool]:
    try:
        parts = output.split()
        volume = round(float(parts[1]) * 100)
        muted = "[MUTED]" in output
        return volume, muted
    except (IndexError, ValueError):
        return 0, True


# Colorized span
def format_span(icon: str, color: str, volume: int) -> str:
    return f'<span foreground="{color}">{icon} {volume:3d}%</span>'


# Base audio widget
class AudioWidget(GenPollText):  # type: ignore[misc]
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

        # Precompute icons and colors mapping
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
        volume, _ = self._get_volume_info(force_refresh=True)
        new_volume = f"{min(100, volume + self.volume_step)}%"
        self._execute_volume_cmd(["wpctl", "set-volume", self.device, new_volume])

    @expose_command()
    def volume_down(self) -> None:
        volume, _ = self._get_volume_info(force_refresh=True)
        new_volume = f"{max(0, volume - self.volume_step)}%"
        self._execute_volume_cmd(["wpctl", "set-volume", self.device, new_volume])

    @expose_command()
    def toggle_mute(self) -> None:
        self._execute_volume_cmd(["wpctl", "set-mute", self.device, "toggle"])

    @expose_command()
    def get_state(self) -> Dict[str, Any]:
        volume, muted = self._get_volume_info(force_refresh=True)
        return {"volume": volume, "muted": muted}

    @expose_command()
    def refresh(self) -> None:
        self._cache = None
        self.poll()


# Separate mic widget inheriting from base
class MicWidget(AudioWidget):
    def __init__(self, **config: Any) -> None:
        super().__init__(kind="input", **config)
