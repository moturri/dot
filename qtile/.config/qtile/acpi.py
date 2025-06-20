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
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Optional, Tuple

from qtile_extras.widget import GenPollText

logger = logging.getLogger(__name__)

CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"
EMPTY_ICON = "󰁺"
FALLBACK_ICON = "󰂑"

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


class AcpiWidget(GenPollText):  # type: ignore
    """Minimal ACPI battery widget using acpi or sysfs fallback."""

    _ENV = {"LC_ALL": "C.UTF-8", **os.environ}

    def __init__(
        self,
        update_interval: float = 15.0,
        show_time: bool = False,
        critical_threshold: int = 10,
        power_supply_path: str = "/sys/class/power_supply",
        **config: Any,
    ) -> None:
        self.show_time = show_time
        self.critical_threshold = max(5, min(25, critical_threshold))
        self.sys_path = Path(power_supply_path)
        self._has_acpi_cmd: Optional[bool] = None
        self._battery_path: Optional[Path] = None
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _poll(self) -> str:
        data = self._get_acpi_data()
        if not data:
            return f"{FALLBACK_ICON} N/A"
        pct, state, minutes = data
        icon, color = self._icon_color(pct, state)
        time_str = self._format_time(minutes) if self.show_time and minutes else ""
        return f'<span foreground="{color}">{icon} {pct}%{time_str}</span>'

    def _has_acpi_command(self) -> bool:
        if self._has_acpi_cmd is None:
            try:
                subprocess.run(
                    ["acpi", "--version"],
                    env=self._ENV,
                    timeout=1.0,
                    capture_output=True,
                    check=True,
                )
                self._has_acpi_cmd = True
            except Exception:
                logger.debug("acpi command not available")
                self._has_acpi_cmd = False
        return self._has_acpi_cmd

    def _get_acpi_data(self) -> Optional[Tuple[int, str, Optional[int]]]:
        if self._has_acpi_command():
            try:
                output = subprocess.check_output(
                    ["acpi", "-b"], env=self._ENV, timeout=1.5
                ).decode()
                parts = output.split(":")[1].split(",")
                state = parts[0].strip().lower()
                pct = int(parts[1].strip().rstrip("%"))
                minutes = None
                if len(parts) > 2 and ":" in parts[2]:
                    h, m = map(int, parts[2].strip().split(":")[:2])
                    minutes = h * 60 + m
                return pct, state, minutes
            except Exception as e:
                logger.warning("acpi parsing failed: %s", e)
        return self._read_sysfs()

    def _read_sysfs(self) -> Optional[Tuple[int, str, Optional[int]]]:
        if not self._battery_path:
            for entry in self.sys_path.iterdir():
                if entry.name.startswith("BAT") and (entry / "status").exists():
                    self._battery_path = entry
                    break
        if not self._battery_path:
            logger.warning("No battery device found in sysfs.")
            return None
        bat = self._battery_path
        try:
            state = (bat / "status").read_text().strip().lower()
            pct = int((bat / "capacity").read_text().strip())
            time_file = bat / (
                "time_to_full_now" if state == "charging" else "time_to_empty_now"
            )
            minutes = None
            if time_file.exists():
                try:
                    seconds = int(time_file.read_text().strip())
                    minutes = seconds // 60
                except ValueError:
                    logger.debug("Could not parse battery time")
            return pct, state, minutes
        except Exception as e:
            logger.warning("Error reading sysfs battery info: %s", e)
            return None

    def _icon_color(self, pct: int, state: str) -> Tuple[str, str]:
        if state == "full":
            return FULL_ICON, "lime"
        if pct <= self.critical_threshold:
            return EMPTY_ICON, "red" if pct <= 5 else "orange"
        for threshold, icon, color in BATTERY_ICONS:
            if pct >= threshold:
                return (
                    (f"{CHARGING_ICON} {icon}", color)
                    if state == "charging"
                    else (icon, color)
                )
        return FALLBACK_ICON, "darkgrey"

    def _format_time(self, minutes: int) -> str:
        h, m = divmod(minutes, 60)
        return f" ({h}h {m:02d}m)" if h else f" ({m}m)"
