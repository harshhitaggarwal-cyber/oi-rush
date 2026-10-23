# OI Rush NSE licensed data provider contract

OI Rush does not scrape exchange webpages. Configure an authorized vendor gateway with `OI_RUSH_PROVIDER_BASE_URL`, `OI_RUSH_PROVIDER_TOKEN`, and optionally `OI_RUSH_PROVIDER_NAME`. Keep secrets in deployment environment variables, never Git. Only NSE is currently supported.

## Endpoints required from the vendor gateway

### GET /instruments?market=NSE
Return an object with an instruments array. Each item must include symbol, name, and expiries, e.g. NIFTY with expiries in YYYY-MM-DD format. Only include NSE contracts and expiries licensed for this service.

### GET /option-chain?market=NSE&underlying=NIFTY&expiry=YYYY-MM-DD
Return an object with market, underlying, expiry, source_timestamp, session_date, underlying_price, and rows. Each row must have numeric strike, call_oi, put_oi, call_coi, put_coi, call_ltp, and put_ltp fields. COI means change in open interest. Include a timezone offset in source_timestamp; validation converts it to Asia/Kolkata before checking session_date.

Example shape:

    {
      "market": "NSE", "underlying": "NIFTY", "expiry": "2026-10-27",
      "source_timestamp": "2026-10-23T15:30:00+05:30",
      "session_date": "2026-10-23", "underlying_price": 25450.5,
      "rows": [{"strike":25400,"call_oi":1234,"put_oi":2345,
        "call_coi":123,"put_coi":456,"call_ltp":110.5,"put_ltp":99.5}]
    }

## Manual CSV import

An operator can download the CSV using the official NSE Option Chain page's Download (.csv) control, then upload it through the Flutter app or the protected backend endpoint. This is a manual upload, not automated website collection.

- Configure a long random `OI_RUSH_CSV_IMPORT_TOKEN` in the API environment.
- The Flutter app sends the file to `POST /v1/admin/upload/nse-csv` as multipart form data. Required metadata: symbol, expiry, session date, actual source timestamp with timezone offset, and underlying price. The token is sent in the `X-Import-Token` header.
- The backend validates the CSV and metadata before persisting a snapshot. Files are limited to 5 MB.
- The JSON alternative `POST /v1/admin/import/nse-csv` is available for trusted backend tooling.
- Never use upload time as the market-data source timestamp.

## Snapshot behavior

- The configured scheduler target is 19:30 Asia/Kolkata for authorized provider fetching. It retries the provider until 20:30. This schedule does not automate manual CSV imports.
- It skips weekends/holidays and refuses scheduled snapshots if calendar/provider configuration is missing or calendar coverage is out of range.
- SQLite is for local single-instance development; use managed PostgreSQL and backups in production.
- Snapshot key is market + underlying + expiry + session date, so retries update rather than duplicate a session record.
- The API serves persisted snapshots only. If no snapshot exists, it returns an unavailable/not-found response rather than silently fetching a different-time chain and labelling it the scheduled snapshot.
- UI must expose session_date, source_timestamp, and status; never present old data as current.
- The vendor agreement must expressly permit intended app display, commercial use, derived calculations, storage/history, and the relevant users/medium.
