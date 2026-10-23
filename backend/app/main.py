from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import FastAPI
from .oi_engine import StrikeData, classify_pair, make_row

app = FastAPI(title="OI Rush API", version="0.1.0")
IST = ZoneInfo("Asia/Kolkata")

@app.get("/health")
def health():
    return {"status": "ok", "service": "oi-rush-api", "time_ist": datetime.now(IST).isoformat(), "data_mode": "demo"}

@app.get("/v1/markets")
def markets():
    return {"markets": [{"id": "NSE", "groups": ["Indices", "Stocks"]}, {"id": "MCX", "groups": ["All active commodity options"]}], "data_mode": "demo"}

@app.get("/v1/instruments/{market}")
def instruments(market: str):
    m = market.upper()
    if m == "NSE": return {"market": m, "groups": ["Indices", "Stocks"], "instruments": [], "status": "provider_not_configured"}
    if m == "MCX": return {"market": m, "groups": ["All active commodity options"], "instruments": [], "status": "official_contract_master_required"}
    return {"market": m, "instruments": [], "status": "unsupported_market"}

@app.get("/v1/option-chain/{symbol}")
def option_chain(symbol: str, market: str = "NSE", expiry: str = "DEMO"):
    p = StrikeData(25450, 12000, 18000, 1100, 1600, 100, 120)
    c = StrikeData(25500, 15000, 22000, 900, 1400, 130, 105)
    return {"market": market.upper(), "underlying": symbol.upper(), "underlying_price": None, "expiry": expiry, "snapshot_status": "DEMO_DATA", "snapshot_session_date": None, "columns": ["Strike", "OI PCR", "LTP PCR", "OI Analysis"], "rows": [make_row(p, "Neutral / No Setup"), make_row(c, classify_pair(p, c))], "warning": "Fictional demo data only; no live exchange feed is connected."}

@app.get("/v1/snapshot-status")
def snapshot_status():
    return {"timezone": "Asia/Kolkata", "target_snapshot_time": "18:00", "current_time_ist": datetime.now(IST).isoformat(), "scheduler_configured": False, "holiday_calendar_configured": False, "data_provider_configured": False, "latest_status": "DEMO_ONLY"}
