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

## Snapshot-time session calendar: NSE 18:00 IST, MCX 23:59 IST

Configure these variables: OI_RUSH_NSE_CALENDAR_YEAR, OI_RUSH_NSE_HOLIDAYS, OI_RUSH_NSE_SPECIAL_SESSIONS, OI_RUSH_MCX_CALENDAR_YEAR, OI_RUSH_MCX_HOLIDAYS, and OI_RUSH_MCX_SPECIAL_SESSIONS. Date lists are comma-separated ISO dates. Calendar-year bounds are mandatory; dates outside the configured year fail closed. Update the calendar annually from official circulars.

Important: NSE options use the NSE F&O calendar, not the equities holiday list. MCX has separate morning and evening sessions; at 23:59, internationally referenceable non-agricultural contracts may trade until 23:30 or 23:55 depending on the seasonal schedule, while other commodity categories close earlier. Therefore OI_RUSH_MCX_HOLIDAYS means dates when the 23:59 snapshot-time run should be skipped, not every date on which the morning session is closed. The repository's 2026 example dates are based on the official NSE F&O and MCX session holiday pages. Special-session dates should be added only after the exchange confirms the session schedule and the intended 23:59 run is valid. A date-only calendar cannot safely infer special-session hours.

## Snapshot behavior

- Scheduler targets NSE at 18:00 and MCX at 23:59 Asia/Kolkata. MCX 23:59 is after the published 23:30/23:55 close for internationally referenceable non-agricultural commodities on ordinary sessions, but it does not mean all commodity categories traded until that time. Each row must retain the provider's actual source timestamp; 23:59 is the capture run time, not a fabricated quote timestamp.
- It skips weekends/holidays and refuses snapshots if calendar/provider configuration is missing or calendar coverage is out of range.
- SQLite is for local single-instance development; use managed PostgreSQL and backups in production.
- Snapshot key is market + underlying + expiry + session date, so retries update rather than duplicate a session record.
- The API serves persisted snapshots only. If no snapshot exists, it returns an unavailable/not-found response rather than silently fetching a different-time chain and labelling it the scheduled snapshot.
- UI must expose session_date, source_timestamp, and status; never present old data as current.
- The vendor agreement must expressly permit intended app display, commercial use, derived calculations, storage/history, and the relevant users/medium.
