# OI Rush

**Let's enter the world of FnO with an EDGE.**

Flutter + FastAPI starter for NSE index/stock options and MCX commodity options. The API calculates OI PCR = Put Total OI / Call Total OI and LTP PCR = Put LTP / Call LTP. OI strategy classification is server-side.

## Current status
- Provider adapter, data validation, SQLite snapshot persistence, exchange-calendar configuration, 18:00 IST scheduler, and backend tests are in the repository.
- No live NSE/MCX feed is connected yet. Credentials and an authorized vendor agreement are not available in this repository.
- Never present sample or stale rows as current market data.
- Public exchange webpage access is not, by itself, permission to redistribute data or derived analytics in a paid app.

## Official data access
- NSE Data & Analytics: https://www.nseindia.com/static/market-data/real-time-data-subscription and https://www.nseindia.com/static/market-data/nse-data-policy. Contact: marketdata@nse.co.in.
- MCX datafeed: https://www.mcxindia.com/technology/datafeed and https://www.mcxindia.com/faq/technology-services. Contact: datafeed@mcxindia.com.
- Confirm the agreement covers the app/mobile display, commercial use, derived OI analysis, persistence/history, and expected subscriber count. If using a vendor, confirm it is authorized for the needed segments and that redistribution to OI Rush subscribers is permitted.

## Configure a licensed vendor adapter
The code expects a vendor gateway exposing the normalized API contract documented in docs/provider-contract.md. Set these environment variables on both API and scheduler services:
- OI_RUSH_PROVIDER_BASE_URL
- OI_RUSH_PROVIDER_TOKEN
- OI_RUSH_PROVIDER_NAME (optional)

The gateway must expose /instruments?market=NSE|MCX and /option-chain?market=NSE&underlying=NIFTY&expiry=YYYY-MM-DD. A real vendor adapter must map the actual licensed vendor protocol into this contract; do not put credentials in Git.

## Configure exchange calendars
Copy backend/.env.example to backend/.env and populate separate complete holiday/special-session dates from the official NSE and MCX annual calendars. Variables are OI_RUSH_NSE_HOLIDAYS, OI_RUSH_NSE_SPECIAL_SESSIONS, OI_RUSH_MCX_HOLIDAYS, and OI_RUSH_MCX_SPECIAL_SESSIONS (comma-separated YYYY-MM-DD). Empty calendars fail closed. Example dates in documentation are illustrative only, not official lists.

## Run backend locally
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
The scheduler targets 18:00 Asia/Kolkata on configured session days. It does not create snapshots if the provider or calendar is missing. Run both services continuously on a reliable host to execute scheduled jobs.

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
- Authorized NSE and MCX feed and explicit commercial/derived-data display rights.
- Vendor-specific protocol mapping and full active contract master, including MCX options-on-futures expiry context.
- Verified official holiday/special-session calendars and production scheduler.
- Managed database, authentication, subscription entitlement checks, monitoring, backup/restore and Android device tests.
