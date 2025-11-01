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

import os
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
DEFAULT_POLL_INTERVAL_S = 30


class BatteryWidget(widget.TextBox):  # type: ignore[misc]
    """
    Behavioural summary (public API preserved):
    - Alerting controlled by `enable_alert`, `critical`, `alert_interval_s` and `alert_command`.
    - Accepts `battery_path` for manual override and `colors` mapping for custom colours.
    - Uses hybrid update model: udev event-driven + periodic polling fallback.
    """

    def __init__(
        self,
        critical: int = 25,
        debounce_s: float = 0.25,
        battery_path: Optional[str] = None,
        colors: Optional[Dict[str, str]] = None,
        enable_alert: bool = True,
        log_path: str = "/tmp/batterywidget.log",
        alert_interval_s: int = 300,
        poll_interval_s: int = DEFAULT_POLL_INTERVAL_S,
        alert_command: Optional[List[str]] = None,
        **config: Any,
    ) -> None:
        super().__init__("", **config)
        self.critical: int = max(1, min(critical, 100))
        self.debounce_ns: int = int(max(0.0, debounce_s) * 1e9)
        self.alert_interval_s: int = max(alert_interval_s, 60)
        self.enable_alert: bool = enable_alert
        self.colors: Dict[str, str] = colors or {}
        self.log_path: Path = Path(log_path)
        self.poll_interval_s: int = max(5, poll_interval_s)
        self.alert_command: List[str] = (
            alert_command if alert_command is not None else ["notify-send"]
        )

        self._stop_event: threading.Event = threading.Event()
        self._last_update: int = 0
        self._last_alert_time: float = 0.0
        self._udev_thread: Optional[threading.Thread] = None
        self._poll_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self.battery_paths: List[Path] = self._detect_batteries(battery_path)
        if not self.battery_paths:
            logger.warning(
                "BatteryWidget: No battery detected in /sys/class/power_supply"
            )

    def _configure(self, qtile: Any, bar: Any) -> None:
        """Start background threads and perform an immediate update."""
        super()._configure(qtile, bar)

        # Ensure any previous threads are stopped (defensive on reload)
        self._stop_event.clear()

        self._udev_thread = threading.Thread(target=self._monitor_battery, daemon=True)
        self._poll_thread = threading.Thread(target=self._periodic_refresh, daemon=True)
        self._udev_thread.start()
        self._poll_thread.start()

        logger.info(
            "BatteryWidget initialized with %d battery(ies)", len(self.battery_paths)
        )

        # Immediate update for startup display
        try:
            # Use call_soon_threadsafe to ensure update runs on Qtile's loop
            self.qtile.call_soon_threadsafe(self._safe_update, self._get_text())
        except Exception as e:
            logger.error("BatteryWidget: initial update failed: %s", e)

    def _get_text(self) -> str:
        """Produce the Pango-markup text for the widget."""
        with self._lock:
            pct: Optional[int] = self._get_battery_percentage()
            if pct is None:
                return '<span foreground="grey">󰁺 N/A</span>'

            state: str = self._get_battery_state()
            icon, color = self._icon_for(pct, state)
            # Alerting may update _last_alert_time; call outside lock if desired,
            # but we keep it inside to avoid races with multiple threads.
            self._maybe_alert(pct)
            return f'<span foreground="{color}">{icon} {pct}%</span>'

    @staticmethod
    def _detect_batteries(manual: Optional[str]) -> List[Path]:
        if manual:
            path = Path(manual)
            return [path] if path.exists() else []
        return [p for p in Path("/sys/class/power_supply").glob("BAT*") if p.is_dir()]

    def _monitor_battery(self) -> None:
        """Listen for udev power_supply events and trigger updates.

        Uses a short poll timeout to allow prompt shutdown.
        """
        try:
            context = pyudev.Context()
            monitor = pyudev.Monitor.from_netlink(context)
            monitor.filter_by(subsystem="power_supply")
            monitor.start()
        except Exception as e:
            logger.error("BatteryWidget: Failed to start udev monitor: %s", e)
            return

        # Poll with small timeout so that stop checks are frequent
        while not self._stop_event.is_set():
            try:
                device = monitor.poll(timeout=2.5)
            except Exception as e:
                logger.error("BatteryWidget: udev poll error: %s", e)
                break

            if self._stop_event.is_set():
                break
            if device is None:
                continue

            # Only respond to battery-type devices
            if device.properties.get("POWER_SUPPLY_TYPE") != "Battery":
                continue

            now = time.monotonic_ns()
            if now - self._last_update < self.debounce_ns:
                continue
            self._last_update = now

            try:
                # Schedule update on main loop
                self.qtile.call_soon_threadsafe(self._safe_update, self._get_text())
            except Exception as e:
                logger.error("BatteryWidget: Failed to schedule redraw: %s", e)

    def _periodic_refresh(self) -> None:
        """Fallback polling to keep the display fresh when udev is quiet."""
        while not self._stop_event.is_set():
            try:
                self.qtile.call_soon_threadsafe(self._safe_update, self._get_text())
            except Exception as e:
                logger.debug("BatteryWidget: periodic update failed: %s", e)
            # Wait with early exit support
            if self._stop_event.wait(self.poll_interval_s):
                break

    def finalize(self) -> None:
        """Halt background threads and perform cleanup."""
        self._stop_event.set()
        # Join with timeout to avoid hanging shutdown
        for t in (self._udev_thread, self._poll_thread):
            if t and t.is_alive():
                t.join(timeout=2.0)
        try:
            super().finalize()
        except Exception:
            # Some versions of Qtile may raise on finalize; swallow to be robust
            pass
        logger.info("BatteryWidget stopped cleanly")

    def _read_int(self, path: Path, name: str) -> Optional[int]:
        try:
            return int((path / name).read_text().strip())
        except (FileNotFoundError, ValueError):
            return None

    def _get_battery_percentage(self) -> Optional[int]:
        """Compute a weighted percentage from available sysfs values.

        Prefer energy_after/energy_full if available, else fall back to capacity.
        """
        values: List[Optional[float]] = []

        for p in self.battery_paths:
            # Try energy_now / energy_full (or charge_ variants)
            energy_now = self._read_float(p, "energy_now") or self._read_float(
                p, "charge_now"
            )
            energy_full = self._read_float(p, "energy_full") or self._read_float(
                p, "charge_full"
            )
            if energy_now is not None and energy_full:
                values.append((energy_now / energy_full) * 100.0)
                continue

            # Fallback to capacity file
            cap = self._read_int(p, "capacity")
            if cap is not None:
                values.append(float(cap))

        valid = [v for v in values if v is not None]
        if not valid:
            return None
        # Weighted average by equal battery; if energy values were used they are already percentage
        avg = sum(valid) / len(valid)
        return int(round(avg))

    def _read_float(self, path: Path, name: str) -> Optional[float]:
        try:
            return float((path / name).read_text().strip())
        except (FileNotFoundError, ValueError):
            return None

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

        # Only attempt notification if DBUS session appears available or alternate command provided
        env_ok = (
            bool(os.environ.get("DBUS_SESSION_BUS_ADDRESS"))
            or self.alert_command[0] != "notify-send"
        )
        if not env_ok:
            logger.debug("BatteryWidget: DBUS session not found; skipping notify-send")
            return

        try:
            subprocess.Popen(
                self.alert_command + ["Low Battery", f"{pct}% remaining"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except Exception as e:
            logger.error("BatteryWidget: Failed to send notification: %s", e)

    def _safe_update(self, text: str) -> None:
        """Update the widget text and force a bar redraw even if identical.

        This method must be called on Qtile's event loop (we schedule it using
        call_soon_threadsafe from background threads).
        """
        try:
            # Minimal change: set self.text so TextBox state is consistent
            self.text = text
            # Force bar redraw. Accessing self.bar may raise if widget detached; handle gracefully.
            try:
                if getattr(self, "bar", None):
                    self.bar.draw()
            except Exception as e:
                logger.debug("BatteryWidget: bar.draw() failed: %s", e)
        except Exception as e:
            logger.error("BatteryWidget: update failed: %s", e)
