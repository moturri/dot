import shutil
import subprocess
from pathlib import Path
from typing import Optional

from libqtile.widget.base import expose_command
from qtile_extras.widget import GenPollText

DEVICE_PRIORITY = ["intel_backlight", "amdgpu_bl0", "acpi_video0"]
BRIGHTNESS_STEP = 5


def run(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(
            cmd, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return ""


def find_device() -> Optional[Path]:
    base = Path("/sys/class/backlight")
    if not base.exists():
        return None
    devices = list(base.iterdir())
    for name in DEVICE_PRIORITY:
        for d in devices:
            if name in d.name:
                return d
    return devices[0] if devices else None


class BrilloWidget(GenPollText):
    def __init__(
        self, update_interval: float = 0.5, step: int = BRIGHTNESS_STEP, **config
    ):
        super().__init__(**config)
        self.step = step
        self.device = find_device()
        self.has_brillo = bool(shutil.which("brillo"))
        self.backend = "brillo" if self.has_brillo else "sysfs"
        self.max = (
            int((self.device / "max_brightness").read_text()) if self.device else 1
        )
        self.func = self.poll
        self.update_interval = update_interval

    def poll(self) -> str:
        percent = self.get_percent()
        icon = (
            "󰃠"
            if percent > 80
            else "󰃝"
            if percent > 60
            else "󰃟"
            if percent > 40
            else "󰃞"
            if percent > 20
            else "󰃜"
        )
        color = (
            "gold"
            if percent > 80
            else "orange"
            if percent > 60
            else "tan"
            if percent > 40
            else "lime"
            if percent > 20
            else "grey"
        )
        return f'<span foreground="{color}">{icon}  {percent}%</span>'

    def get_percent(self) -> int:
        if self.backend == "brillo":
            val = run(["brillo", "-G"])
            try:
                return int(float(val))
            except ValueError:
                return 0
        if self.device:
            current = int((self.device / "brightness").read_text())
            return current * 100 // self.max
        return 0

    def set_percent(self, val: int) -> None:
        val = max(0, min(100, val))
        if self.backend == "brillo":
            run(["brillo", "-S", str(val)])
        elif self.device:
            raw = val * self.max // 100
            (self.device / "brightness").write_text(str(raw))

    @expose_command()
    def increase(self) -> None:
        self.set_percent(self.get_percent() + self.step)

    @expose_command()
    def decrease(self) -> None:
        self.set_percent(self.get_percent() - self.step)
