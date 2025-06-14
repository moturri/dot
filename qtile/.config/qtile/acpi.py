# Copyright (C) 2025, Elton Moturi
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
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
from typing import Any, Dict, List, Optional, Tuple

from libqtile.widget.base import expose_command  # type: ignore[attr-defined]
from qtile_extras.widget import GenPollText

# Logger
logger = logging.getLogger("qtile.acpi_battery")
logger.setLevel(logging.WARNING)

# Icons and colors
CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"
EMPTY_ICON = "󰁺"
FALLBACK_ICON = "󰂑"
FALLBACK_COLOR = "#666666"

BATTERY_ICONS: Tuple[Tuple[int, str, str], ...] = (
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
    """Optimized ACPI battery widget with caching and fallback."""

    _ENV = {"LC_ALL": "C.UTF-8", **os.environ}
    __slots__ = (
        "show_time",
        "critical_threshold",
        "sys_path",
        "_last_output",
        "_last_parsed",
        "_last_text",
        "_has_acpi_cmd",
        "_preferred_battery_path",
    )

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
        self._last_output: Optional[str] = None
        self._last_parsed: Optional[Tuple[int, str, Optional[int]]] = None
        self._last_text = ""
        self._has_acpi_cmd: Optional[bool] = None
        self._preferred_battery_path: Optional[Path] = None
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _poll(self) -> str:
        output = self._get_battery_output()
        if not output:
            return self._set_last_text(f"{FALLBACK_ICON} N/A", FALLBACK_COLOR)

        parsed = self._parse_acpi(output)
        if not parsed:
            return self._set_last_text(f"{FALLBACK_ICON} ERR", FALLBACK_COLOR)

        pct, state, minutes = parsed
        icon, color = self._get_icon_color(pct, state)
        time_str = self._format_time(minutes) if self.show_time else ""
        return self._set_last_text(f"{icon} {pct:3d}%{time_str}", color)

    def _set_last_text(self, text: str, color: str) -> str:
        self._last_text = f'<span foreground="{color}">{text}</span>'
        return self._last_text

    def _has_acpi_command(self) -> bool:
        if self._has_acpi_cmd is None:
            try:
                subprocess.run(
                    ["acpi", "--version"],
                    env=self._ENV,
                    timeout=1,
                    check=True,
                    capture_output=True,
                )
                self._has_acpi_cmd = True
            except (OSError, subprocess.SubprocessError):
                self._has_acpi_cmd = False
        return self._has_acpi_cmd

    def _get_battery_path(self) -> Optional[Path]:
        if self._preferred_battery_path is not None:
            return self._preferred_battery_path
        try:
            for entry in self.sys_path.iterdir():
                if entry.name.startswith("BAT") and (entry / "status").exists():
                    self._preferred_battery_path = entry
                    break
        except OSError:
            pass
        return self._preferred_battery_path

    def _get_battery_output(self) -> Optional[str]:
        return self._run_acpi() if self._has_acpi_command() else self._read_sysfs()

    def _run_acpi(self) -> Optional[str]:
        try:
            out = subprocess.run(
                ["acpi", "-b"],
                capture_output=True,
                timeout=1.5,
                text=True,
                env=self._ENV,
                check=True,
            )
            return out.stdout.strip() or None
        except (subprocess.SubprocessError, OSError):
            self._has_acpi_cmd = False
            return None

    def _read_sysfs(self) -> Optional[str]:
        bat = self._get_battery_path()
        if not bat:
            return None
        try:
            status = (bat / "status").read_text().strip().lower()
            capacity = int((bat / "capacity").read_text().strip())
            seconds = None
            time_file = (
                bat / "time_to_full_now"
                if status == "charging"
                else bat / "time_to_empty_now"
            )
            if time_file.exists():
                try:
                    seconds = int(time_file.read_text().strip())
                except (ValueError, OSError):
                    pass
            minutes = seconds // 60 if seconds else 0
            hours, mins = divmod(minutes, 60)
            time_str = f", {hours}:{mins:02d} {'until charged' if status == 'charging' else 'remaining'}"
            return f"Battery: {status.capitalize()}, {capacity}%{time_str}"
        except (OSError, ValueError) as e:
            logger.error("Sysfs read failed: %s", e)
            return None

    def _parse_acpi(self, output: str) -> Optional[Tuple[int, str, Optional[int]]]:
        if output == self._last_output and self._last_parsed:
            return self._last_parsed
        try:
            parts = output.split(":")[1].split(",")
            state = parts[0].strip().lower()
            percentage = int(parts[1].strip().rstrip("%"))
            minutes = None
            if len(parts) > 2 and ":" in parts[2]:
                h, m = map(int, parts[2].strip().split(":")[:2])
                minutes = h * 60 + m
            self._last_output = output
            self._last_parsed = (percentage, state, minutes)
            return self._last_parsed
        except (ValueError, IndexError) as e:
            logger.warning("Parse error: %s", e)
            return None

    def _get_icon_color(self, pct: int, state: str) -> Tuple[str, str]:
        if state == "full":
            return FULL_ICON, "lime"
        if pct <= self.critical_threshold:
            return EMPTY_ICON, "red" if pct <= 5 else "orange"
        for threshold, icon, color in BATTERY_ICONS:
            if pct >= threshold:
                return (
                    f"{CHARGING_ICON} {icon}" if state == "charging" else icon,
                    color,
                )
        return FALLBACK_ICON, FALLBACK_COLOR

    def _format_time(self, minutes: Optional[int]) -> str:
        if minutes is None or minutes < 0:
            return ""
        h, m = divmod(minutes, 60)
        return f" ({h}h {m:02d}m)" if h else f" ({m}m)"

    @expose_command()
    def toggle_time_display(self) -> None:
        self.show_time = not self.show_time
        self.force_update()

    @expose_command()
    def get_info(self) -> str:
        return self._get_battery_output() or "Battery: N/A"

    @expose_command()
    def get_percentage(self) -> int:
        parsed = self._parse_acpi(self._get_battery_output() or "")
        return parsed[0] if parsed else -1

    @expose_command()
    def get_state(self) -> str:
        parsed = self._parse_acpi(self._get_battery_output() or "")
        return parsed[1] if parsed else "unknown"

    @expose_command()
    def get_time_remaining(self) -> int:
        parsed = self._parse_acpi(self._get_battery_output() or "")
        return parsed[2] if parsed and parsed[2] is not None else -1

    @expose_command()
    def is_critical(self) -> bool:
        parsed = self._parse_acpi(self._get_battery_output() or "")
        return bool(parsed and parsed[0] <= self.critical_threshold)

    @expose_command()
    def refresh(self) -> None:
        self.force_update()

    @expose_command()
    def reset_cache(self) -> None:
        self._last_output = None
        self._last_parsed = None
        self._last_text = ""
        self._has_acpi_cmd = None
        self._preferred_battery_path = None
        self.force_update()


class BatteryManager:
    """Lean system battery manager."""

    _ENV = {"LC_ALL": "C.UTF-8", **os.environ}

    @staticmethod
    def get_all_batteries() -> List[str]:
        try:
            return [
                f.name
                for f in Path("/sys/class/power_supply").iterdir()
                if f.name.startswith("BAT") and f.is_dir()
            ]
        except OSError:
            return []

    @staticmethod
    def is_ac_connected() -> bool:
        try:
            for ac in Path("/sys/class/power_supply").iterdir():
                if ac.name.startswith(("AC", "ADP")):
                    return (ac / "online").read_text().strip() == "1"
        except OSError:
            pass
        return False

    @staticmethod
    def get_battery_health(battery: str = "BAT0") -> Optional[Dict[str, Any]]:
        bat_path = Path(f"/sys/class/power_supply/{battery}")
        if not bat_path.exists():
            return None
        keys = {
            "cycle_count",
            "charge_full",
            "charge_full_design",
            "voltage_now",
            "current_now",
            "power_now",
            "technology",
            "manufacturer",
            "model_name",
        }
        info: Dict[str, Any] = {}
        for key in keys:
            fp = bat_path / key
            if fp.exists():
                try:
                    val = fp.read_text().strip()
                    info[key] = int(val) if val.isdigit() else val
                except (OSError, ValueError):
                    continue
        if "charge_full" in info and "charge_full_design" in info:
            try:
                info["health_percentage"] = round(
                    (info["charge_full"] / info["charge_full_design"]) * 100, 1
                )
            except Exception:
                pass
        return info
