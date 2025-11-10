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
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pyudev  # type: ignore[import-untyped]
from libqtile.log_utils import logger
from qtile_extras import widget

BATTERY_ICONS: Tuple[Tuple[int, str, str], ...] = (
    (95, "", "orchid"),
    (85, "", "limegreen"),
    (75, "", "palegreen"),
    (60, "", "tan"),
    (40, "", "moccasin"),
    (30, "", "goldenrod"),
    (20, "", "tomato"),
    (0, "", "indianred"),
)

CHARGING_ICON: str = "󱐋"


@dataclass
class _BatteryState:
    """A normalized snapshot of the battery's state used to avoid redundant redraws."""

    status: str
    capacity: Optional[int]

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, _BatteryState):
            return NotImplemented
        return (self.status or "").lower() == (
            other.status or ""
        ).lower() and self.capacity == other.capacity


class BatteryWidget(widget.TextBox):  # type: ignore[misc]
    """
    Robust, notification-free, event-driven battery widget for Qtile.

    • Uses udev power_supply events when available.
    • Thread-safe and resource-clean on shutdown.
    """

    def __init__(
        self,
        critical: int = 25,
        debounce_s: float = 1.0,
        battery_path: Optional[str] = None,
        colors: Optional[Dict[str, str]] = None,
        **config: Any,
    ) -> None:
        super().__init__("", **config)

        self.critical: int = max(1, min(critical, 100))
        self.debounce_ns: int = int(max(debounce_s, 0.0) * 1e9)
        self.colors: Dict[str, str] = colors or {}

        self._stop_event = threading.Event()
        self._last_update_ns: int = 0
        self._monitor_thread: Optional[threading.Thread] = None
        self._shutdown_write_fd: Optional[int] = None
        self._shutdown_read_fd: Optional[int] = None
        self._cached_state = _BatteryState("unknown", None)
        self._energy_full_cache: Dict[Path, Optional[float]] = {}

        self.battery_paths: List[Path] = self._detect_batteries(battery_path)
        if not self.battery_paths:
            logger.warning(
                "BatteryWidget: No battery detected in /sys/class/power_supply"
            )
            self.text = '<span foreground="grey"> N/A</span>'

        self.add_callbacks({"Button1": self._manual_refresh})

    # Lifecycle management

    def _configure(self, qtile: Any, bar: Any) -> None:
        super()._configure(qtile, bar)
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(target=self._run_monitor, daemon=True)

        try:
            self._update_state()
            text = self._compose_text()
            self.qtile.call_soon_threadsafe(self._update_text_safely, text)
        except Exception as e:
            logger.error(f"BatteryWidget: Initial update failed: {e}")

        self._monitor_thread.start()

    def finalize(self) -> None:
        """Ensure clean thread shutdown and file descriptor closure."""
        if self._shutdown_write_fd is not None:
            try:
                os.write(self._shutdown_write_fd, b"x")
            except Exception:
                pass

        self._stop_event.set()

        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)

        for fd in (self._shutdown_read_fd, self._shutdown_write_fd):
            if fd is not None:
                try:
                    os.fstat(fd)
                    os.close(fd)
                except Exception:
                    pass

        super().finalize()
        logger.debug("BatteryWidget: Stopped cleanly")

    # Event / polling loop

    def _run_monitor(self) -> None:
        """Runs the udev event monitor loop."""
        try:
            self._event_loop()
        except Exception as e:
            logger.error(f"BatteryWidget: udev monitor failed: {e}")

    def _event_loop(self) -> None:
        """Main udev event monitor loop."""
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem="power_supply")
        monitor.start()
        monitor_fd = monitor.fileno()

        shutdown_r, shutdown_w = self._create_shutdown_pipe()
        self._shutdown_read_fd = shutdown_r
        self._shutdown_write_fd = shutdown_w

        try:
            while not self._stop_event.is_set():
                ready, _, _ = select.select([monitor_fd, shutdown_r], [], [], 1.0)
                if shutdown_r in ready or self._stop_event.is_set():
                    break

                if monitor_fd not in ready:
                    continue

                try:
                    device = monitor.poll(timeout=0)
                except Exception:
                    device = None
                if device is None:
                    continue

                now_ns = time.monotonic_ns()
                if now_ns - self._last_update_ns < self.debounce_ns:
                    continue
                self._last_update_ns = now_ns

                self._safe_redraw()

        finally:
            for fd in (shutdown_r, shutdown_w):
                try:
                    os.close(fd)
                except Exception:
                    pass
            logger.debug("BatteryWidget: udev loop terminated")

    # Core helpers

    def _safe_redraw(self) -> None:
        """Recompute text and refresh display safely."""
        try:
            if self._update_state():
                text = self._compose_text()
                self.qtile.call_soon_threadsafe(self._update_text_safely, text)
        except Exception as e:
            logger.error(f"BatteryWidget: redraw failed: {e}")

    @staticmethod
    def _create_shutdown_pipe() -> Tuple[int, int]:
        r, w = os.pipe()
        flags = fcntl.fcntl(w, fcntl.F_GETFL)
        fcntl.fcntl(w, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        return r, w

    @staticmethod
    def _detect_batteries(manual: Optional[str]) -> List[Path]:
        if manual:
            path = Path(manual)
            return [path] if path.exists() else []
        base = Path("/sys/class/power_supply")
        return [p for p in base.glob("BAT*") if p.is_dir()]

    def _manual_refresh(self) -> None:
        self._safe_redraw()

    # Data collection and formatting

    def _update_state(self) -> bool:
        """
        Fetch battery data, update the cached state, and return True if changed.
        """
        battery_data = {p: self._read_battery_info(p) for p in self.battery_paths}
        pct = self._compute_percentage(battery_data)
        status = self._derive_state(battery_data)

        new_state = _BatteryState(status, pct)
        if new_state == self._cached_state:
            return False

        self._cached_state = new_state
        return True

    def _compose_text(self) -> str:
        """Compose the display text based on the cached battery state."""
        state = self._cached_state
        if state.capacity is None:
            return '<span foreground="grey"> N/A</span>'

        pct = state.capacity
        status = state.status

        icon, color = self._icon_for(pct, status)
        return f'<span foreground="{color}">{icon}\u00a0  {pct}%</span>'

    def _read_battery_info(self, path: Path) -> Dict[str, Optional[str]]:
        """Read key sysfs fields for one battery safely."""
        keys = [
            "capacity",
            "status",
            "energy_now",
            "charge_now",
            "energy_full",
            "charge_full",
        ]
        out: Dict[str, Optional[str]] = {}
        for k in keys:
            try:
                out[k] = (path / k).read_text(encoding="utf-8", errors="ignore").strip()
            except Exception:
                out[k] = None
        return out

    def _compute_percentage(
        self, battery_data: Dict[Path, Dict[str, Optional[str]]]
    ) -> Optional[int]:
        """Compute averaged capacity across batteries."""
        values: List[float] = []
        for path, data in battery_data.items():
            cap = data.get("capacity")
            if cap is not None:
                try:
                    values.append(float(int(cap)))
                    continue
                except Exception:
                    pass

            now_s = data.get("energy_now") or data.get("charge_now")
            full_s = data.get("energy_full") or data.get("charge_full")
            try:
                now = float(now_s) if now_s is not None else None
                if path not in self._energy_full_cache:
                    self._energy_full_cache[path] = float(full_s) if full_s else None
                full = self._energy_full_cache.get(path)
                if now is not None and full and full > 0:
                    values.append((now / full) * 100.0)
            except Exception:
                continue

        if not values:
            return None
        avg = sum(values) / len(values)
        return int(round(max(0.0, min(100.0, avg))))

    def _derive_state(self, battery_data: Dict[Path, Dict[str, Optional[str]]]) -> str:
        """Return overall charging/discharging/full/unknown."""
        for data in battery_data.values():
            state = data.get("status")
            if state:
                lower = state.lower()
                if lower in ("charging", "discharging", "full"):
                    return lower
        for power_supply in Path("/sys/class/power_supply").glob("*"):
            try:
                if (power_supply / "type").read_text().strip() == "Mains":
                    if (power_supply / "online").read_text().strip() == "1":
                        return "charging"
            except Exception:
                continue
        return "unknown"

    def _icon_for(self, pct: int, state: str) -> Tuple[str, str]:
        """Choose icon and color."""
        for threshold, icon, color in BATTERY_ICONS:
            if pct >= threshold:
                if state == "charging" and pct < 100:
                    icon = f"{CHARGING_ICON} {icon}"
                return icon, self.colors.get(color, color)
        return "", "grey"

    def _update_text_safely(self, text: str) -> None:
        try:
            if getattr(self, "bar", None):
                if self.text != text:
                    self.text = text
                    self.bar.draw()
            else:
                self.text = text
        except Exception as e:
            logger.error("BatteryWidget: Update failed: %s", e)

    # Public API

    def get_status(self) -> Tuple[Optional[int], str]:
        """Return (percentage, state) for external use."""
        try:
            data = {p: self._read_battery_info(p) for p in self.battery_paths}
            return self._compute_percentage(data), self._derive_state(data)
        except Exception:
            return None, "unknown"
