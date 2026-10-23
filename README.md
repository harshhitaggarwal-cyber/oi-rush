# OI Rush

**Let's enter the world of FnO with an EDGE.**

Flutter + FastAPI starter for NSE index/stock options and MCX commodity options. The UI has Strike, OI PCR, LTP PCR, and OI Analysis.

## Status
- Development starter, not production-ready.
- No live NSE/MCX feed connected; all sample rows are fictional demo data.
- Commercial data access/redistribution permission must be verified with the exchanges or an authorized provider.
- Strategy rules live on the backend, not in the production mobile client.

## Strategy
- Strong Bullish: Call COI positive and Put COI negative at both adjacent strikes.
- Strong Bearish: Call COI negative and Put COI positive at both adjacent strikes.
- Initially Bullish: all four COI values positive; Put COI > Call COI at both strikes; previous strike's Put COI is highest and Call COI lowest among the four COI values.
- Initially Bearish: all four COI values positive; Call COI > Put COI at both strikes; current/next strike's Call COI is highest and Put COI lowest among the four COI values.
- Otherwise Neutral / No Setup.

## Run backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

## Run Flutter
Install Flutter SDK, then run `cd flutter_app && flutter pub get && flutter run`.

## Required before release
- Approved data access for NSE and MCX, including commercial display, derived analytics and historical storage.
- Official contract master for all active MCX commodity options and NSE contracts.
- Exchange holiday and special-session calendar.
- Persistent, idempotent 18:00 Asia/Kolkata snapshot scheduler.
- Authentication, subscription entitlement checks, monitoring, backups and Android device tests.
- Never silently show stale data as today's snapshot.
