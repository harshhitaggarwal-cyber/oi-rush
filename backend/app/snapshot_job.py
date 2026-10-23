"""Snapshot orchestration: validated provider data -> strategy metrics -> durable SQLite."""
from datetime import date, datetime
import json
import os
import sqlite3
from pathlib import Path
from zoneinfo import ZoneInfo

from .market_calendar import ExchangeCalendar
from .oi_engine import StrikeData, classify_pair, make_row
from .providers import MarketDataProvider, validate_chain_payload

IST = ZoneInfo("Asia/Kolkata")
DEFAULT_DB = Path(os.getenv("OI_RUSH_DB_PATH", "data/oi_rush.sqlite3"))


def connect_db(db_path: str | Path = DEFAULT_DB):
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        market TEXT NOT NULL, underlying TEXT NOT NULL, expiry TEXT NOT NULL,
        session_date TEXT NOT NULL, source_timestamp TEXT NOT NULL,
        captured_at_ist TEXT NOT NULL, underlying_price REAL,
        status TEXT NOT NULL, payload_json TEXT NOT NULL,
        UNIQUE(market, underlying, expiry, session_date)
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS snapshot_runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, market TEXT NOT NULL,
        session_date TEXT NOT NULL, started_at_ist TEXT NOT NULL,
        finished_at_ist TEXT NOT NULL, status TEXT NOT NULL,
        detail_json TEXT NOT NULL
    )""")
    conn.commit()
    return conn


def normalized_rows(chain: dict) -> list[dict]:
    source_rows = sorted(chain["rows"], key=lambda r: float(r["strike"]))
    data = [StrikeData(
        strike=float(r["strike"]), call_oi=float(r["call_oi"]), put_oi=float(r["put_oi"]),
        call_coi=float(r["call_coi"]), put_coi=float(r["put_coi"]),
        call_ltp=float(r["call_ltp"]), put_ltp=float(r["put_ltp"])) for r in source_rows]
    result = []
    for i, item in enumerate(data):
        analysis = "Neutral / No Setup" if i == 0 else classify_pair(data[i-1], item)
        row = make_row(item, analysis)
        row["oi_pcr"] = round(row["oi_pcr"], 4) if row["oi_pcr"] is not None else None
        row["ltp_pcr"] = round(row["ltp_pcr"], 4) if row["ltp_pcr"] is not None else None
        result.append(row)
    return result


def persist_snapshot(chain: dict, db_path: str | Path = DEFAULT_DB) -> dict:
    captured = datetime.now(IST).isoformat()
    market, underlying, expiry = chain["market"].upper(), chain["underlying"].upper(), str(chain["expiry"])
    session_date, source_timestamp = str(chain["session_date"]), str(chain["source_timestamp"])
    payload = {
        "market": market, "underlying": underlying, "expiry": expiry,
        "session_date": session_date, "source_timestamp": source_timestamp,
        "captured_at_ist": captured, "underlying_price": chain["underlying_price"],
        "snapshot_status": "AVAILABLE", "columns": ["Strike", "OI PCR", "LTP PCR", "OI Analysis"],
        "rows": normalized_rows(chain)
    }
    conn = connect_db(db_path)
    try:
        conn.execute("""INSERT INTO snapshots
          (market, underlying, expiry, session_date, source_timestamp, captured_at_ist,
           underlying_price, status, payload_json)
          VALUES (?, ?, ?, ?, ?, ?, ?, 'AVAILABLE', ?)
          ON CONFLICT(market, underlying, expiry, session_date) DO UPDATE SET
           source_timestamp=excluded.source_timestamp, captured_at_ist=excluded.captured_at_ist,
           underlying_price=excluded.underlying_price, status='AVAILABLE', payload_json=excluded.payload_json""",
          (market, underlying, expiry, session_date, source_timestamp, captured, chain["underlying_price"], json.dumps(payload)))
        conn.commit()
    finally:
        conn.close()
    return payload


def latest_snapshot(market: str, underlying: str, expiry: str, db_path: str | Path = DEFAULT_DB):
    conn = connect_db(db_path)
    try:
        row = conn.execute("""SELECT payload_json FROM snapshots
            WHERE market=? AND underlying=? AND expiry=? AND status='AVAILABLE'
            ORDER BY session_date DESC, source_timestamp DESC LIMIT 1""",
            (market.upper(), underlying.upper(), expiry)).fetchone()
        return json.loads(row[0]) if row else None
    finally:
        conn.close()


def record_run(market: str, session_date: date, status: str, details: dict,
               db_path: str | Path = DEFAULT_DB, started: datetime | None = None):
    finished = datetime.now(IST)
    started = started or finished
    conn = connect_db(db_path)
    try:
        conn.execute("INSERT INTO snapshot_runs(market, session_date, started_at_ist, finished_at_ist, status, detail_json) VALUES (?, ?, ?, ?, ?, ?)",
            (market.upper(), str(session_date), started.astimezone(IST).isoformat(), finished.isoformat(), status, json.dumps(details)))
        conn.commit()
    finally:
        conn.close()


def run_snapshot(exchange: str, session_date: date, calendar: ExchangeCalendar,
                 provider: MarketDataProvider, instruments: list[dict],
                 db_path: str | Path = DEFAULT_DB) -> dict:
    started = datetime.now(IST)
    if calendar.exchange != exchange.upper():
        return {"status": "ERROR", "reason": "calendar_exchange_mismatch"}
    calendar_status = calendar.status(session_date)
    if calendar_status == "CALENDAR_UNCONFIGURED":
        result = {"status": "UNAVAILABLE", "reason": "calendar_unconfigured", "session_date": str(session_date)}
        record_run(exchange, session_date, result["status"], result, db_path, started)
        return result
    if calendar_status == "CALENDAR_OUT_OF_RANGE":
        result = {"status": "UNAVAILABLE", "reason": "calendar_out_of_range", "session_date": str(session_date)}
        record_run(exchange, session_date, result["status"], result, db_path, started)
        return result
    if calendar_status == "NON_TRADING_DAY":
        result = {"status": "SKIPPED", "reason": "non_trading_day", "session_date": str(session_date)}
        record_run(exchange, session_date, result["status"], result, db_path, started)
        return result
    provider_status = provider.status()
    if not provider_status.configured:
        result = {"status": "UNAVAILABLE", "reason": "provider_unconfigured", "session_date": str(session_date)}
        record_run(exchange, session_date, result["status"], result, db_path, started)
        return result
    saved, errors = [], []
    for instrument in instruments:
        symbol = instrument["symbol"]
        for expiry in instrument.get("expiries", []):
            try:
                chain = provider.fetch_option_chain(exchange, symbol, str(expiry))
                validate_chain_payload(chain, exchange, symbol, str(expiry))
                if date.fromisoformat(str(chain["session_date"])) != session_date:
                    raise ValueError("Provider returned a different session date.")
                payload = persist_snapshot(chain, db_path)
                saved.append({"underlying": symbol, "expiry": str(expiry), "row_count": len(payload["rows"])})
            except Exception as exc:
                errors.append({"underlying": symbol, "expiry": str(expiry), "error": str(exc)[:300]})
    status = "AVAILABLE" if saved and not errors else ("PARTIAL" if saved else "FAILED")
    result = {"status": status, "market": exchange.upper(), "session_date": str(session_date),
              "saved_chains": saved, "errors": errors, "provider": provider_status.provider_name}
    record_run(exchange, session_date, status, result, db_path, started)
    return result
