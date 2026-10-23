"""Fail-closed exchange calendar helpers for the scheduled 18:00 IST snapshot."""
from dataclasses import dataclass
from datetime import date
from typing import Iterable

@dataclass(frozen=True)
class ExchangeCalendar:
    exchange: str
    holidays: frozenset[date]
    configured: bool = False
    special_sessions: frozenset[date] = frozenset()
    calendar_year: int | None = None

    @classmethod
    def from_dates(cls, exchange: str, holiday_dates: Iterable[date], special_sessions: Iterable[date] = (), calendar_year: int | None = None) -> "ExchangeCalendar":
        return cls(exchange=exchange.upper(), holidays=frozenset(holiday_dates), configured=True,
                   special_sessions=frozenset(special_sessions), calendar_year=calendar_year)

    def status(self, day: date) -> str:
        if not self.configured: return "CALENDAR_UNCONFIGURED"
        if self.calendar_year is not None and day.year != self.calendar_year: return "CALENDAR_OUT_OF_RANGE"
        # Explicit special sessions override the regular holiday/weekend rule.
        if day in self.special_sessions: return "SESSION_CANDIDATE"
        if day in self.holidays or day.weekday() >= 5: return "NON_TRADING_DAY"
        return "SESSION_CANDIDATE"

    def is_session_candidate(self, day: date) -> bool:
        return self.status(day) == "SESSION_CANDIDATE"


def calendar_from_env(exchange: str) -> ExchangeCalendar:
    """Read the snapshot-time calendar; year coverage is mandatory to fail closed next year."""
    import os
    prefix = exchange.upper()
    holidays_raw = os.getenv(f"OI_RUSH_{prefix}_HOLIDAYS", "").strip()
    sessions_raw = os.getenv(f"OI_RUSH_{prefix}_SPECIAL_SESSIONS", "").strip()
    year_raw = os.getenv(f"OI_RUSH_{prefix}_CALENDAR_YEAR", "").strip()
    if not holidays_raw or not year_raw:
        return ExchangeCalendar(exchange=prefix, holidays=frozenset(), configured=False)
    year = int(year_raw)
    holidays = [date.fromisoformat(x.strip()) for x in holidays_raw.split(",") if x.strip()]
    sessions = [date.fromisoformat(x.strip()) for x in sessions_raw.split(",") if x.strip()]
    if any(d.year != year for d in holidays + sessions):
        raise ValueError(f"All {prefix} calendar dates must belong to configured year {year}.")
    return ExchangeCalendar.from_dates(prefix, holidays, sessions, calendar_year=year)
