from datetime import date
from app.market_calendar import ExchangeCalendar
from app.providers import UnconfiguredProvider
from app.snapshot_job import run_snapshot

def test_unconfigured_calendar_fails_closed():
    cal=ExchangeCalendar(exchange="NSE",holidays=frozenset(),configured=False)
    assert cal.status(date(2026,10,26)) == "CALENDAR_UNCONFIGURED"

def test_weekend_skipped_when_calendar_configured():
    cal=ExchangeCalendar.from_dates("MCX",[])
    assert cal.status(date(2026,10,24)) == "NON_TRADING_DAY"

def test_calendar_fails_closed_outside_configured_year():
    cal=ExchangeCalendar.from_dates("NSE",[date(2026,1,26)],calendar_year=2026)
    assert cal.status(date(2027,1,4)) == "CALENDAR_OUT_OF_RANGE"

def test_special_session_can_override_weekend():
    cal=ExchangeCalendar.from_dates("MCX",[],special_sessions=[date(2026,11,8)],calendar_year=2026)
    assert cal.status(date(2026,11,8)) == "SESSION_CANDIDATE"

def test_provider_missing_never_generates_snapshot(tmp_path):
    cal=ExchangeCalendar.from_dates("NSE",[])
    result=run_snapshot("NSE",date(2026,10,26),cal,UnconfiguredProvider(),[],tmp_path/"test.sqlite3")
    assert result["status"] == "UNAVAILABLE"
    assert result["reason"] == "provider_unconfigured"


def test_snapshot_refuses_out_of_range_calendar(tmp_path):
    cal=ExchangeCalendar.from_dates("NSE",[date(2026,1,26)],calendar_year=2026)
    result=run_snapshot("NSE",date(2027,1,4),cal,UnconfiguredProvider(),[],tmp_path/"test.sqlite3")
    assert result["status"] == "UNAVAILABLE"
    assert result["reason"] == "calendar_out_of_range"
