"""Fail-closed exchange calendar helpers.

Populate separate NSE and MCX holidays/special sessions from the official calendars.
No official calendar is bundled because it must be maintained and reviewed each year.
"""
from dataclasses import dataclass
from datetime import date
from typing import Iterable


@dataclass(frozen=True)
class ExchangeCalendar:
    exchange: str
    holidays: frozenset[date]
    configured: bool = False
    special_sessions: frozenset[date] = frozenset()

    @classmethod
    def from_dates(cls, exchange: str, holiday_dates: Iterable[date],
                   special_sessions: Iterable[date] = ()) -> "ExchangeCalendar":
        return cls(exchange=exchange.upper(), holidays=frozenset(holiday_dates),
                   configured=True, special_sessions=frozenset(special_sessions))

    def is_session_candidate(self, day: date) -> bool:
        if not self.configured:
            return False
        if day in self.holidays:
            return False
        return day in self.special_sessions or day.weekday() < 5

    def status(self, day: date) -> str:
        if not self.configured:
            return "CALENDAR_UNCONFIGURED"
        if day in self.holidays:
            return "NON_TRADING_DAY"
        if day.weekday() >= 5 and day not in self.special_sessions:
            return "NON_TRADING_DAY"
        return "SESSION_CANDIDATE"


def calendar_from_env(exchange: str) -> ExchangeCalendar:
    """Read comma-separated official dates; empty/missing holiday env means unconfigured."""
    import os
    prefix = exchange.upper()
    holidays_raw = os.getenv(f"OI_RUSH_{prefix}_HOLIDAYS", "").strip()
    sessions_raw = os.getenv(f"OI_RUSH_{prefix}_SPECIAL_SESSIONS", "").strip()
    if not holidays_raw:
        return ExchangeCalendar(exchange=prefix, holidays=frozenset(), configured=False)
    holidays = [date.fromisoformat(x.strip()) for x in holidays_raw.split(",") if x.strip()]
    sessions = [date.fromisoformat(x.strip()) for x in sessions_raw.split(",") if x.strip()]
    return ExchangeCalendar.from_dates(prefix, holidays, sessions)
