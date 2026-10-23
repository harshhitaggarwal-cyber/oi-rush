"""APScheduler entry point for the daily 18:00 Asia/Kolkata snapshot run."""
import logging
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from apscheduler.schedulers.blocking import BlockingScheduler
from .market_calendar import calendar_from_env
from .providers import HttpJsonProvider
from .snapshot_job import run_snapshot

IST = ZoneInfo("Asia/Kolkata")
LOG = logging.getLogger("oi_rush.scheduler")

def last_session_candidate(calendar, today: date) -> date | None:
    if not calendar.configured:
        return None
    day = today
    for _ in range(15):
        if calendar.is_session_candidate(day): return day
        day -= timedelta(days=1)
    return None

def run_daily():
    now = datetime.now(IST)
    provider = HttpJsonProvider.from_env()
    for market in ("NSE", "MCX"):
        calendar = calendar_from_env(market)
        session_date = last_session_candidate(calendar, now.date())
        if session_date is None:
            LOG.error("%s: official calendar missing or no recent session candidate; no snapshot made", market); continue
        if session_date != now.date():
            LOG.info("%s: today is not a session candidate; skipping snapshot run (latest candidate %s)", market, session_date); continue
        if not provider.status().configured:
            LOG.error("%s: authorized provider not configured; no snapshot made", market); continue
        try:
            instruments = provider.fetch_instruments(market)
            result = run_snapshot(market, session_date, calendar, provider, instruments)
            LOG.info("%s snapshot result: %s", market, result)
        except Exception:
            LOG.exception("%s snapshot run failed", market)

def main():
    logging.basicConfig(level=logging.INFO)
    scheduler = BlockingScheduler(timezone=IST)
    scheduler.add_job(run_daily, "cron", hour=18, minute=0, id="oi-rush-daily-snapshot", misfire_grace_time=3600, coalesce=True, max_instances=1)
    LOG.info("OI Rush scheduler started; daily target 18:00 Asia/Kolkata")
    scheduler.start()

if __name__ == "__main__": main()
