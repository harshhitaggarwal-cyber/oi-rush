"""Manual browser/app upload for operator-downloaded NSE option-chain CSV files."""
from datetime import date
import hmac
import os

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile

from .nse_csv_import import parse_nse_option_chain_csv
from .providers import validate_chain_payload
from .snapshot_job import persist_snapshot

router = APIRouter()
MAX_CSV_BYTES = 5_000_000


@router.post("/v1/admin/upload/nse-csv")
async def upload_nse_csv(
    file: UploadFile = File(...),
    symbol: str = Form(..., min_length=1, max_length=40),
    expiry: str = Form(..., min_length=8, max_length=20),
    session_date: date = Form(...),
    source_timestamp: str = Form(..., min_length=10, max_length=50),
    underlying_price: float = Form(..., gt=0),
    x_import_token: str | None = Header(default=None, alias="X-Import-Token"),
):
    """Accept a manually selected CSV; never downloads or scrapes NSE."""
    expected = os.getenv("OI_RUSH_CSV_IMPORT_TOKEN", "").strip()
    if not expected:
        raise HTTPException(status_code=503, detail="CSV upload is disabled until OI_RUSH_CSV_IMPORT_TOKEN is configured.")
    if not x_import_token or not hmac.compare_digest(x_import_token, expected):
        raise HTTPException(status_code=401, detail="Invalid import token.")
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=415, detail="Choose an NSE option-chain .csv file.")
    raw = await file.read(MAX_CSV_BYTES + 1)
    if len(raw) > MAX_CSV_BYTES:
        raise HTTPException(status_code=413, detail="CSV file must be 5 MB or smaller.")
    try:
        csv_text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=422, detail="CSV must be UTF-8 encoded. Re-download the file from NSE.") from exc
    symbol = symbol.strip().upper()
    expiry = expiry.strip()
    try:
        rows = parse_nse_option_chain_csv(csv_text)
        chain = {
            "market": "NSE",
            "underlying": symbol,
            "expiry": expiry,
            "session_date": session_date.isoformat(),
            "source_timestamp": source_timestamp,
            "underlying_price": underlying_price,
            "rows": rows,
        }
        validate_chain_payload(chain, "NSE", symbol, expiry)
        payload = persist_snapshot(chain)
        return {
            "status": "AVAILABLE",
            "market": "NSE",
            "underlying": symbol,
            "expiry": expiry,
            "session_date": payload["session_date"],
            "source_timestamp": payload["source_timestamp"],
            "row_count": len(payload["rows"]),
            "message": "CSV uploaded, validated, and saved.",
        }
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=f"CSV upload failed: {str(exc)[:250]}") from exc
    finally:
        await file.close()
