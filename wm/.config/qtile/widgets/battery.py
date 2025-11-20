# Copyright (c) 2025 Elton Moturi 
# MIT License

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
        self.debounce_ns: int = int(max(debounce_s, 0.1) * 1_000_000_000)
        self.colors: Dict[str, str] = colors or {}

        self._stop_evt = threading.Event()
        self._last_update_ns: int = 0
        self._state = BatteryState("unknown", None)

        self._context = pyudev.Context()

        self.batteries: List[Path] = self._detect(battery_path)
        if not self.batteries:
            self.text = '<span foreground="grey">󰂃 N/A</span>'
            return

        self.add_callbacks({"Button1": self.update_now})

    # ------------------------------------------------------------
    # Qtile lifecycle
    # ------------------------------------------------------------

    def _configure(self, qtile: Any, bar: Any) -> None:
        super()._configure(qtile, bar)
        self._stop_evt.clear()
        threading.Thread(target=self._monitor, daemon=True).start()
        self.update_now()

    def finalize(self) -> None:
        self._stop_evt.set()
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
            if poller.poll(100):  # 100ms
                if monitor.poll(0):
                    now = time.monotonic_ns()
                    if now - self._last_update_ns >= self.debounce_ns:
                        self._last_update_ns = now
                        self._redraw()

    # ------------------------------------------------------------
    # Core
    # ------------------------------------------------------------

    def update_now(self) -> None:
        self._last_update_ns = 0
        self._redraw()

    def _redraw(self) -> None:
        if self._update_state():
            self.text = self._format()
            self.bar.draw()

    def _update_state(self) -> bool:
        data: Dict[Path, Dict[str, Optional[str]]] = {
            p: self._read(p) for p in self.batteries
        }

        pct = self._percentage(data)
        status = self._status(data)

        new = BatteryState(status, pct)

        if new == self._state:
            return False

        self._state = new
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

    def _percentage(
        self,
        data: Dict[Path, Dict[str, Optional[str]]],
    ) -> Optional[int]:
        values: List[float] = []

        for d in data.values():
            cap = d["capacity"]
            if cap is not None:
                try:
                    values.append(float(cap))
                    continue
                except ValueError:
                    pass

            now = d["energy_now"] or d["charge_now"]
            full = d["energy_full"] or d["charge_full"]

            if now is None or full is None:
                continue

            try:
                n = float(now)
                f = float(full)
                if f > 0:
                    values.append((n / f) * 100.0)
            except ValueError:
                continue

        if not values:
            return None

        return int(round(sum(values) / len(values)))

    def _status(self, data: Dict[Path, Dict[str, Optional[str]]]) -> str:
        for d in data.values():
            s = d["status"]
            if s:
                sl = s.lower()
                if sl in ("charging", "discharging", "full"):
                    return sl

        return "charging" if self._ac_online() else "discharging"

    def _ac_online(self) -> bool:
        try:
            for dev in self._context.list_devices(subsystem="power_supply"):
                if dev.get("POWER_SUPPLY_TYPE") == "Mains":
                    online_status = dev.get("POWER_SUPPLY_ONLINE")
                    if online_status is not None:
                        return str(online_status) == "1"
                    return False
        except Exception as e:
            logger.debug(f"BatteryWidget: AC check failed: {e}")
        return False

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

    def get_state(self) -> Tuple[Optional[int], str]:
        data = {p: self._read(p) for p in self.batteries}
        return self._percentage(data), self._status(data)
