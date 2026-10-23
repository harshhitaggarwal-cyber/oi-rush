# OI Rush licensed data provider contract

OI Rush does not scrape exchange webpages. Configure an authorized vendor gateway with OI_RUSH_PROVIDER_BASE_URL, OI_RUSH_PROVIDER_TOKEN, and optionally OI_RUSH_PROVIDER_NAME. Keep secrets in deployment environment variables, never Git.

## Endpoints required from the vendor gateway

### GET /instruments?market=NSE or MCX
Return an object with an instruments array. Each item must include symbol, name, and expiries, e.g. NIFTY with expiries in YYYY-MM-DD format. Only include contracts and expiries licensed for this service. MCX options are options on futures; preserve the underlying futures contract/expiry relationship and include all active commodity option contracts rather than a hard-coded short list.

### GET /option-chain?market=NSE&underlying=NIFTY&expiry=YYYY-MM-DD
Return an object with market, underlying, expiry, source_timestamp, session_date, underlying_price, and rows. Each row must have numeric strike, call_oi, put_oi, call_coi, put_coi, call_ltp, and put_ltp fields. COI means change in open interest. Include a timezone offset in source_timestamp; validation converts it to Asia/Kolkata before checking session_date.

Example shape:

    {
      "market": "NSE", "underlying": "NIFTY", "expiry": "2026-10-27",
      "source_timestamp": "2026-10-23T18:00:01+05:30",
      "session_date": "2026-10-23", "underlying_price": 25450.5,
      "rows": [{"strike":25400,"call_oi":1234,"put_oi":2345,
        "call_coi":123,"put_coi":456,"call_ltp":110.5,"put_ltp":99.5}]
    }

## 18:00 IST session calendar

Configure these variables: OI_RUSH_NSE_CALENDAR_YEAR, OI_RUSH_NSE_HOLIDAYS, OI_RUSH_NSE_SPECIAL_SESSIONS, OI_RUSH_MCX_CALENDAR_YEAR, OI_RUSH_MCX_HOLIDAYS, and OI_RUSH_MCX_SPECIAL_SESSIONS. Date lists are comma-separated ISO dates. Calendar-year bounds are mandatory; dates outside the configured year fail closed. Update the calendar annually from official circulars.

Important: NSE options use the NSE F&O calendar, not the equities holiday list. MCX has separate morning and evening sessions; at 18:00, some dates with a closed morning session are open in the evening. Therefore OI_RUSH_MCX_HOLIDAYS means dates when the 18:00 snapshot-time session is closed, not every date on which the morning session is closed. The repository's 2026 example dates are based on the official NSE F&O and MCX session holiday pages. Special-session dates should be added only after the exchange confirms the session includes the intended 18:00 snapshot time. A date-only calendar cannot safely infer special-session hours.

## Snapshot behavior

- Scheduler target is 18:00 Asia/Kolkata. For MCX this is a time-specific snapshot during its evening session on normal session days, not an end-of-day close.
- It skips weekends/holidays and refuses snapshots if calendar/provider configuration is missing or calendar coverage is out of range.
- SQLite is for local single-instance development; use managed PostgreSQL and backups in production.
- Snapshot key is market + underlying + expiry + session date, so retries update rather than duplicate a session record.
- The API serves persisted snapshots only. If no snapshot exists, it returns an unavailable/not-found response rather than silently fetching a different-time chain and labelling it the 18:00 snapshot.
- UI must expose session_date, source_timestamp, and status; never present old data as current.
- The vendor agreement must expressly permit intended app display, commercial use, derived calculations, storage/history, and the relevant users/medium.
