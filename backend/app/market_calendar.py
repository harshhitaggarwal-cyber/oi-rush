"""Exchange-session calendar helpers.

Do not assume a day is open when an official holiday calendar has not been loaded.
Keep the official NSE and MCX holiday lists as separate, reviewed configuration.
"""
from dataclasses import dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class ExchangeCalendar:
    exchange: str
    holidays: frozenset[date]
    configured: bool = False

    @classmethod
    def from_dates(cls, exchange: str, holiday_dates: Iterable[date]) -> "ExchangeCalendar":
        return cls(exchange=exchange.upper(), holidays=frozenset(holiday_dates), configured=True)

    def is_session_candidate(self, day: date) -> bool:
        """True only for weekdays not listed as holidays; not a substitute for special-session data."""
        if not self.configured:
            return False
        return day.weekday() < 5 and day not in self.holidays

    def status(self, day: date) -> str:
        if not self.configured:
            return "CALENDAR_UNCONFIGURED"
        if day.weekday() >= 5 or day in self.holidays:
            return "NON_TRADING_DAY"
        return "SESSION_CANDIDATE"
