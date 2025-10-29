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


import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pyudev  # type: ignore[import-untyped]
from libqtile.command.base import expose_command
from libqtile.log_utils import logger
from qtile_extras.widget import GenPollText

BATTERY_ICONS: Tuple[Tuple[int, str, str], ...] = (
    (90, "󰁹", "limegreen"),
    (80, "󰁹", "palegreen"),
    (60, "󰂀", "yellow"),
    (40, "󰁿", "gold"),
    (20, "󰁾", "orange"),
    (0, "󰁻", "indianred"),
)

CHARGING_ICON = "󱐋"


class BatteryWidget(GenPollText):  # type: ignore[misc]

    def __init__(
        self,
        critical: int = 15,
        debounce_s: float = 0.25,
        battery_path: Optional[str] = None,
        colors: Optional[Dict[str, str]] = None,
        enable_alert: bool = True,
        log_path: str = "/tmp/batterywidget.log",
        **config: Any,
    ):
        self.critical = max(1, min(critical, 100))
        self.debounce_ns = int(debounce_s * 1e9)
        self.enable_alert = enable_alert
        self.colors = colors or {}
        self.log_path = Path(log_path)
        self._stop_event = threading.Event()
        self._last_update = 0
        self._last_alert_time = 0.0

        self.battery_paths = self._detect_batteries(battery_path)
        if not self.battery_paths:
            text = '<span foreground="grey">󰁺 No Battery</span>'
        else:
            text = self._poll()

        super().__init__(func=self._poll, update_interval=9999.0, **config)
        self.text = text
        self._thread = threading.Thread(target=self._monitor_battery, daemon=True)
        self._thread.start()
        logger.info("BatteryWidget started with %d batteries", len(self.battery_paths))

    @staticmethod
    def _detect_batteries(manual: Optional[str]) -> List[Path]:
        if manual:
            path = Path(manual)
            return [path] if path.exists() else []
        return [p for p in Path("/sys/class/power_supply").glob("BAT*") if p.is_dir()]

    def _monitor_battery(self) -> None:
        """Listen for udev battery events and trigger redraws."""
        try:
            context = pyudev.Context()
            monitor = pyudev.Monitor.from_netlink(context)
            monitor.filter_by(subsystem="power_supply")
        except Exception as e:
            logger.error("Failed to start udev monitor: %s", e)
            return

        for device in iter(lambda: monitor.poll(timeout=1000), None):
            if self._stop_event.is_set():
                break
            if not device or "BAT" not in device.sys_name:
                continue
            now = time.monotonic_ns()
            if now - self._last_update < self.debounce_ns:
                continue
            self._last_update = now
            try:
                self.qtile.call_soon_threadsafe(self.force_update)
            except Exception:
                logger.exception("Failed to trigger redraw")

    def finalize(self) -> None:
        """Graceful shutdown."""
        self._stop_event.set()
        if self._thread.is_alive():
            self._thread.join(timeout=2.0)
        super().finalize()
        logger.info("BatteryWidget stopped cleanly")

    def _read_int(self, path: Path, name: str) -> Optional[int]:
        try:
            return int((path / name).read_text().strip())
        except (FileNotFoundError, ValueError):
            return None

    def _get_battery_percentage(self) -> Optional[int]:
        values = [self._read_int(p, "capacity") for p in self.battery_paths]
        valid = [v for v in values if v is not None]
        return sum(valid) // len(valid) if valid else None

    def _get_battery_state(self) -> str:
        for p in self.battery_paths:
            try:
                state = (p / "status").read_text().strip().lower()
                if state in ("charging", "discharging"):
                    return state
            except FileNotFoundError:
                continue
        return "unknown"

    def _icon_for(self, pct: int, state: str) -> Tuple[str, str]:
        for threshold, icon, color in BATTERY_ICONS:
            if pct >= threshold:
                if state == "charging":
                    icon = f"{CHARGING_ICON} {icon}"
                return icon, self.colors.get(color, color)
        return "󰁻", self.colors.get("grey", "grey")

    def _maybe_alert(self, pct: int) -> None:
        if not self.enable_alert or pct > self.critical:
            return
        if time.monotonic() - self._last_alert_time < 300:
            return
        self._last_alert_time = time.monotonic()
        subprocess.Popen(
            ["notify-send", "Low Battery", f"{pct}% remaining"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def _poll(self) -> str:
        pct = self._get_battery_percentage()
        if pct is None:
            return '<span foreground="grey">󰁺 N/A</span>'
        state = self._get_battery_state()
        icon, color = self._icon_for(pct, state)
        self._maybe_alert(pct)
        return f'<span foreground="{color}">{icon} {pct}%</span>'

    @expose_command()
    def refresh(self) -> None:
        self.force_update()
