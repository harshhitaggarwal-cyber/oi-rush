"""Parse the official NSE option-chain CSV export for an explicit backend import.

This module does not download or scrape NSE. An operator supplies a CSV they
have obtained from NSE and its displayed snapshot metadata.
"""
import csv
import io
import math


def _number(value: str) -> float:
    cleaned = (value or "").strip().replace(",", "")
    if cleaned in {"", "-", "--", "NA", "N/A"}:
        return 0.0
    result = float(cleaned)
    if not math.isfinite(result):
        raise ValueError("CSV contains a non-finite numeric value.")
    return result


def parse_nse_option_chain_csv(text: str) -> list[dict]:
    """Parse NSE's 22-column option-chain export into normalized strike rows."""
    if not text or not text.strip():
        raise ValueError("CSV content is empty.")
    rows = csv.reader(io.StringIO(text.lstrip("\ufeff")))
    parsed = []
    for raw in rows:
        # NSE's export may contain one or more header/summary rows. A data row
        # has the strike at column 12 (zero-based index 11).
        if len(raw) < 22:
            continue
        try:
            strike = _number(raw[11])
        except (ValueError, TypeError):
            continue
        if strike <= 0:
            continue
        try:
            parsed.append({
                "strike": strike,
                "call_oi": _number(raw[1]),
                "call_coi": _number(raw[2]),
                "call_ltp": _number(raw[5]),
                "put_ltp": _number(raw[17]),
                "put_coi": _number(raw[20]),
                "put_oi": _number(raw[21]),
            })
        except (ValueError, TypeError, IndexError) as exc:
            raise ValueError(f"Invalid numeric data at strike {strike:g}: {exc}") from exc
    if not parsed:
        raise ValueError("No option-chain data rows found. Please use the NSE equity-derivatives option-chain CSV export.")
    parsed.sort(key=lambda item: item["strike"])
    if len({item["strike"] for item in parsed}) != len(parsed):
        raise ValueError("CSV contains duplicate strike prices.")
    return parsed
