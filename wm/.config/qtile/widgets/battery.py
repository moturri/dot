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
import select
import socket
import subprocess
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional, Tuple

import pyudev  # type: ignore[import-untyped]
from libqtile.command.base import expose_command
from qtile_extras.widget import GenPollText

if TYPE_CHECKING:
    from pyudev import Monitor

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

DEBOUNCE_SECONDS = 1.0
ERROR_RETRY_SECONDS = 3.0
COMMAND_TIMEOUT = 0.5
FALLBACK_POLL_INTERVAL = 9999.0


def run_command(cmd: list[str], timeout: float = COMMAND_TIMEOUT) -> Optional[str]:
    """Run an external command safely and return its stdout or None on failure."""
    try:
        out = subprocess.check_output(
            cmd,
            text=True,
            timeout=timeout,
            stderr=subprocess.DEVNULL,
            env={"LC_ALL": "C.UTF-8", **os.environ},
        )
        return out.strip() if out else None
    except (subprocess.SubprocessError, FileNotFoundError, OSError):
        return None


class BatteryWidget(GenPollText):  # type: ignore[misc]
    """Battery widget using udev monitoring with acpid socket fallback."""

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
        self._battery_exists: Optional[bool] = None
        self._monitor: Optional["Monitor"] = None

        super().__init__(
            func=self._poll, update_interval=FALLBACK_POLL_INTERVAL, **config
        )

        self._udev_thread = threading.Thread(
            target=self._monitor_loop, daemon=True, name="udev-monitor"
        )
        self._acpid_thread = threading.Thread(
            target=self._acpid_listener, daemon=True, name="acpid-listener"
        )

        self._udev_thread.start()
        self._acpid_thread.start()

        logger.debug("BatteryWidget initialised with path=%s", self.battery_path)

    def finalize(self) -> None:
        """Graceful shutdown."""
        logger.debug("Finalising BatteryWidget")
        self._stop_event.set()

        if self._monitor is not None:
            send_stop = getattr(self._monitor, "send_stop_event", None)
            if callable(send_stop):
                try:
                    send_stop()
                except Exception:
                    logger.exception("Error stopping pyudev monitor")

        if self._udev_thread.is_alive():
            self._udev_thread.join(timeout=1.0)

        if self._acpid_thread.is_alive():
            self._acpid_thread.join(timeout=1.0)

        super().finalize()

    def _monitor_loop(self) -> None:
        """Listen to udev events and trigger updates."""
        logger.debug("Starting pyudev monitor loop")
        while not self._stop_event.is_set():
            try:
                self._udev_listen()
            except Exception as e:
                logger.warning("Battery monitor error: %s, retrying in 5s", e)
                time.sleep(5)  # Wait before retrying
        logger.debug("Exiting pyudev monitor loop")

    def _udev_listen(self) -> None:
        """Monitor power_supply subsystem for changes."""
        context = pyudev.Context()
        monitor = pyudev.Monitor.from_netlink(context)
        monitor.filter_by(subsystem="power_supply")
        self._monitor = monitor

        battery_names = {self.battery_path.name, "AC", "AC0", "ACAD", "ACPI0003:00"}
        logger.debug("Listening for power_supply events: %s", battery_names)

        for device in iter(monitor.poll, None):
            if self._stop_event.is_set():
                break
            if not isinstance(device, pyudev.Device):
                continue

            name = device.sys_name
            logger.debug(
                "udev event received: %s (action=%s)",
                name,
                getattr(device, "action", None),
            )

            if name in battery_names:
                with self._update_lock:
                    now = time.monotonic()
                    if now - self._last_update < DEBOUNCE_SECONDS:
                        continue
                    self._last_update = now
                logger.debug("Scheduling update for device: %s", name)
                self._schedule_update()

    def _acpid_listener(self) -> None:
        """Listen to /run/acpid.socket for power events as fallback."""
        sock_path = "/run/acpid.socket"
        if not os.path.exists(sock_path):
            logger.warning("acpid socket not found at %s", sock_path)
            return

        logger.debug("Starting acpid socket listener on %s", sock_path)
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
                s.connect(sock_path)
                s.setblocking(False)
                poller = select.poll()
                poller.register(s, select.POLLIN)

                while not self._stop_event.is_set():
                    events = poller.poll(1000)  # 1s timeout to allow graceful exit
                    for _, flag in events:
                        if flag & select.POLLIN:
                            # read and split lines since acpid may send multiple events
                            try:
                                raw = s.recv(4096)
                            except BlockingIOError:
                                continue
                            if not raw:
                                continue
                            for line in raw.decode(errors="ignore").splitlines():
                                data = line.strip()
                                if not data:
                                    continue
                                # Typical acpid event lines contain these tokens
                                if (
                                    "battery" in data
                                    or "ac_adapter" in data
                                ):
                                    logger.debug("acpid event: %s", data)
                                    with self._update_lock:
                                        now = time.monotonic()
                                        if now - self._last_update < DEBOUNCE_SECONDS:
                                            continue
                                        self._last_update = now
                                    self._schedule_update()
        except Exception:
            logger.exception("Error in acpid listener loop")

        logger.debug("Exiting acpid listener")

    def _schedule_update(self) -> None:
        """Thread-safe UI update trigger."""
        try:
            if hasattr(self.qtile, "call_soon_threadsafe"):
                self.qtile.call_soon_threadsafe(self.force_update)
            else:
                self.force_update()
            logger.debug("UI update scheduled/executed")
        except Exception:
            logger.exception("Error scheduling update")

    def _poll(self) -> str:
        """Read and render battery data for the widget."""
        status = self._get_status()
        logger.debug("Polling battery status: %s", status)
        if not status:
            return f'<span foreground="grey">{EMPTY_ICON} N/A</span>'
        pct, state, mins = status
        icon, color = self._icon_for(pct, state)
        t = self._fmt_time(mins) if (self.show_time and mins) else ""
        result = f'<span foreground="{color}">{icon} {pct}%{t}</span>'
        logger.debug("Rendered widget text: %s", result)
        return result

    def _get_status(self) -> Optional[Tuple[int, str, Optional[int]]]:
        """
        Get battery status from sysfs, falling back to acpi command.
        Keeping _from_acpi() as a last-resort fallback in case socket and udev fail.
        """
        if self._battery_exists is False:
            return self._from_acpi()

        status = self._from_sys()
        if status is None:
            return self._from_acpi()
        return status

    def _from_sys(self) -> Optional[Tuple[int, str, Optional[int]]]:
        """Get battery status from sysfs (preferred)."""
        try:
            pct = max(0, min(100, self._read_int("capacity")))
            state = self._read("status").lower()
            mins = self._estimate_time(state)
            self._battery_exists = True
            return pct, state, mins
        except Exception:
            self._battery_exists = None
            logger.exception("Error reading sysfs battery data")
            return None

    def _read(self, name: str) -> str:
        """Read a sysfs value for the battery."""
        with open(self.battery_path / name, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _read_int(self, name: str) -> int:
        return int(self._read(name))

    def _estimate_time(self, state: str) -> Optional[int]:
        """Estimate remaining time in minutes when discharging."""
        if state != "discharging":
            return None
        for prefix in ("charge", "energy"):
            try:
                now = self._read_int(f"{prefix}_now")
                rate_key = "current_now" if prefix == "charge" else "power_now"
                rate = self._read_int(rate_key)
                if rate > 0:
                    return int((now / rate) * 60)
            except Exception:
                continue
        return None

    def _from_acpi(self) -> Optional[Tuple[int, str, Optional[int]]]:
        """Fallback that uses the acpi command if socket/udev/sysfs are unavailable."""
        out = run_command(["acpi", "-b"])
        if not out:
            return None
        try:
            _, info = out.split(":", 1)
            parts = [p.strip() for p in info.split(",")]
            state = parts[0].lower()
            pct = int(parts[1].rstrip("%"))
            mins = None
            if len(parts) > 2 and ":" in parts[2]:
                h, m = map(int, parts[2].split(":")[:2])
                mins = h * 60 + m
            return pct, state, mins
        except Exception:
            logger.exception("Error parsing ACPI output: %s", out)
            return None

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

    @staticmethod
    def _fmt_time(mins: int) -> str:
        """Format minutes into human-readable time string."""
        if mins <= 0:
            return ""
        h, m = divmod(mins, 60)
        return f" ({h}h {m:02d}m)" if h else f" ({m}m)"

    @expose_command()
    def refresh(self) -> None:
        """Manual update trigger."""
        with self._update_lock:
            self._last_update = 0.0
        logger.debug("Manual refresh invoked")
        self.force_update()
