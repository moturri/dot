import os
import subprocess
from typing import Any, Optional, Tuple

from qtile_extras.widget import GenPollText

CHARGING_ICON = "󱐋"
FULL_ICON = "󰂄"
EMPTY_ICON = "󰁺"
FALLBACK_ICON = "󰂑"

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


class AcpiWidget(GenPollText):  # type: ignore
    """Minimal battery widget using the `acpi` command."""

    _env: dict[str, str]

    def __init__(
        self,
        update_interval: float = 15.0,
        show_time: bool = False,
        critical_threshold: int = 10,
        **config: Any,
    ) -> None:
        self.show_time = show_time
        self.critical_threshold = max(5, min(25, critical_threshold))
        self._env = {"LC_ALL": "C.UTF-8", **os.environ}
        super().__init__(func=self._poll, update_interval=update_interval, **config)

    def _poll(self) -> str:
        data = self._get_acpi_data()
        if not data:
            return f"{FALLBACK_ICON} N/A"

        pct, state, minutes = data
        icon, color = self._get_icon_color(pct, state)
        time_str = self._format_time(minutes) if self.show_time and minutes else ""
        return f'<span foreground="{color}">{icon} {pct}%{time_str}</span>'

    def _get_acpi_data(self) -> Optional[Tuple[int, str, Optional[int]]]:
        try:
            output = subprocess.check_output(
                ["acpi", "-b"], env=self._env, timeout=1.5
            ).decode()
            parts = output.split(":")[1].split(",")
            state = parts[0].strip().lower()
            pct = int(parts[1].strip().rstrip("%"))

            minutes: Optional[int] = None
            if len(parts) > 2 and ":" in parts[2]:
                h, m = map(int, parts[2].strip().split(":")[:2])
                minutes = h * 60 + m

            return pct, state, minutes
        except Exception:
            return None

    def _get_icon_color(self, pct: int, state: str) -> Tuple[str, str]:
        if state == "full":
            return FULL_ICON, "lime"
        if pct <= self.critical_threshold:
            return EMPTY_ICON, "red" if pct <= 5 else "orange"

        for threshold, icon, color in BATTERY_ICONS:
            if pct >= threshold:
                icon = f"{CHARGING_ICON} {icon}" if state == "charging" else icon
                return icon, color

        return FALLBACK_ICON, "#666666"

    def _format_time(self, minutes: int) -> str:
        h, m = divmod(minutes, 60)
        return f" ({h}h {m:02d}m)" if h else f" ({m}m)"
