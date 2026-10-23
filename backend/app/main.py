from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import FastAPI, HTTPException, Query
from .market_calendar import calendar_from_env
from .providers import HttpJsonProvider
from .snapshot_job import latest_snapshot, persist_snapshot

app = FastAPI(title="OI Rush API", version="0.2.0")
IST = ZoneInfo("Asia/Kolkata")
def get_provider(): return HttpJsonProvider.from_env()

@app.get("/health")
def health():
    provider=get_provider()
    return {"status":"ok","service":"oi-rush-api","time_ist":datetime.now(IST).isoformat(),"data_mode":"provider_configured" if provider.status().configured else "unavailable","provider":provider.status().provider_name}

@app.get("/v1/markets")
def markets():
    provider=get_provider()
    return {"markets":[{"id":"NSE","label":"NSE","groups":["Indices","Stocks"]},{"id":"MCX","label":"MCX","groups":["All active commodity options"]}],"data_mode":"provider_configured" if provider.status().configured else "unavailable"}

@app.get("/v1/instruments/{market}")
def instruments(market: str):
    m=market.upper()
    if m not in ("NSE","MCX"): raise HTTPException(status_code=400,detail="market must be NSE or MCX")
    provider=get_provider()
    if not provider.status().configured: raise HTTPException(status_code=503,detail="Authorized market-data provider is not configured.")
    try: return {"market":m,"instruments":provider.fetch_instruments(m),"status":"AVAILABLE"}
    except Exception as exc: raise HTTPException(status_code=502,detail=f"Provider instruments request failed: {str(exc)[:200]}")

@app.get("/v1/option-chain/{symbol}")
def option_chain(symbol: str, market: str = Query(default="NSE"), expiry: str = Query(...)):
    m=market.upper()
    if m not in ("NSE","MCX"): raise HTTPException(status_code=400,detail="market must be NSE or MCX")
    saved=latest_snapshot(m,symbol,expiry)
    if saved: return saved
    provider=get_provider()
    if not provider.status().configured: raise HTTPException(status_code=503,detail="No snapshot is stored and authorized market-data provider is not configured.")
    try: return persist_snapshot(provider.fetch_option_chain(m,symbol,expiry))
    except Exception as exc: raise HTTPException(status_code=502,detail=f"No valid chain available: {str(exc)[:200]}")

@app.get("/v1/snapshot-status")
def snapshot_status():
    provider=get_provider(); calendars={m:calendar_from_env(m) for m in ("NSE","MCX")}
    return {"timezone":"Asia/Kolkata","target_snapshot_time":"18:00","current_time_ist":datetime.now(IST).isoformat(),"scheduler_configured":True,"holiday_calendars":{m:{"configured":c.configured,"holiday_count":len(c.holidays),"special_session_count":len(c.special_sessions)} for m,c in calendars.items()},"data_provider_configured":provider.status().configured,"provider_name":provider.status().provider_name,"latest_status":"READY_TO_FETCH" if provider.status().configured and all(c.configured for c in calendars.values()) else "CONFIGURATION_REQUIRED"}
