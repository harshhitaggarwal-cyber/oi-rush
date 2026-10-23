"""NSE-only daily snapshot scheduler in Asia/Kolkata time.

Starts at 19:30 IST and retries an authorized provider every 10 minutes until 20:30.
Provider source timestamps remain authoritative; no NSE webpage scraping is performed.
"""
import logging
import time
from datetime import datetime, time as clock_time
from zoneinfo import ZoneInfo

from apscheduler.schedulers.blocking import BlockingScheduler
from .market_calendar import calendar_from_env
from .providers import HttpJsonProvider
from .snapshot_job import run_snapshot

IST = ZoneInfo("Asia/Kolkata")
LOG = logging.getLogger("oi_rush.scheduler")
TARGETS = {"NSE": (19, 30)}
RETRY_SECONDS = 10 * 60
CUTOFF = clock_time(20, 30)


def run_market_snapshot(market: str):
    market = market.upper()
    if market != "NSE":
        LOG.error("%s: market is disabled; only NSE snapshots are enabled", market)
        return

    provider = HttpJsonProvider.from_env()
    if not provider.status().configured:
        LOG.error("%s: authorized provider not configured; no snapshot made", market)
        return

    while True:
        now = datetime.now(IST)
        calendar = calendar_from_env(market)
        if not calendar.configured:
            LOG.error("%s: exchange calendar missing; no snapshot made", market)
            return
        calendar_status = calendar.status(now.date())
        if calendar_status != "SESSION_CANDIDATE":
            LOG.info("%s: no snapshot for %s; calendar status=%s", market, now.date(), calendar_status)
            return

        try:
            instruments = provider.fetch_instruments(market)
            result = run_snapshot(market, now.date(), calendar, provider, instruments)
            LOG.info("%s snapshot attempt at %s: %s", market, now.isoformat(), result)
            if result.get("status") == "AVAILABLE":
                LOG.info("%s snapshot complete; no further retries needed", market)
                return
        except Exception:
            LOG.exception("%s snapshot attempt failed", market)

        now = datetime.now(IST)
        if now.time().replace(tzinfo=None) >= CUTOFF:
            LOG.warning("%s: retry cutoff 20:30 IST reached; no valid complete snapshot confirmed", market)
            return
        LOG.info("%s: retrying in 10 minutes if data is still unavailable", market)
        time.sleep(RETRY_SECONDS)


def main():
    logging.basicConfig(level=logging.INFO)
    scheduler = BlockingScheduler(timezone=IST)
    for market, (hour, minute) in TARGETS.items():
        scheduler.add_job(
            run_market_snapshot, "cron", args=[market], hour=hour, minute=minute,
            id=f"oi-rush-{market.lower()}-daily-snapshot",
            misfire_grace_time=3600, coalesce=True, max_instances=1,
        )
    LOG.info("OI Rush NSE-only scheduler started; target 19:30 IST, retries every 10 minutes until 20:30 IST")
    scheduler.start()


if __name__ == "__main__":
    main()
