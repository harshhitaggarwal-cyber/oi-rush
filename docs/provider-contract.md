# OI Rush licensed data provider contract

OI Rush does not scrape exchange webpages. Configure an authorized vendor gateway with OI_RUSH_PROVIDER_BASE_URL, OI_RUSH_PROVIDER_TOKEN, and optionally OI_RUSH_PROVIDER_NAME. Keep secrets in deployment environment variables, never Git.

## Endpoints required from the vendor gateway

### GET /instruments?market=NSE or MCX
Return an object with an instruments array. Each item must include symbol, name, and expiries, e.g. NIFTY with expiries in YYYY-MM-DD format. Only include contracts and expiries licensed for this service. MCX options are options on futures; preserve the underlying futures contract/expiry relationship and include all active commodity option contracts rather than a hard-coded short list.

### GET /option-chain?market=NSE&underlying=NIFTY&expiry=YYYY-MM-DD
Return an object with market, underlying, expiry, source_timestamp, session_date, underlying_price, and rows. Each row must have numeric strike, call_oi, put_oi, call_coi, put_coi, call_ltp, and put_ltp fields. COI means change in open interest. Normalize source_timestamp to Asia/Kolkata before matching its date with session_date.

Example shape:

    {
      "market": "NSE", "underlying": "NIFTY", "expiry": "2026-10-27",
      "source_timestamp": "2026-10-23T18:00:01+05:30",
      "session_date": "2026-10-23", "underlying_price": 25450.5,
      "rows": [{"strike":25400,"call_oi":1234,"put_oi":2345,
        "call_coi":123,"put_coi":456,"call_ltp":110.5,"put_ltp":99.5}]
    }

## Calendar configuration

Populate reviewed official NSE and MCX calendars separately in deployment variables: OI_RUSH_NSE_HOLIDAYS, OI_RUSH_NSE_SPECIAL_SESSIONS, OI_RUSH_MCX_HOLIDAYS, and OI_RUSH_MCX_SPECIAL_SESSIONS. Values are comma-separated ISO dates. Empty/missing holiday configuration makes the calendar fail closed. These are not bundled as official dates; maintain them from each exchange's official annual circular and validate special-session hours independently.

## Snapshot behavior

- Scheduler target is 18:00 Asia/Kolkata.
- It skips non-session days and refuses snapshots if calendar/provider configuration is missing.
- SQLite is for local single-instance development; use managed PostgreSQL and backups in production.
- Snapshot key is market + underlying + expiry + session date, so retries update rather than duplicate a session record.
- UI must expose session_date, source_timestamp, and status; never present old data as current.
- The vendor agreement must expressly permit intended app display, commercial use, derived calculations, storage/history, and the relevant users/medium.
