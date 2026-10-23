from datetime import date
from app.market_calendar import ExchangeCalendar
from app.providers import UnconfiguredProvider
from app.snapshot_job import run_snapshot


def test_unconfigured_calendar_fails_closed():
    cal = ExchangeCalendar(exchange="NSE", holidays=frozenset(), configured=False)
    assert cal.status(date(2026, 10, 26)) == "CALENDAR_UNCONFIGURED"


def test_weekend_skipped_when_calendar_configured():
    cal = ExchangeCalendar.from_dates("MCX", [])
    assert cal.status(date(2026, 10, 24)) == "NON_TRADING_DAY"


def test_provider_missing_never_generates_snapshot():
    cal = ExchangeCalendar.from_dates("NSE", [])
    result = run_snapshot("NSE", date(2026, 10, 26), cal, UnconfiguredProvider(), [])
    assert result["status"] == "UNAVAILABLE"
    assert result["reason"] == "provider_unconfigured"
