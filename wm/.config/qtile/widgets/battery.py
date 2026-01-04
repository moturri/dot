# Copyright (c) 2025 Elton Moturi - MIT License

from __future__ import annotations

import select
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Iterator

import pyudev  # type: ignore[import-untyped]
from libqtile.log_utils import logger
from qtile_extras.widget import TextBox

# Battery icon thresholds: (percentage, icon, color)
BATTERY_ICONS: tuple[tuple[int, str, str], ...] = (
    (90, "󰁹", "mediumpurple"),
    (80, "󰂂", "limegreen"),
    (70, "󰂀", "palegreen"),
    (60, "󰁿", "tan"),
    (40, "󰁽", "moccasin"),
    (30, "󰁼", "goldenrod"),
    (20, "󰁻", "tomato"),
    (10, "󰁺", "indianred"),
    (0, "󰂎", "red"),
)

CHARGING_ICON: Final[str] = "󱐋 "
POWER_SUPPLY: Final[Path] = Path("/sys/class/power_supply")


class BatteryError(Exception):
    """Raised when battery operations fail."""


@dataclass(frozen=True, slots=True)
class BatteryIcon:
    threshold: int
    icon: str
    color: str


@dataclass(frozen=True, slots=True)
class BatteryState:
    status: str
    capacity: int | None

    def is_charging(self) -> bool:
        return self.status == "charging"

    def is_full(self) -> bool:
        return self.status == "full"

    def is_discharging(self) -> bool:
        return self.status == "discharging"


@dataclass(frozen=True, slots=True)
class BatteryData:
    capacity: str | None = None
    status: str | None = None
    energy_now: str | None = None
    charge_now: str | None = None
    energy_full: str | None = None
    charge_full: str | None = None


class BatteryWidget(TextBox):  # type: ignore[misc]
    """
    Qtile battery widget backed by sysfs and udev.

    Design notes:
    - Sysfs reads are treated as unreliable input and parsed defensively.
    - udev is used for change notification, not for primary data access.
    - All failures degrade gracefully; the bar must never crash.
    """

    CRITICAL_MIN: Final[int] = 1
    CRITICAL_MAX: Final[int] = 100
    DEBOUNCE_MIN: Final[float] = 0.1
    DEBOUNCE_MAX: Final[float] = 10.0
    AC_CACHE_EXPIRY: Final[float] = 2.0
    POLL_TIMEOUT: Final[int] = 100
    MONITOR_INTERVAL: Final[float] = 1.0
    THREAD_JOIN_TIMEOUT: Final[float] = 1.0

    def __init__(
        self,
        critical: int = 20,
        debounce_s: float = 1.0,
        battery_path: str | None = None,
        colors: dict[str, str] | None = None,
        show_percentage: bool = True,
        **config: Any,
    ) -> None:
        super().__init__("", **config)

        self.critical = max(self.CRITICAL_MIN, min(critical, self.CRITICAL_MAX))
        self.debounce_s = max(self.DEBOUNCE_MIN, min(debounce_s, self.DEBOUNCE_MAX))
        self.colors = colors or {}
        self.show_percentage = show_percentage

        self._stop_evt = threading.Event()
        self._lock = threading.Lock()
        self._last_update = 0.0
        self._state = BatteryState(status="unknown", capacity=None)
        self._monitor_thread: threading.Thread | None = None

        self._ac_online_cache: bool | None = None
        self._ac_last_checked = 0.0

        self.battery_levels = tuple(
            BatteryIcon(threshold=t, icon=i, color=c) for t, i, c in BATTERY_ICONS
        )

        try:
            self._context = pyudev.Context()
        except Exception as e:
            logger.exception("Failed to initialize udev context")
            raise BatteryError("Could not initialize udev") from e

        # Battery auto-detection intentionally uses sysfs naming (BAT*)
        # because udev classification is inconsistent across vendors.
        self.batteries = self._detect_batteries(battery_path)

        if not self.batteries:
            self.text = '<span foreground="grey">󰂃 N/A</span>'
            logger.warning("No batteries detected")
            return

        self.add_callbacks({"Button1": self.update_now})

    def _configure(self, qtile: Any, bar: Any) -> None:
        super()._configure(qtile, bar)
        self._stop_evt.clear()

        if not self._monitor_thread or not self._monitor_thread.is_alive():
            self._monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="BatteryWidget-Monitor",
            )
            self._monitor_thread.start()

        self.update_now()

    def finalize(self) -> None:
        self._stop_evt.set()

        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=self.THREAD_JOIN_TIMEOUT)
            if self._monitor_thread.is_alive():
                logger.warning("Battery monitor thread did not terminate cleanly")
            self._monitor_thread = None

        super().finalize()

    def _monitor_loop(self) -> None:
        try:
            monitor = pyudev.Monitor.from_netlink(self._context)
            monitor.filter_by(subsystem="power_supply")
            monitor.start()

            poller = select.poll()
            poller.register(monitor.fileno(), select.POLLIN)

            while not self._stop_evt.wait(self.MONITOR_INTERVAL):
                if poller.poll(self.POLL_TIMEOUT):
                    if monitor.poll(0):
                        self._debounced_redraw()

        except Exception:
            logger.exception("Battery monitor loop crashed")

    def _debounced_redraw(self) -> None:
        now = time.monotonic()
        if now - self._last_update >= self.debounce_s:
            self._redraw()
            self._last_update = now

    @contextmanager
    def _state_lock(self) -> Iterator[None]:
        if not self._lock.acquire(timeout=1.0):
            logger.warning("Failed to acquire battery state lock")
            yield
            return
        try:
            yield
        finally:
            self._lock.release()

    def update_now(self) -> None:
        self._last_update = 0.0
        self._redraw()

    def _redraw(self) -> None:
        try:
            if self._update_state():
                with self._state_lock():
                    self.text = self._format_display()
                self.bar.draw()
        except Exception:
            logger.exception("Error redrawing battery widget")

    def _update_state(self) -> bool:
        try:
            with self._state_lock():
                data = {p: self._read_battery(p) for p in self.batteries}
                capacity = self._calculate_percentage(data)
                status = self._determine_status(data)
                new_state = BatteryState(status=status, capacity=capacity)

                if new_state != self._state:
                    self._state = new_state
                    return True
                return False

        except Exception:
            logger.exception("Error updating battery state")
            return False

    def _format_display(self) -> str:
        capacity = self._state.capacity
        if capacity is None:
            return '<span foreground="grey">󰂃 N/A</span>'

        icon, color = self._get_icon_style(capacity, self._state.status)
        fg = self.colors.get(color, color)
        weight = ' weight="bold"' if capacity <= self.critical else ""

        text = f"{icon} {capacity}%" if self.show_percentage else icon
        return f'<span foreground="{fg}"{weight}>{text}</span>'

    def _get_icon_style(self, percentage: int, status: str) -> tuple[str, str]:
        for level in self.battery_levels:
            if percentage >= level.threshold:
                icon = (
                    f"{CHARGING_ICON}{level.icon}"
                    if status == "charging" and percentage < 100
                    else level.icon
                )
                return icon, level.color

        level = self.battery_levels[-1]
        return level.icon, level.color

    @staticmethod
    def _read_battery(path: Path) -> BatteryData:
        def read_file(name: str) -> str | None:
            try:
                p = path / name
                return p.read_text(errors="ignore").strip() if p.exists() else None
            except Exception:
                return None

        return BatteryData(
            capacity=read_file("capacity"),
            status=read_file("status"),
            energy_now=read_file("energy_now"),
            charge_now=read_file("charge_now"),
            energy_full=read_file("energy_full"),
            charge_full=read_file("charge_full"),
        )

    def _calculate_percentage(self, data: dict[Path, BatteryData]) -> int | None:
        values: list[float] = []

        for d in data.values():
            if d.capacity:
                try:
                    values.append(float(d.capacity))
                    continue
                except ValueError:
                    pass

            now = d.energy_now or d.charge_now
            full = d.energy_full or d.charge_full
            if not now or not full:
                continue

            try:
                n, f = float(now), float(full)
                if f > 0:
                    values.append((n / f) * 100.0)
            except ValueError:
                pass

        if not values:
            return None

        avg = sum(values) / len(values)
        return max(0, min(100, int(round(avg))))

    def _determine_status(self, data: dict[Path, BatteryData]) -> str:
        for d in data.values():
            if d.status:
                s = d.status.strip().lower()
                if s in ("charging", "discharging", "full"):
                    return s
        return "charging" if self._is_ac_online() else "discharging"

    def _is_ac_online(self) -> bool:
        now = time.monotonic()

        if (
            self._ac_online_cache is not None
            and now - self._ac_last_checked < self.AC_CACHE_EXPIRY
        ):
            return self._ac_online_cache

        try:
            online = any(
                dev.get("POWER_SUPPLY_TYPE") == "Mains"
                and dev.get("POWER_SUPPLY_ONLINE") == "1"
                for dev in self._context.list_devices(subsystem="power_supply")
            )
            self._ac_online_cache = online
            self._ac_last_checked = now
            return online
        except Exception:
            logger.exception("Failed to check AC adapter status")
            return self._ac_online_cache or False

    @staticmethod
    def _detect_batteries(manual: str | None) -> list[Path]:
        if manual:
            p = Path(manual)
            return [p] if p.is_dir() else []

        try:
            return [p for p in POWER_SUPPLY.glob("BAT*") if p.is_dir()]
        except Exception:
            logger.exception("Battery detection failed")
            return []

    def get_state(self) -> BatteryState:
        with self._state_lock():
            return self._state

    def get_capacity(self) -> int | None:
        return self._state.capacity

    def is_critical(self) -> bool:
        c = self._state.capacity
        return c is not None and c <= self.critical
