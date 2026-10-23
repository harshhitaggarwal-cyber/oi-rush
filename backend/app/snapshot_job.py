"""Guarded snapshot orchestration skeleton; provider and official calendars are required."""
from datetime import date, datetime
from zoneinfo import ZoneInfo

from .market_calendar import ExchangeCalendar
from .providers import MarketDataProvider

IST = ZoneInfo("Asia/Kolkata")


def run_snapshot(exchange: str, session_date: date, calendar: ExchangeCalendar,
                 provider: MarketDataProvider, instruments: list[dict]) -> dict:
    """Prepare a snapshot only when calendar and authorized provider are configured.

    Persistence and a scheduler deployment are intentionally separate concerns.
    """
    if calendar.exchange != exchange.upper():
        return {"status": "ERROR", "reason": "calendar_exchange_mismatch"}
    calendar_status = calendar.status(session_date)
    if calendar_status == "CALENDAR_UNCONFIGURED":
        return {"status": "UNAVAILABLE", "reason": "calendar_unconfigured", "session_date": str(session_date)}
    if calendar_status == "NON_TRADING_DAY":
        return {"status": "SKIPPED", "reason": "non_trading_day", "session_date": str(session_date)}
    provider_status = provider.status()
    if not provider_status.configured:
        return {"status": "UNAVAILABLE", "reason": "provider_unconfigured", "session_date": str(session_date)}
    # Do not return success until a real provider fetch and durable persistence are implemented.
    return {"status": "NOT_IMPLEMENTED", "reason": "provider_fetch_and_persistence_required",
            "session_date": str(session_date), "created_at_ist": datetime.now(IST).isoformat(),
            "instrument_count": len(instruments)}
