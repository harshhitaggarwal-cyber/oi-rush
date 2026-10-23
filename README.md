# OI Rush

**Let's enter the world of FnO with an EDGE.**

Flutter + FastAPI starter for NSE index and stock options only. MCX is currently out of scope and disabled in the API and scheduler. The API calculates OI PCR = Put Total OI / Call Total OI and LTP PCR = Put LTP / Call LTP. OI strategy classification is server-side.

## Current status
- Provider adapter, data validation, SQLite snapshot persistence, exchange-calendar configuration, NSE 19:30 IST scheduler, and backend tests are in the repository.
- No live NSE feed is connected yet. Provider credentials and an authorized vendor agreement are not configured.
- Never present sample or stale rows as current market data.
- Public exchange webpage access is not, by itself, permission to automate extraction or redistribute data/derived analytics in a paid app. A genuinely free source may be used only if its terms expressly allow the intended use.

## Official NSE data access
- NSE Data & Analytics: https://www.nseindia.com/static/market-data/real-time-data-subscription
- NSE data policy: https://www.nseindia.com/static/market-data/nse-data-policy
- Contact: marketdata@nse.co.in.
- Confirm the agreement covers the app/mobile display, commercial use, derived OI analysis, persistence/history, and expected subscriber count. If using a vendor, confirm it is authorized for the needed segments and that redistribution to OI Rush subscribers is permitted.

## Configure a licensed vendor adapter
The code expects a vendor gateway exposing the normalized API contract documented in docs/provider-contract.md. Set these environment variables on both API and scheduler services:
- OI_RUSH_PROVIDER_BASE_URL
- OI_RUSH_PROVIDER_TOKEN
- OI_RUSH_PROVIDER_NAME (optional)

The gateway must expose /instruments?market=NSE and /option-chain?market=NSE&underlying=NIFTY&expiry=YYYY-MM-DD. A real vendor adapter must map the actual licensed vendor protocol into this contract; do not put credentials in Git.

## Import an NSE option-chain CSV (manual upload)

The backend accepts a CSV exported by an operator from the official NSE Option Chain page. This is a manual import workflow; the API does not automatically scrape or download NSE content.

1. Set a long random `OI_RUSH_CSV_IMPORT_TOKEN` in the backend environment and restart the API.
2. Export the selected NSE equity-derivatives option chain using NSE's Download (.csv) control.
3. In the Flutter app, open NSE analysis and tap the upload icon. Choose the `.csv` file and enter the symbol, expiry (`YYYY-MM-DD`), session date (`YYYY-MM-DD`), actual source timestamp (including timezone offset), underlying price, and import token. The app sends a multipart upload to `POST /v1/admin/upload/nse-csv`. The source timestamp must be the actual timestamp for that snapshot, not the upload time. The older JSON endpoint `POST /v1/admin/import/nse-csv` remains available for backend tooling.
4. The backend validates the rows, calculates OI PCR/LTP PCR and strategy labels, and saves the snapshot for the app.

Example request body:
```json
{
  "symbol": "NIFTY",
  "expiry": "2026-10-27",
  "session_date": "2026-10-23",
  "source_timestamp": "2026-10-23T15:30:00+05:30",
  "underlying_price": 25450.5,
  "csv_text": "<paste the full downloaded CSV text here>"
}
```

This import endpoint is disabled unless the token is configured. Manual CSV import does not create a daily automatic fetch. The scheduler targets 19:30 IST and retries an authorized provider every 10 minutes until 20:30 IST. It does not download or scrape the NSE public website; the provider must be configured and permitted for automated retrieval and app display.

## Configure exchange calendars
Copy backend/.env.example to backend/.env and populate complete NSE F&O holiday/special-session dates from the official NSE annual calendar. Variables include OI_RUSH_NSE_CALENDAR_YEAR, OI_RUSH_NSE_HOLIDAYS, and OI_RUSH_NSE_SPECIAL_SESSIONS (comma-separated YYYY-MM-DD). Empty calendars fail closed. Example dates in documentation are illustrative only, not official lists.

## Run the Flutter app\n```bash\ncd flutter_app\nflutter pub get\nflutter run --dart-define=OI_RUSH_API_URL=http://localhost:8000\n```\nFor an Android emulator, use `--dart-define=OI_RUSH_API_URL=http://10.0.2.2:8000`. For a deployed app, set the URL to your HTTPS API host. Do not embed the admin import token in the app; enter it only when performing an authorized manual upload.\n\n## Run backend locally
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

Run the scheduled worker in a separate terminal:
```bash
cd backend
source .venv/bin/activate
python -m app.scheduler
```
The scheduler targets NSE at 19:30 Asia/Kolkata on configured session days. It does not create snapshots if the provider or calendar is missing. Run both services continuously on a reliable host to execute scheduled jobs.

## Docker local setup
1. Copy backend/.env.example to backend/.env and configure it.
2. Run `docker compose up --build` from the repository root.
3. API docs are at http://localhost:8000/docs. API and scheduler share the persistent data volume.

SQLite is for local/single-instance development; production should use managed PostgreSQL, backups, monitoring, retries and a durable scheduler deployment.

## Run tests
```bash
cd backend
pip install -r requirements.txt
pytest -q
```
GitHub Actions runs backend tests on relevant pushes and pull requests.

## Strategy labels
- Strong Bullish: Call COI positive and Put COI negative at both adjacent strikes.
- Strong Bearish: Call COI negative and Put COI positive at both adjacent strikes.
- Initially Bullish: all four COI values positive; Put COI > Call COI at both strikes; previous strike's Put COI is highest and Call COI lowest among the four COI values.
- Initially Bearish: all four COI values positive; Call COI > Put COI at both strikes; current/next strike's Call COI is highest and Put COI lowest among the four COI values.
- Otherwise Neutral / No Setup.

## Still required before production
- Authorized NSE feed and explicit commercial/derived-data display rights.
- Vendor-specific protocol mapping and complete active NSE contract master.
- Verified official NSE F&O holiday/special-session calendar and production scheduler.
- Managed database, authentication, subscription entitlement checks, monitoring, backup/restore and Android device tests.
