"""Market-specific daily snapshot scheduler in Asia/Kolkata time.

NSE target: 18:00 IST.
MCX target: 23:59 IST (after the normal evening session close).
The provider's actual source timestamp remains authoritative; capture time is not
misrepresented as the exchange's quote timestamp.
"""
import logging
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo
from apscheduler.schedulers.blocking import BlockingScheduler
from .market_calendar import calendar_from_env
from .providers import HttpJsonProvider
from .snapshot_job import run_snapshot

IST = ZoneInfo("Asia/Kolkata")
LOG = logging.getLogger("oi_rush.scheduler")
TARGETS = {"NSE": (18, 0), "MCX": (23, 59)}

def run_market_snapshot(market: str):
    now = datetime.now(IST)
    market = market.upper()
    calendar = calendar_from_env(market)
    if not calendar.configured:
        LOG.error("%s: exchange calendar missing; no snapshot made", market)
        return
    calendar_status = calendar.status(now.date())
    if calendar_status != "SESSION_CANDIDATE":
        LOG.info("%s: no snapshot for %s; calendar status=%s", market, now.date(), calendar_status)
        return
    provider = HttpJsonProvider.from_env()
    if not provider.status().configured:
        LOG.error("%s: authorized provider not configured; no snapshot made", market)
        return
    try:
        instruments = provider.fetch_instruments(market)
        result = run_snapshot(market, now.date(), calendar, provider, instruments)
        LOG.info("%s snapshot result: %s", market, result)
    except Exception:
        LOG.exception("%s snapshot run failed", market)

def main():
    logging.basicConfig(level=logging.INFO)
    scheduler = BlockingScheduler(timezone=IST)
    for market, (hour, minute) in TARGETS.items():
        scheduler.add_job(
            run_market_snapshot, "cron", args=[market], hour=hour, minute=minute,
            id=f"oi-rush-{market.lower()}-daily-snapshot",
            misfire_grace_time=3600, coalesce=True, max_instances=1,
        )
    LOG.info("OI Rush scheduler started; NSE 18:00 IST, MCX 23:59 IST")
    scheduler.start()

if __name__ == "__main__":
    main()
