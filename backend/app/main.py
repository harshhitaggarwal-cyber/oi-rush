from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException, Query
from .market_calendar import calendar_from_env
from .providers import HttpJsonProvider
from .snapshot_job import latest_snapshot

app = FastAPI(title="OI Rush API", version="0.2.2")
IST = ZoneInfo("Asia/Kolkata")

def get_provider():
    return HttpJsonProvider.from_env()

@app.get("/health")
def health():
    provider = get_provider()
    return {
        "status": "ok",
        "service": "oi-rush-api",
        "time_ist": datetime.now(IST).isoformat(),
        "data_mode": "provider_configured" if provider.status().configured else "unavailable",
        "provider": provider.status().provider_name,
    }

@app.get("/v1/markets")
def markets():
    provider = get_provider()
    return {
        "markets": [{"id": "NSE", "label": "NSE", "groups": ["Indices", "Stocks"]}],
        "data_mode": "provider_configured" if provider.status().configured else "unavailable",
    }

@app.get("/v1/instruments/{market}")
def instruments(market: str):
    m = market.upper()
    if m != "NSE":
        raise HTTPException(status_code=400, detail="Only NSE is currently supported")
    provider = get_provider()
    if not provider.status().configured:
        raise HTTPException(status_code=503, detail="Authorized NSE market-data provider is not configured.")
    try:
        return {"market": m, "instruments": provider.fetch_instruments(m), "status": "AVAILABLE"}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Provider instruments request failed: {str(exc)[:200]}")

@app.get("/v1/option-chain/{symbol}")
def option_chain(symbol: str, market: str = Query(default="NSE"), expiry: str = Query(...)):
    m = market.upper()
    if m != "NSE":
        raise HTTPException(status_code=400, detail="Only NSE is currently supported")
    saved = latest_snapshot(m, symbol, expiry)
    if saved:
        return saved
    raise HTTPException(status_code=404, detail="No persisted NSE snapshot exists for this underlying and expiry. Do not treat a live or stale response as the 18:00 snapshot.")

@app.get("/v1/snapshot-status")
def snapshot_status():
    provider = get_provider()
    calendar = calendar_from_env("NSE")
    return {
        "timezone": "Asia/Kolkata",
        "target_snapshot_times": {"NSE": "18:00"},
        "current_time_ist": datetime.now(IST).isoformat(),
        "scheduler_process_required": True,
        "holiday_calendars": {
            "NSE": {
                "configured": calendar.configured,
                "holiday_count": len(calendar.holidays),
                "special_session_count": len(calendar.special_sessions),
            }
        },
        "data_provider_configured": provider.status().configured,
        "provider_name": provider.status().provider_name,
        "latest_status": "READY_TO_FETCH" if provider.status().configured and calendar.configured else "CONFIGURATION_REQUIRED",
    }
