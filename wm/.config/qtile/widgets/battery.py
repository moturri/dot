# Copyright (c) 2025 Elton Moturi - MIT License

from __future__ import annotations

import select
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pyudev  # type: ignore[import-untyped]
from libqtile.log_utils import logger
from qtile_extras.widget import TextBox

BATTERY_ICONS: Tuple[Tuple[int, str, str], ...] = (
    (90, "󰁹", "orchid"),
    (80, "󰂂", "limegreen"),
    (70, "󰂀", "palegreen"),
    (60, "󰁿", "tan"),
    (40, "󰁽", "moccasin"),
    (30, "󰁼", "goldenrod"),
    (20, "󰁻", "tomato"),
    (10, "󰁺", "indianred"),
)

CHARGING_ICON = "󱐋 "
POWER_SUPPLY = Path("/sys/class/power_supply")


@dataclass(frozen=True, slots=True)
class BatteryState:
    status: str
    capacity: Optional[int]


class BatteryWidget(TextBox):  # type: ignore[misc]
    """Qtile widget that monitors battery status via sysfs."""

    _monitor_thread: Optional[threading.Thread] = None
    _ac_cache_expiry: float = 2.0  # seconds

    def __init__(
        self,
        critical: int = 20,
        debounce_s: float = 1.0,
        battery_path: Optional[str] = None,
        colors: Optional[Dict[str, str]] = None,
        **config: Any,
    ) -> None:
        super().__init__("", **config)

        self.critical: int = max(1, min(critical, 100))
        self.debounce_s: float = max(debounce_s, 0.1)
        self.colors: Dict[str, str] = colors or {}

        self._stop_evt = threading.Event()
        self._last_update: float = 0.0
        self._state: BatteryState = BatteryState("unknown", None)

        self._context = pyudev.Context()
        self.batteries: List[Path] = self._detect(battery_path)

        if not self.batteries:
            self.text = '<span foreground="grey">󰂃 N/A</span>'
            return

        self.add_callbacks({"Button1": self.update_now})

        # AC cache
        self._ac_online_cache: Optional[bool] = None
        self._ac_last_checked: float = 0.0

    # ------------------------------------------------------------
    # Qtile lifecycle
    # ------------------------------------------------------------
    def _configure(self, qtile: Any, bar: Any) -> None:
        super()._configure(qtile, bar)
        self._stop_evt.clear()
        if not self._monitor_thread or not self._monitor_thread.is_alive():
            self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
            self._monitor_thread.start()
        self.update_now()

    def finalize(self) -> None:
        self._stop_evt.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=1.0)
        super().finalize()

    # ------------------------------------------------------------
    # Event loop
    # ------------------------------------------------------------
    def _monitor(self) -> None:
        monitor = pyudev.Monitor.from_netlink(self._context)
        monitor.filter_by(subsystem="power_supply")
        monitor.start()

        poller = select.poll()
        poller.register(monitor.fileno(), select.POLLIN)

        while not self._stop_evt.wait(1.0):
            if poller.poll(100):
                if monitor.poll(0):
                    now = time.monotonic()
                    if now - self._last_update >= self.debounce_s:
                        self._last_update = now
                        self._redraw()

    # ------------------------------------------------------------
    # Core
    # ------------------------------------------------------------
    def update_now(self) -> None:
        self._last_update = 0.0
        self._redraw()

    def _redraw(self) -> None:
        if self._update_state():
            self.text = self._format()
            self.bar.draw()

    def _update_state(self) -> bool:
        data = {p: self._read(p) for p in self.batteries}
        pct = self._percentage(data)
        status = self._status(data)
        new_state = BatteryState(status, pct)

        if new_state == self._state:
            return False

        self._state = new_state
        return True

    # ------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------
    def _format(self) -> str:
        pct = self._state.capacity
        if pct is None:
            return '<span foreground="grey">󰂃 N/A</span>'

        icon, color = self._icon(pct, self._state.status)
        fg = self.colors.get(color, color)
        weight = ' weight="bold"' if pct <= self.critical else ""
        return f'<span foreground="{fg}"{weight}>{icon} {pct}%</span>'

    # ------------------------------------------------------------
    # Sysfs IO
    # ------------------------------------------------------------
    @staticmethod
    def _read(path: Path) -> Dict[str, Optional[str]]:
        keys = (
            "capacity",
            "status",
            "energy_now",
            "charge_now",
            "energy_full",
            "charge_full",
        )
        out: Dict[str, Optional[str]] = {}
        for key in keys:
            file = path / key
            try:
                out[key] = file.read_text(encoding="utf-8", errors="ignore").strip()
            except Exception:
                out[key] = None
        return out

    def _percentage(self, data: Dict[Path, Dict[str, Optional[str]]]) -> Optional[int]:
        values: List[float] = []

        for d in data.values():
            cap = d.get("capacity")
            if cap is not None:
                try:
                    values.append(float(cap))
                    continue
                except ValueError:
                    logger.debug("Invalid capacity value: %s", cap)

            now_str = d.get("energy_now") or d.get("charge_now")
            full_str = d.get("energy_full") or d.get("charge_full")
            if now_str is None or full_str is None:
                continue

            try:
                now = float(now_str)
                full = float(full_str)
                if full > 0:
                    values.append((now / full) * 100.0)
            except ValueError:
                logger.debug(
                    "Invalid energy/charge values: now=%s, full=%s", now_str, full_str
                )

        if not values:
            return None
        return int(round(sum(values) / len(values)))

    def _status(self, data: Dict[Path, Dict[str, Optional[str]]]) -> str:
        for d in data.values():
            s = d.get("status")
            if s:
                sl = s.lower()
                if sl in ("charging", "discharging", "full"):
                    return sl
        return "charging" if self._ac_online() else "discharging"

    def _ac_online(self) -> bool:
        now = time.monotonic()
        if (
            self._ac_online_cache is not None
            and now - self._ac_last_checked < self._ac_cache_expiry
        ):
            return self._ac_online_cache

        online = False
        try:
            for dev in self._context.list_devices(subsystem="power_supply"):
                if dev.get("POWER_SUPPLY_TYPE") == "Mains":
                    status = dev.get("POWER_SUPPLY_ONLINE")
                    if status is not None:
                        online = str(status) == "1"
                        break
        except Exception as exc:
            logger.debug("BatteryWidget: AC check failed: %s", exc)

        self._ac_online_cache = online
        self._ac_last_checked = now
        return online

    def _icon(self, pct: int, status: str) -> Tuple[str, str]:
        for thresh, icon, color in BATTERY_ICONS:
            if pct >= thresh:
                if status == "charging" and pct < 100:
                    return f"{CHARGING_ICON}{icon}", color
                return icon, color
        return "󰂎", "red"

    # ------------------------------------------------------------
    # Detection + public API
    # ------------------------------------------------------------
    @staticmethod
    def _detect(manual: Optional[str]) -> List[Path]:
        if manual:
            p = Path(manual)
            return [p] if p.is_dir() else []
        return [p for p in POWER_SUPPLY.glob("BAT*") if p.is_dir()]

    def get_state(self) -> BatteryState:
        """Return cached state instead of re-reading sysfs."""
        return self._state
