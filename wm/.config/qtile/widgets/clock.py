"""
Robust Clock Widget for Qtile
Minimalist, professional clock widget with proper lifecycle and type safety.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any, Optional

from libqtile.widget import base


class Clock(base.InLoopPollText):
    """
    Minimalist clock widget for Qtile.

    Features:
    - Displays date and time in a single line
    - Updates every second
    - Supports configurable timezone
    - Safe lifecycle management
    """

    defaults: list[tuple[str, Any, str]] = [
        ("format", "%Y-%m-%d %H:%M:%S", "strftime format string"),
        ("update_interval", 1.0, "Update interval in seconds"),
        (
            "timezone",
            None,
            "Timezone string (e.g., 'America/New_York') or None for local",
        ),
    ]

    def __init__(self, **config: Any) -> None:
        super().__init__(**config)  # type: ignore[no-untyped-call]
        self.add_defaults(Clock.defaults)  # type: ignore[no-untyped-call]

        self.format: str
        self.update_interval: float
        self.timezone: Optional[str | tzinfo]

        self._tz: Optional[tzinfo] = None
        self._parse_timezone()

    def _parse_timezone(self) -> None:
        """Parse the configured timezone string into a tzinfo object."""
        if self.timezone is None:
            self._tz = None
            return

        if isinstance(self.timezone, str):
            try:
                from zoneinfo import ZoneInfo  # Python 3.9+

                self._tz = ZoneInfo(self.timezone)
            except ImportError:
                try:
                    from dateutil.tz import gettz

                    self._tz = gettz(self.timezone)
                except ImportError:
                    self._tz = None
        elif isinstance(self.timezone, tzinfo):
            self._tz = self.timezone
        else:
            self._tz = None

    def poll(self) -> str:  # type: ignore[override]
        """Return the current date and time string."""
        now = datetime.now(timezone.utc)
        now = now.astimezone(self._tz) if self._tz else now.astimezone()
        now += timedelta(seconds=0.5)  # small offset to avoid rounding issues
        return now.strftime(self.format)
