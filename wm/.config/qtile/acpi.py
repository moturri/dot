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
import os
import subprocess
import threading
import time
from typing import Any, Optional, Tuple

import pyudev  # type: ignore[import-untyped]
from libqtile.command.base import expose_command
from qtile_extras.widget import GenPollText

logger = logging.getLogger(__name__)

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


def run(cmd: list[str], timeout: float = 0.5) -> Optional[str]:
    """Run a command safely with short timeout."""
    try:
        return subprocess.check_output(
            cmd,
            text=True,
            timeout=timeout,
            env={"LC_ALL": "C.UTF-8", **os.environ},
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return None


class AcpiWidget(GenPollText):  # type: ignore[misc]
    """Battery widget with pyudev event monitoring and fallback polling."""

    def __init__(
        self,
        show_time: bool = False,
        critical_threshold: int = 20,
        battery_path: str = "/sys/class/power_supply/BAT0",
        **config: Any,
    ) -> None:
        self.path = battery_path
        self.show_time = show_time
        self.critical = max(5, min(critical_threshold, 25))
        self._stop_event = threading.Event()
        self._last_update = 0.0

        # Polling interval acts as fallback when events fail
        super().__init__(func=self._poll, update_interval=60.0, **config)

        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def finalize(self) -> None:
        """Ensure background thread stops when widget is destroyed."""
        self._stop_event.set()
        super().finalize()  # type: ignore[no-untyped-call]

    def _monitor_loop(self) -> None:
        """Monitor udev events and trigger updates."""
        while not self._stop_event.is_set():
            try:
                self._listen_once()
            except Exception as e:
                logger.warning("Battery monitor error: %s", e)
                time.sleep(3.0)  # brief pause before retry

    def _listen_once(self) -> None:
        """Attach one monitor session to pyudev (auto-reconnects if lost)."""
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem="power_supply")

        for device in iter(monitor.poll, None):
            if self._stop_event.is_set():
                break
            if not isinstance(device, pyudev.Device):
                continue
            if device.sys_name != os.path.basename(self.path):
                continue

            # Debounce: ignore if events come too fast
            now = time.monotonic()
            if now - self._last_update < 1.0:
                continue
            self._last_update = now

            if hasattr(self.qtile, "call_soon_threadsafe"):
                self.qtile.call_soon_threadsafe(self.force_update)

    def _poll(self) -> str:
        """Main display method: combines sysfs and acpi sources."""
        status = self._from_sys() or self._from_acpi()
        if not status:
            return f'<span foreground="grey">{EMPTY_ICON} N/A</span>'
        pct, state, mins = status
        icon, color = self._icon(pct, state)
        time_str = self._format_time(mins) if self.show_time and mins else ""
        return f'<span foreground="{color}">{icon} {pct}%{time_str}</span>'

    def _from_sys(self) -> Optional[Tuple[int, str, Optional[int]]]:
        """Read battery data from sysfs (preferred)."""
        try:
            pct = self._read_int("capacity")
            state = self._read("status").lower()
            mins = self._estimate_time(state)
            return pct, state, mins
        except (OSError, ValueError, PermissionError):
            return None

    def _read(self, name: str) -> str:
        with open(os.path.join(self.path, name), "r", encoding="utf-8") as f:
            return f.read().strip()

    def _read_int(self, name: str) -> int:
        return int(self._read(name))

    def _estimate_time(self, state: str) -> Optional[int]:
        """Roughly estimate remaining time in minutes when discharging."""
        if state != "discharging":
            return None
        for prefix in ("charge", "energy"):
            try:
                now = self._read_int(f"{prefix}_now")
                rate = self._read_int(
                    "current_now" if prefix == "charge" else "power_now"
                )
                if rate > 0:
                    return int((now / rate) * 60)
            except (OSError, ValueError):
                continue
        return None

    def _from_acpi(self) -> Optional[Tuple[int, str, Optional[int]]]:
        """Fallback: parse output from acpi -b."""
        output = run(["acpi", "-b"])
        if not output:
            return None
        try:
            after_colon = output.split(":", 1)[1].strip()
            parts = [p.strip() for p in after_colon.split(",")]
            state = parts[0].lower()
            pct = int(parts[1].rstrip("%"))
            mins = None
            if len(parts) > 2:
                time_field = parts[2]
                if ":" in time_field:
                    h, m = map(int, time_field.split(":")[:2])
                    mins = h * 60 + m
            return pct, state, mins
        except (IndexError, ValueError):
            return None

    def _icon(self, pct: int, state: str) -> Tuple[str, str]:
        """Return icon and color based on charge level and state."""
        if state == "charging":
            for threshold, icon, color in BATTERY_ICONS:
                if pct >= threshold:
                    return f"{CHARGING_ICON} {icon}", color
            return f"{CHARGING_ICON} {EMPTY_ICON}", "darkgreen"
        if state == "full":
            return FULL_ICON, "lime"
        if state in ("unknown", "not charging"):
            return BATTERY_ICONS[0][1], "grey"
        if pct <= self.critical:
            return EMPTY_ICON, "red" if pct <= 5 else "orange"
        for threshold, icon, color in BATTERY_ICONS:
            if pct >= threshold:
                return icon, color
        return EMPTY_ICON, "grey"

    @staticmethod
    def _format_time(mins: int) -> str:
        """Convert minutes to formatted (h m) string."""
        h, m = divmod(mins, 60)
        return f" ({h}h {m:02d}m)" if h else f" ({m}m)"

    @expose_command()
    def refresh(self) -> None:
        """Manual update trigger."""
        self.force_update()
