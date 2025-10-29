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


import logging
import threading
import time
from pathlib import Path
from typing import Any, Optional, Tuple

import pyudev  # type: ignore[import-untyped]
from libqtile.command.base import expose_command
from qtile_extras.widget import GenPollText

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.FileHandler("/tmp/acpiwidget.log", encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(threadName)s: %(message)s")
    )
    logger.addHandler(handler)

CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"
EMPTY_ICON = "󰁺"

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

DEBOUNCE_SECONDS = 0.25


class BatteryWidget(GenPollText):  # type: ignore[misc]
    """Battery widget using pure pyudev monitoring (no polling, no acpi)."""

    def __init__(
        self,
        show_time: bool = False,
        critical_threshold: int = 20,
        battery_path: str = "/sys/class/power_supply/BAT0",
        **config: Any,
    ) -> None:
        self.battery_path = Path(battery_path)
        self.battery_name = self.battery_path.name
        self.show_time = show_time
        self.critical = max(5, min(critical_threshold, 25))

        self._stop_event = threading.Event()
        self._update_lock = threading.Lock()
        self._last_update = 0.0
        self._last_status: Optional[Tuple[int, str]] = None
        self._monitor_thread = threading.Thread(
            target=self._udev_loop, daemon=True, name="udev-monitor"
        )

        super().__init__(func=self._poll, update_interval=9999.0, **config)
        self._monitor_thread.start()

        logger.debug("BatteryWidget initialized: path=%s", self.battery_path)

    def finalize(self) -> None:
        """Graceful shutdown."""
        logger.debug("Finalizing BatteryWidget")
        self._stop_event.set()
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
        super().finalize()

    def _udev_loop(self) -> None:
        """Listen for udev power events and trigger redraws."""
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem="power_supply")
        logger.debug("udev monitor started for power_supply events")

        for device in iter(monitor.poll, None):
            if self._stop_event.is_set():
                break
            if not isinstance(device, pyudev.Device):
                continue
            name = device.sys_name
            if name not in {self.battery_name, "AC", "AC0", "ACAD", "ACPI0003:00"}:
                continue
            with self._update_lock:
                now = time.monotonic()
                if now - self._last_update < DEBOUNCE_SECONDS:
                    continue
                self._last_update = now
            logger.debug("udev event received: %s (action=%s)", name, device.action)
            self._schedule_update()

    def _schedule_update(self) -> None:
        """Thread-safe immediate UI update."""
        try:

            def redraw() -> None:
                new_text = self._poll()
                if new_text != getattr(self, "text", None):
                    self.text = new_text
                    self.bar.draw()
                    logger.debug("BatteryWidget redrawn")

            self.qtile.call_soon_threadsafe(redraw)
        except Exception:
            logger.exception("Error scheduling update")

    def _poll(self) -> str:
        """Read and render battery data."""
        try:
            pct = max(0, min(100, self._read_int("capacity")))
            state = self._read("status").lower()
        except Exception:
            logger.exception("Error reading battery sysfs data")
            return f'<span foreground="grey">{EMPTY_ICON} N/A</span>'

        icon, color = self._icon_for(pct, state)
        text = f'<span foreground="{color}">{icon} {pct}%</span>'
        return text

    def _read(self, name: str) -> str:
        """Read a sysfs attribute value."""
        with open(self.battery_path / name, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _read_int(self, name: str) -> int:
        """Read an integer sysfs attribute."""
        return int(self._read(name))

    def _icon_for(self, pct: int, state: str) -> Tuple[str, str]:
        """Select icon and colour according to battery percentage and state."""
        if state == "full":
            return FULL_ICON, "lime"
        if state in ("unknown", "not charging"):
            return BATTERY_ICONS[0][1], "grey"

        icon, color = EMPTY_ICON, "grey"
        for threshold, i, c in BATTERY_ICONS:
            if pct >= threshold:
                icon, color = i, c
                break

        if state == "charging":
            icon = f"{CHARGING_ICON} {icon}"

        if pct <= self.critical:
            icon, color = EMPTY_ICON, "red" if pct <= 5 else "orange"

        return icon, color

    @expose_command()
    def refresh(self) -> None:
        """Manual refresh trigger."""
        logger.debug("Manual refresh triggered")
        self._schedule_update()
