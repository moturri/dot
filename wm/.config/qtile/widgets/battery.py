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


from __future__ import annotations

import subprocess
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pyudev  # type: ignore[import-untyped]
from libqtile.log_utils import logger
from qtile_extras import widget

BATTERY_ICONS: Tuple[Tuple[int, str, str], ...] = (
    (90, "󰁹", "limegreen"),
    (80, "󰁹", "palegreen"),
    (60, "󰂀", "cyan"),
    (40, "󰁿", "gold"),
    (20, "󰁾", "tomato"),
    (0, "󰁻", "indianred"),
)

CHARGING_ICON = "󱐋"


class BatteryWidget(widget.TextBox):  # type: ignore[misc]
    """
    A thread-safe Qtile battery widget with udev monitoring and low-battery alerts.
    Compatible with mypy --strict and Arch-based minimalist setups.
    """

    def __init__(
        self,
        critical: int = 15,
        debounce_s: float = 0.25,
        battery_path: Optional[str] = None,
        colors: Optional[Dict[str, str]] = None,
        enable_alert: bool = True,
        log_path: str = "/tmp/batterywidget.log",
        alert_interval_s: int = 300,
        **config: Any,
    ) -> None:
        super().__init__("", **config)
        self.critical: int = max(1, min(critical, 100))
        self.debounce_ns: int = int(debounce_s * 1e9)
        self.alert_interval_s: int = max(alert_interval_s, 60)
        self.enable_alert: bool = enable_alert
        self.colors: Dict[str, str] = colors or {}
        self.log_path: Path = Path(log_path)

        self._stop_event: threading.Event = threading.Event()
        self._last_update: int = 0
        self._last_alert_time: float = 0.0
        self._thread: Optional[threading.Thread] = None

        self.battery_paths: List[Path] = self._detect_batteries(battery_path)
        if not self.battery_paths:
            logger.warning(
                "BatteryWidget: No battery detected in /sys/class/power_supply"
            )

    def _configure(self, qtile: Any, bar: Any) -> None:
        super()._configure(qtile, bar)
        self._thread = threading.Thread(target=self._monitor_battery, daemon=True)
        self._thread.start()
        logger.info(
            "BatteryWidget initialized with %d battery(ies)", len(self.battery_paths)
        )
        # Immediate update for startup display
        self.update(self._get_text())

    def _get_text(self) -> str:
        pct: Optional[int] = self._get_battery_percentage()
        if pct is None:
            return '<span foreground="grey">󰁺 N/A</span>'

        state: str = self._get_battery_state()
        icon, color = self._icon_for(pct, state)
        self._maybe_alert(pct)
        return f'<span foreground="{color}">{icon} {pct}%</span>'

    @staticmethod
    def _detect_batteries(manual: Optional[str]) -> List[Path]:
        if manual:
            path = Path(manual)
            return [path] if path.exists() else []
        return [p for p in Path("/sys/class/power_supply").glob("BAT*") if p.is_dir()]

    def _monitor_battery(self) -> None:
        """Continuously listen for udev power events and refresh widget text."""
        try:
            context = pyudev.Context()
            monitor = pyudev.Monitor.from_netlink(context)
            monitor.filter_by(subsystem="power_supply")
            monitor.start()
        except Exception as e:
            logger.error("BatteryWidget: Failed to start udev monitor: %s", e)
            return

        for device in iter(lambda: monitor.poll(timeout=1000), None):
            if self._stop_event.is_set():
                break
            if not device or device.properties.get("POWER_SUPPLY_TYPE") != "Battery":
                continue
            now = time.monotonic_ns()
            if now - self._last_update < self.debounce_ns:
                continue
            self._last_update = now
            try:
                self.qtile.call_soon_threadsafe(self.update, self._get_text())
            except Exception as e:
                logger.error("BatteryWidget: Failed to trigger redraw: %s", e)

    def finalize(self) -> None:
        """Ensure thread and resources shut down cleanly."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        super().finalize()
        logger.info("BatteryWidget stopped cleanly")

    def _read_int(self, path: Path, name: str) -> Optional[int]:
        try:
            return int((path / name).read_text().strip())
        except (FileNotFoundError, ValueError):
            return None

    def _get_battery_percentage(self) -> Optional[int]:
        values: List[Optional[int]] = [
            self._read_int(p, "capacity") for p in self.battery_paths
        ]
        valid = [v for v in values if v is not None]
        return sum(valid) // len(valid) if valid else None

    def _get_battery_state(self) -> str:
        try:
            ac_online = Path("/sys/class/power_supply/AC/online").read_text().strip()
            if ac_online == "1":
                return "charging"
        except (FileNotFoundError, ValueError):
            pass

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
        now = time.monotonic()
        if now - self._last_alert_time < self.alert_interval_s:
            return
        self._last_alert_time = now
        try:
            subprocess.Popen(
                ["notify-send", "Low Battery", f"{pct}% remaining"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as e:
            logger.error("BatteryWidget: Failed to send notification: %s", e)
