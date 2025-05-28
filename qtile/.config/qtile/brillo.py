import subprocess
import time
from pathlib import Path
from typing import List, Optional, Tuple

from libqtile.widget.base import expose_command
from qtile_extras.widget import GenPollText


def run(cmd: List[str]) -> str:
    """Run a shell command and return output or empty string on failure."""
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL, timeout=1
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError, TimeoutError):
        return ""


def format_output(icon: str, value: int, color: str) -> str:
    """Format widget output with icon, value, and color."""
    return f'<span foreground="{color}">{icon}  {value:3d}%</span>'


class BrilloWidget(GenPollText):
    """Brightness control widget with multiple backend support."""
    
    def __init__(
        self,
        update_interval: float = 1.0,
        step: int = 5,
        device_name: Optional[str] = None,
        icons: List[Tuple[int, str, str]] = None,
        prefer_brillo: bool = True,
        **config,
    ):
        self.step = step
        self.device_name = device_name
        self.prefer_brillo = prefer_brillo
        
        # Default icons configuration
        self.icons = icons or [
            (80, "󰃠", "gold"),
            (60, "󰃝", "darkorange"),
            (40, "󰃟", "tan"),
            (20, "󰃞", "lime"),
            (0, "󰃜", "dimgrey"),
        ]
        
        # Initialize backends
        self.has_brillo = bool(run(["which", "brillo"]))
        self.device = self._find_backlight_device()
        self.max_brightness = self._get_max_brightness()
        
        # Caching for performance
        self._last_percent = None
        self._last_check = 0.0
        self._cache_duration = 0.3
        
        # Determine best backend
        self.backend = self._select_backend()
        
        super().__init__(func=self.poll, update_interval=update_interval, **config)
    
    def _find_backlight_device(self) -> Optional[Path]:
        """Find the best backlight device."""
        backlight_dir = Path("/sys/class/backlight")
        
        if not backlight_dir.exists():
            return None
            
        try:
            devices = list(backlight_dir.iterdir())
            if not devices:
                return None
                
            # If specific device requested, try to find it
            if self.device_name:
                for device in devices:
                    if self.device_name in device.name:
                        return device
                        
            # Prefer intel_backlight, acpi_video0, or first available
            preferred_order = ["intel_backlight", "acpi_video0", "amdgpu_bl0"]
            for preferred in preferred_order:
                for device in devices:
                    if preferred in device.name:
                        return device
                        
            # Return first available device
            return devices[0]
            
        except (OSError, PermissionError):
            return None
    
    def _get_max_brightness(self) -> int:
        """Get maximum brightness value."""
        if not self.device:
            return 0
            
        try:
            max_file = self.device / "max_brightness"
            if max_file.exists():
                return int(max_file.read_text().strip())
        except (FileNotFoundError, ValueError, OSError, PermissionError):
            pass
        return 0
    
    def _read_current_brightness(self) -> Optional[int]:
        """Read current brightness from sysfs."""
        if not self.device:
            return None
            
        try:
            brightness_file = self.device / "brightness"
            if brightness_file.exists():
                return int(brightness_file.read_text().strip())
        except (FileNotFoundError, ValueError, OSError, PermissionError):
            pass
        return None
    
    def _write_brightness(self, value: int) -> bool:
        """Write brightness value to sysfs."""
        if not self.device:
            return False
            
        try:
            brightness_file = self.device / "brightness"
            brightness_file.write_text(str(max(0, min(value, self.max_brightness))))
            return True
        except (OSError, PermissionError):
            return False
    
    def _select_backend(self) -> str:
        """Select the best available backend."""
        if self.prefer_brillo and self.has_brillo:
            return "brillo"
        elif self.device and self.max_brightness > 0:
            return "sysfs"
        elif self.has_brillo:
            return "brillo"
        else:
            return "none"
    
    def _get_current_percent(self, use_cache: bool = True) -> Optional[int]:
        """Get current brightness percentage with optional caching."""
        now = time.time()
        
        # Use cache if available and recent
        if use_cache and self._last_percent is not None and (now - self._last_check) < self._cache_duration:
            return self._last_percent
        
        percent = None
        
        if self.backend == "brillo":
            output = run(["brillo", "-G"])
            if output:
                try:
                    percent = int(float(output))
                except ValueError:
                    pass
        elif self.backend == "sysfs":
            current = self._read_current_brightness()
            if current is not None and self.max_brightness > 0:
                percent = int((current / self.max_brightness) * 100)
        
        # Update cache
        if percent is not None:
            self._last_percent = percent
            self._last_check = now
            
        return percent
    
    def poll(self) -> str:
        """Poll current brightness status."""
        percent = self._get_current_percent()
        
        if percent is None:
            return '<span foreground="grey">󰳲  N/A</span>'
        
        # Find appropriate icon
        for level, icon, color in self.icons:
            if percent >= level:
                return format_output(icon, percent, color)
        
        # Fallback to lowest icon
        return format_output(self.icons[-1][1], percent, self.icons[-1][2])
    
    def _change_brightness_percent(self, delta: int) -> bool:
        """Change brightness by delta percentage."""
        current = self._get_current_percent(use_cache=False)
        if current is None:
            return False
            
        new_percent = max(0, min(100, current + delta))
        
        if self.backend == "brillo":
            if delta > 0:
                return bool(run(["brillo", "-A", str(abs(delta))]))
            else:
                return bool(run(["brillo", "-U", str(abs(delta))]))
        elif self.backend == "sysfs":
            new_value = int((new_percent / 100) * self.max_brightness)
            success = self._write_brightness(new_value)
            if success:
                # Invalidate cache
                self._last_percent = None
            return success
        
        return False
    
    @expose_command()
    def increase(self):
        """Increase brightness by step amount."""
        if self.backend != "none":
            self._change_brightness_percent(self.step)
    
    @expose_command()
    def decrease(self):
        """Decrease brightness by step amount."""
        if self.backend != "none":
            self._change_brightness_percent(-self.step)
    
    @expose_command()
    def set_percent(self, percent: int):
        """Set brightness to specific percentage."""
        percent = max(0, min(100, percent))
        
        if self.backend == "brillo":
            run(["brillo", "-S", str(percent)])
        elif self.backend == "sysfs":
            value = int((percent / 100) * self.max_brightness)
            success = self._write_brightness(value)
            if success:
                self._last_percent = None
    
    @expose_command()
    def get_info(self) -> str:
        """Get widget information for debugging."""
        return f"Backend: {self.backend}, Device: {self.device.name if self.device else 'None'}, Brillo: {self.has_brillo}"
