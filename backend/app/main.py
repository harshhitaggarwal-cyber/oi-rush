from datetime import datetime, date
import hmac
import os
from zoneinfo import ZoneInfo
from fastapi import FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field
from .market_calendar import calendar_from_env
from .providers import HttpJsonProvider
from .snapshot_job import latest_snapshot, persist_snapshot
from .nse_csv_import import parse_nse_option_chain_csv
from .providers import validate_chain_payload
from .csv_upload import router as csv_upload_router

app = FastAPI(title="OI Rush API", version="0.2.3")
app.include_router(csv_upload_router)
IST = ZoneInfo("Asia/Kolkata")

def get_provider():
    return HttpJsonProvider.from_env()


class NSECsvImportRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=40)
    expiry: str = Field(min_length=8, max_length=20)
    session_date: date
    # Must be the actual timestamp displayed with the downloaded NSE snapshot,
    # including an offset (for example +05:30), not the time of upload.
    source_timestamp: str = Field(min_length=10, max_length=50)
    underlying_price: float = Field(gt=0)
    csv_text: str = Field(min_length=1, max_length=5_000_000)


@app.post("/v1/admin/import/nse-csv")
def import_nse_csv(
    body: NSECsvImportRequest,
    x_import_token: str | None = Header(default=None, alias="X-Import-Token"),
):
    """Import an operator-provided NSE CSV; this endpoint does not scrape NSE."""
    expected = os.getenv("OI_RUSH_CSV_IMPORT_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="CSV import is disabled until OI_RUSH_CSV_IMPORT_TOKEN is configured.")
    if not x_import_token or not hmac.compare_digest(x_import_token, expected):
        raise HTTPException(status_code=401, detail="Invalid import token.")
    symbol = body.symbol.strip().upper()
    expiry = body.expiry.strip()
    try:
        rows = parse_nse_option_chain_csv(body.csv_text)
        chain = {
            "market": "NSE",
            "underlying": symbol,
            "expiry": expiry,
            "session_date": body.session_date.isoformat(),
            "source_timestamp": body.source_timestamp,
            "underlying_price": body.underlying_price,
            "rows": rows,
        }
        validate_chain_payload(chain, "NSE", symbol, expiry)
        payload = persist_snapshot(chain)
        return {
            "status": "AVAILABLE",
            "market": "NSE",
            "underlying": symbol,
            "expiry": expiry,
            "session_date": payload["session_date"],
            "source_timestamp": payload["source_timestamp"],
            "row_count": len(payload["rows"]),
            "message": "CSV snapshot imported and saved.",
        }
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=f"CSV import failed: {str(exc)[:250]}") from exc

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
    raise HTTPException(status_code=404, detail="No persisted NSE snapshot exists for this underlying and expiry. Do not treat a live or stale response as the 19:30 snapshot.")

@app.get("/v1/snapshot-status")
def snapshot_status():
    provider = get_provider()
    calendar = calendar_from_env("NSE")
    return {
        "timezone": "Asia/Kolkata",
        "target_snapshot_times": {"NSE": "19:30"},
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
