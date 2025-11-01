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

import fcntl
import os
import select
import subprocess
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

_T = TypeVar("_T")

import pyudev  # type: ignore[import-untyped]
from libqtile.log_utils import logger
from qtile_extras import widget

BATTERY_ICONS: Tuple[Tuple[int, str, str], ...] = (
    (90, "󰂁", "limegreen"),
    (80, "󰂀", "palegreen"),
    (70, "󰁿", "lightgreen"),
    (60, "󰁾", "tan"),
    (40, "󰁽", "moccasin"),
    (30, "󰁻", "goldenrod"),
    (20, "󰁺", "tomato"),
    (0, "󰁹", "indianred"),
)

CHARGING_ICON: str = "󱐋"


@dataclass
class _BatteryState:
    """A snapshot of the battery's state."""

    status: str
    capacity: Optional[int]


class BatteryWidget(widget.TextBox):  # type: ignore[misc]
    """
    A pure event-driven battery widget for Qtile.
    It listens for udev power events (no polling) and updates text only when necessary.
    """

    def __init__(
        self,
        critical: int = 25,
        debounce_s: float = 0.2,
        battery_path: Optional[str] = None,
        enable_alert: bool = True,
        alert_interval_s: int = 300,
        alert_command: Optional[List[str]] = None,
        colors: Optional[Dict[str, str]] = None,
        **config: Any,
    ) -> None:
        super().__init__("", **config)

        self.critical: int = max(1, min(critical, 100))
        self.debounce_ns: int = int(max(debounce_s, 0.0) * 1e9)
        self.enable_alert: bool = enable_alert
        self.alert_interval_s: int = max(alert_interval_s, 60)
        self.alert_command: List[str] = alert_command or ["notify-send"]
        self.colors: Dict[str, str] = colors or {}

        self._stop_event: threading.Event = threading.Event()
        self._last_update_ns: int = 0
        self._last_alert_time: float = 0.0
        self._monitor_thread: Optional[threading.Thread] = None
        self._shutdown_write_fd: Optional[int] = None

        # Cache to avoid redundant redraws
        self._cached_state: _BatteryState = _BatteryState("unknown", None)

        self.battery_paths: List[Path] = self._detect_batteries(battery_path)
        if not self.battery_paths:
            logger.warning(
                "BatteryWidget: No battery detected in /sys/class/power_supply"
            )
            self.text = '<span foreground="grey">󰁹 N/A</span>'

        # Allow manual refresh by clicking
        self.add_callbacks({"Button1": self._manual_refresh})

    def _configure(self, qtile: Any, bar: Any) -> None:
        """Start udev event thread and render initial state."""
        super()._configure(qtile, bar)

        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._event_loop, daemon=True)
        self._monitor_thread.start()

        # Initial draw
        try:
            text = self._compose_text()
            self.qtile.call_soon_threadsafe(self._safe_update, text)
        except Exception as e:
            logger.error("BatteryWidget: Initial update failed: %s", e)

        logger.info(
            "BatteryWidget initialized with %d battery(ies)", len(self.battery_paths)
        )

    def finalize(self) -> None:
        """Cleanly stop background thread."""
        self._stop_event.set()
        if self._shutdown_write_fd is not None:
            try:
                os.write(self._shutdown_write_fd, b"x")
            except Exception:
                pass

        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)

        super().finalize()
        logger.info("BatteryWidget stopped cleanly")

    def _event_loop(self) -> None:
        """Listen for power-related udev events and trigger updates."""
        try:
            context = pyudev.Context()
            monitor = pyudev.Monitor.from_netlink(context)
            monitor.filter_by(subsystem="power_supply")
            monitor.start()
            monitor_fd = monitor.fileno()
        except Exception as e:
            logger.error("BatteryWidget: Failed to start udev monitor: %s", e)
            return

        shutdown_r, shutdown_w = self._create_shutdown_pipe()
        self._shutdown_write_fd = shutdown_w

        try:
            while not self._stop_event.is_set():
                ready, _, _ = select.select([monitor_fd, shutdown_r], [], [], 1.0)
                if shutdown_r in ready or self._stop_event.is_set():
                    break

                if monitor_fd not in ready:
                    continue

                device = monitor.poll(timeout=0)
                if device is None:
                    continue

                power_type: str = device.properties.get("POWER_SUPPLY_TYPE", "")
                if power_type not in ("Battery", "Mains", "USB"):
                    continue

                now_ns = time.monotonic_ns()
                if now_ns - self._last_update_ns < self.debounce_ns:
                    continue
                self._last_update_ns = now_ns

                text = self._compose_text()
                if text != self.text:
                    self.qtile.call_soon_threadsafe(self._safe_update, text)

        except Exception as e:
            logger.error("BatteryWidget: Event loop error: %s", e)

        finally:
            try:
                os.close(shutdown_r)
                os.close(shutdown_w)
            except Exception:
                pass
            logger.info("BatteryWidget: Event loop terminated")

    @staticmethod
    def _create_shutdown_pipe() -> Tuple[int, int]:
        """Create a pipe for interrupting select() on shutdown."""
        r, w = os.pipe()
        flags = fcntl.fcntl(w, fcntl.F_GETFL)
        fcntl.fcntl(w, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        return r, w

    def _manual_refresh(self) -> None:
        """Force immediate text update when widget is clicked."""
        try:
            text = self._compose_text()
            self._safe_update(text)
            logger.debug("BatteryWidget: Manual refresh triggered")
        except Exception as e:
            logger.error("BatteryWidget: Manual refresh failed: %s", e)

    @staticmethod
    def _detect_batteries(manual: Optional[str]) -> List[Path]:
        """Detect battery directories under /sys/class/power_supply."""
        if manual:
            path = Path(manual)
            return [path] if path.exists() else []
        base = Path("/sys/class/power_supply")
        return [p for p in base.glob("BAT*") if p.is_dir()]

    def _compose_text(self) -> str:
        """Compose display text with icon, color, and percentage."""
        pct = self._get_battery_percentage()
        if pct is None:
            return '<span foreground="grey">󰁹 N/A</span>'

        state = self._get_battery_state()
        new_state = _BatteryState(state, pct)
        if new_state == self._cached_state and self.text:
            return self.text  # No change, no need to re-render
        self._cached_state = new_state

        self._maybe_alert(pct)
        icon, color = self._icon_for(pct, state)
        return f'<span foreground="{color}">{icon}  {pct}%</span>'

    def _get_battery_percentage(self) -> Optional[int]:
        """Read capacity or energy values and compute percentage."""
        values: List[float] = []
        for path in self.battery_paths:
            cap = self._read_value(path, "capacity", int)
            if cap is not None:
                values.append(float(cap))
                continue

            now = self._read_value(path, "energy_now", float) or self._read_value(
                path, "charge_now", float
            )
            full = self._read_value(path, "energy_full", float) or self._read_value(
                path, "charge_full", float
            )
            if now is not None and full and full > 0:
                values.append((now / full) * 100.0)

        if not values:
            return None
        avg = sum(values) / len(values)
        return int(round(max(0.0, min(100.0, avg))))

    def _get_battery_state(self) -> str:
        """Read battery or AC status."""
        # Prioritize the battery's own status report, which can be more accurate
        # (e.g., distinguishes between 'Charging' and 'Full').
        for p in self.battery_paths:
            state = self._read_value(p, "status", str)
            if state:
                lower = state.lower()
                if lower in ("charging", "discharging", "full"):
                    return lower

        # Fallback to checking for an online AC adapter
        for power_supply in Path("/sys/class/power_supply").glob("*"):
            try:
                if (power_supply / "type").read_text().strip() == "Mains":
                    if (power_supply / "online").read_text().strip() == "1":
                        return "charging"  # Assume charging if AC is on
            except (FileNotFoundError, ValueError):
                continue

        return "unknown"

    def _read_value(
        self, path: Path, name: str, converter: Callable[[str], _T]
    ) -> Optional[_T]:
        """Safely read a value from a sysfs file."""
        try:
            return converter((path / name).read_text().strip())
        except (FileNotFoundError, ValueError):
            return None

    def _icon_for(self, pct: int, state: str) -> Tuple[str, str]:
        """Return appropriate icon and color for given battery level."""
        if pct >= 100 and state in ("charging", "full"):
            return "󰂄", "limegreen"

        for threshold, icon, color in BATTERY_ICONS:
            if pct >= threshold:
                if state == "charging":
                    icon = f"{CHARGING_ICON} {icon}"
                return icon, self.colors.get(color, color)
        return "󰁻", "grey"

    def _maybe_alert(self, pct: int) -> None:
        """Trigger low-battery alert if below threshold."""
        if not self.enable_alert or pct > self.critical:
            return
        now = time.monotonic()
        if now - self._last_alert_time < self.alert_interval_s:
            return
        self._last_alert_time = now

        env_ok = (
            bool(os.environ.get("DBUS_SESSION_BUS_ADDRESS"))
            or self.alert_command[0] != "notify-send"
        )
        if not env_ok:
            logger.debug("BatteryWidget: No DBUS session for notifications")
            return

        try:
            subprocess.Popen(
                self.alert_command + ["Low Battery", f"{pct}% remaining"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            logger.info("BatteryWidget: Low battery alert sent (%d%%)", pct)
        except Exception as e:
            logger.error("BatteryWidget: Failed to send alert: %s", e)

    def _safe_update(self, text: str) -> None:
        """Safely update the widget text and redraw."""
        try:
            self.text = text
            if getattr(self, "bar", None):
                self.bar.draw()
        except Exception as e:
            logger.error("BatteryWidget: Update failed: %s", e)
