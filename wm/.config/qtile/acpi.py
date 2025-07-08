# MIT License
#
# Copyright (c) 2025 Elton Moturi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import subprocess
from typing import Any, List, Optional, Tuple

from libqtile.command.base import expose_command
from qtile_extras.widget import GenPollText

CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"

EMPTY_ICON = "󰁺"

BATTERY_ICONS = (
    (95, "󰂂", "limegreen"),
    (80, "󰂁", "palegreen"),
    (60, "󰂀", "khaki"),
    (40, "󰁿", "tan"),
    (20, "󰁻", "lightsalmon"),
    (10, "󰁻", "orange"),
    (5, "󰁻", "red"),
    (0, EMPTY_ICON, "darkred"),
)


def run(cmd: List[str], timeout: float = 0.5) -> Optional[str]:
    try:
        return subprocess.check_output(
            cmd, text=True, timeout=timeout, env={"LC_ALL": "C.UTF-8", **os.environ}
        ).strip()
    except Exception:
        return None


class AcpiWidget(GenPollText):  # type: ignore[misc]
    """Suckless Qtile battery widget with /sys and acpi fallback."""

    def __init__(
        self,
        update_interval: float = 15.0,
        show_time: bool = False,
        critical_threshold: int = 20,
        battery_path: str = "/sys/class/power_supply/BAT0",
        **config: Any,
    ):
        self.path = battery_path
        self.show_time = show_time
        self.critical = max(5, min(25, critical_threshold))
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _poll(self) -> str:
        data = self._from_sys() or self._from_acpi()
        if not data:
            return f'<span foreground="grey">{EMPTY_ICON} N/A</span>'

        pct, state, mins = data
        icon, color = self._icon(pct, state)
        time = self._format_time(mins) if self.show_time and mins else ""
        return f'<span foreground="{color}">{icon} {pct}%{time}</span>'

    def _from_sys(self) -> Optional[Tuple[int, str, Optional[int]]]:
        try:
            pct = self._read_int("capacity")
            state = self._read("status").lower()
            mins = self._estimate_time(state)
            return pct, state, mins
        except Exception:
            return None

    def _read(self, name: str) -> str:
        with open(f"{self.path}/{name}", "r", encoding="utf-8") as f:
            return f.read().strip()

    def _read_int(self, name: str) -> int:
        return int(self._read(name))

    def _estimate_time(self, state: str) -> Optional[int]:
        if state != "discharging":
            return None
        for prefix in ["charge", "energy"]:
            try:
                now = self._read_int(f"{prefix}_now")
                rate = self._read_int(
                    "current_now" if prefix == "charge" else "power_now"
                )
                return int((now / rate) * 60) if rate > 0 else None
            except Exception:
                continue
        return None

    def _from_acpi(self) -> Optional[Tuple[int, str, Optional[int]]]:
        out = run(["acpi", "-b"])
        if not out:
            return None
        try:
            parts = out.split(":", 1)[1].strip().split(", ")
            state = parts[0].lower()
            pct = int(parts[1].rstrip("%"))
            mins = None
            if len(parts) > 2 and ":" in parts[2]:
                h, m = map(int, parts[2].split(":")[:2])
                mins = h * 60 + m
            return pct, state, mins
        except Exception:
            return None

    def _icon(self, pct: int, state: str) -> Tuple[str, str]:
        if state == "charging":
            for threshold, icon, color in BATTERY_ICONS:
                if pct >= threshold:
                    return f"{CHARGING_ICON} {icon}", color
            return f"{CHARGING_ICON} {EMPTY_ICON}", "darkgreen"
        if state == "full":
            return FULL_ICON, "lime"
        if pct <= self.critical:
            return EMPTY_ICON, "red" if pct <= 5 else "orange"
        for threshold, icon, color in BATTERY_ICONS:
            if pct >= threshold:
                return icon, color
        return EMPTY_ICON, "grey"

    def _format_time(self, mins: int) -> str:
        h, m = divmod(mins, 60)
        return f" ({h}h {m:02d}m)" if h else f" ({m}m)"

    @expose_command()
    def refresh(self) -> None:
        self.force_update()
