import subprocess
import time
from typing import List, Optional, Tuple

from libqtile.widget.base import expose_command
from qtile_extras.widget import GenPollText

# Volume change step (in percent)
VOLUME_STEP = 5


def run(cmd: List[str]) -> str:
    """Execute command with error handling and timeout."""
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=1
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
        # wpctl get-volume returns float like 0.30, 0.75, etc.
        volume = int(float(parts[1]) * 100)
        muted = "[MUTED]" in output
        return volume, muted
    except (IndexError, ValueError):
        return 0, True


def format_output(icon: str, volume: int, color: str) -> str:
    """Format widget output with icon, volume, and color."""
    return f'<span foreground="{color}">{icon}  {volume:3d}%</span>'


class AudioDevice(GenPollText):
    """Base class for audio device widgets."""
    
    def __init__(
        self,
        device: str,
        icons: List[Tuple[int, str, str]],
        muted_icon: str,
        update_interval: float = 0.5,
        debounce_time: float = 0.1,
        **config,
    ):
        self.device = device
        self.icons = icons
        self.muted_icon = muted_icon
        self.debounce_time = debounce_time
        
        # Caching for performance
        self._last_output = ""
        self._last_check = 0.0
        self._cached_volume_info: Optional[Tuple[int, bool]] = None
        self._cache_time = 0.0
        
        super().__init__(func=self.poll, update_interval=update_interval, **config)

    def _get_volume_info(self, use_cache: bool = True) -> Tuple[int, bool]:
        """Get volume info with optional caching."""
        now = time.time()
        
        if use_cache and self._cached_volume_info and (now - self._cache_time) < 0.5:
            return self._cached_volume_info
            
        output = run(["wpctl", "get-volume", self.device])
        volume_info = parse_volume(output) if output else (0, True)
        
        # Cache the result
        self._cached_volume_info = volume_info
        self._cache_time = now
        
        return volume_info

    def poll(self) -> str:
        """Poll for current audio status with debouncing."""
        now = time.time()
        
        # Debounce rapid updates
        if now - self._last_check < self.debounce_time:
            return self._last_output
            
        self._last_check = now
        
        # Get volume info
        volume, muted = self._get_volume_info()
        
        # Handle no device case
        if volume == 0 and muted and not run(["wpctl", "get-volume", self.device]):
            result = f'<span foreground="grey">{self.muted_icon}  N/A</span>'
        elif muted:
            result = format_output(self.muted_icon, volume, "dimgrey")
        else:
            # Find appropriate icon based on volume thresholds
            icon, color = self.icons[-1][1], self.icons[-1][2]  # Default to lowest
            for threshold, vol_icon, vol_color in self.icons:
                if volume >= threshold:
                    icon, color = vol_icon, vol_color
                    break
            result = format_output(icon, volume, color)
        
        self._last_output = result
        return result

    def _get_volume(self) -> int:
        """Get current volume level."""
        volume, _ = self._get_volume_info(use_cache=False)
        return volume

    def _set_volume(self, value: float):
        """Set volume level (0.0 to 1.0)."""
        value = max(0.0, min(value, 1.0))
        run(["wpctl", "set-volume", self.device, f"{value:.2f}"])
        # Invalidate cache
        self._cached_volume_info = None

    @expose_command()
    def volume_up(self):
        """Increase volume by VOLUME_STEP."""
        current = self._get_volume()
        self._set_volume((current + VOLUME_STEP) / 100)

    @expose_command()
    def volume_down(self):
        """Decrease volume by VOLUME_STEP."""
        current = self._get_volume()
        self._set_volume((current - VOLUME_STEP) / 100)

    @expose_command()
    def toggle_mute(self):
        """Toggle mute status."""
        run(["wpctl", "set-mute", self.device, "toggle"])
        # Invalidate cache
        self._cached_volume_info = None


class AudioWidget(AudioDevice):
    """Audio output (speakers/headphones) widget."""
    
    def __init__(
        self,
        device: str = "@DEFAULT_AUDIO_SINK@",
        thresholds: List[int] = None,
        colors: List[str] = None,
        icons: List[str] = None,
        muted_icon: str = "󰝟",
        **config,
    ):
        # Default configuration
        default_thresholds = [70, 40, 0]
        default_colors = ["salmon", "mediumpurple", "springgreen"]
        default_icons = ["󰕾", "󰖀", "󰕿"]
        
        # Use provided values or defaults
        thresholds = thresholds or default_thresholds
        colors = colors or default_colors
        icons = icons or default_icons
        
        # Combine into tuples for base class
        icon_config = list(zip(thresholds, icons, colors))
        
        super().__init__(device, icon_config, muted_icon, **config)


class MicWidget(AudioDevice):
    """Audio input (microphone) widget."""
    
    def __init__(
        self,
        device: str = "@DEFAULT_AUDIO_SOURCE@",
        thresholds: List[int] = None,
        colors: List[str] = None,
        icons: List[str] = None,
        muted_icon: str = "󰍭",
        **config,
    ):
        # Default configuration
        default_thresholds = [70, 40, 0]
        default_colors = ["salmon", "mediumpurple", "springgreen"]
        default_icons = ["󰍬", "󰍬", "󰍬"]
        
        # Use provided values or defaults
        thresholds = thresholds or default_thresholds
        colors = colors or default_colors
        icons = icons or default_icons
        
        # Combine into tuples for base class
        icon_config = list(zip(thresholds, icons, colors))
        
        super().__init__(device, icon_config, muted_icon, **config)
