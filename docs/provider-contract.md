# OI Rush NSE licensed data provider contract

OI Rush does not scrape exchange webpages. Configure an authorized vendor gateway with OI_RUSH_PROVIDER_BASE_URL, OI_RUSH_PROVIDER_TOKEN, and optionally OI_RUSH_PROVIDER_NAME. Keep secrets in deployment environment variables, never Git. MCX is not currently supported by the app, API, or scheduler.

## Endpoints required from the vendor gateway

### GET /instruments?market=NSE
Return an object with an instruments array. Each item must include symbol, name, and expiries, e.g. NIFTY with expiries in YYYY-MM-DD format. Only include NSE contracts and expiries licensed for this service.

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

## Snapshot-time session calendar: NSE 18:00 IST

Configure these variables: OI_RUSH_NSE_CALENDAR_YEAR, OI_RUSH_NSE_HOLIDAYS, and OI_RUSH_NSE_SPECIAL_SESSIONS. Date lists are comma-separated ISO dates. Calendar-year bounds are mandatory; dates outside the configured year fail closed. Update the calendar annually from official NSE F&O circulars.

Important:

## Snapshot behavior

- Scheduler targets NSE at 18:00 Asia/Kolkata. MCX 23:59 is after the published 23:30/23:55 close for internationally referenceable non-agricultural commodities on ordinary sessions, but it does not mean all commodity categories traded until that time. Each row must retain the provider's actual source timestamp; 23:59 is the capture run time, not a fabricated quote timestamp.
- It skips weekends/holidays and refuses snapshots if calendar/provider configuration is missing or calendar coverage is out of range.
- SQLite is for local single-instance development; use managed PostgreSQL and backups in production.
- Snapshot key is market + underlying + expiry + session date, so retries update rather than duplicate a session record.
- The API serves persisted snapshots only. If no snapshot exists, it returns an unavailable/not-found response rather than silently fetching a different-time chain and labelling it the scheduled snapshot.
- UI must expose session_date, source_timestamp, and status; never present old data as current.
- The vendor agreement must expressly permit intended app display, commercial use, derived calculations, storage/history, and the relevant users/medium.
