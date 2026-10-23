"""Normalized provider adapter for a licensed NSE/MCX market-data service.

The upstream service must normalize its licensed source into the documented OI Rush
JSON contract. This module does not scrape exchange websites and never invents data.
"""
from dataclasses import dataclass
from datetime import date, datetime
import math
import os
from typing import Protocol
from urllib.parse import urljoin
from zoneinfo import ZoneInfo
import httpx

IST = ZoneInfo("Asia/Kolkata")

@dataclass(frozen=True)
class ProviderStatus:
    configured: bool
    provider_name: str | None
    message: str

class MarketDataProvider(Protocol):
    def status(self) -> ProviderStatus: ...
    def fetch_instruments(self, market: str) -> list[dict]: ...
    def fetch_option_chain(self, market: str, underlying: str, expiry: str) -> dict: ...

class UnconfiguredProvider:
    def status(self) -> ProviderStatus:
        return ProviderStatus(False, None, "No authorized market-data provider configured.")
    def fetch_instruments(self, market: str) -> list[dict]:
        raise RuntimeError("Market-data provider is not configured.")
    def fetch_option_chain(self, market: str, underlying: str, expiry: str) -> dict:
        raise RuntimeError("Market-data provider is not configured; live data is unavailable.")

class HttpJsonProvider:
    """Adapter for an authorized vendor gateway implementing the OI Rush JSON contract."""
    def __init__(self, base_url: str, token: str, provider_name: str = "authorized-provider"):
        self.base_url = base_url.rstrip("/") + "/"
        self.token = token
        self.provider_name = provider_name

    @classmethod
    def from_env(cls):
        base_url = os.getenv("OI_RUSH_PROVIDER_BASE_URL", "").strip()
        token = os.getenv("OI_RUSH_PROVIDER_TOKEN", "").strip()
        if not base_url or not token:
            return UnconfiguredProvider()
        return cls(base_url, token, os.getenv("OI_RUSH_PROVIDER_NAME", "authorized-provider"))

    def status(self) -> ProviderStatus:
        return ProviderStatus(True, self.provider_name, "Credentials configured; upstream reachability is checked on fetch.")

    def _get(self, path: str, params: dict) -> dict:
        response = httpx.get(urljoin(self.base_url, path.lstrip("/")), params=params,
            headers={"Authorization": f"Bearer {self.token}", "Accept": "application/json"}, timeout=20.0)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Provider response must be a JSON object.")
        return payload

    def fetch_instruments(self, market: str) -> list[dict]:
        payload = self._get("instruments", {"market": market.upper()})
        instruments = payload.get("instruments")
        if not isinstance(instruments, list):
            raise ValueError("Provider response must contain an instruments array.")
        validated = []
        for item in instruments:
            if not isinstance(item, dict) or not item.get("symbol") or not isinstance(item.get("expiries"), list):
                raise ValueError("Each instrument needs symbol and expiries fields.")
            if any(not isinstance(expiry, str) for expiry in item["expiries"]):
                raise ValueError("Every expiry must be a string in the vendor contract's documented format.")
            validated.append(item)
        return validated

    def fetch_option_chain(self, market: str, underlying: str, expiry: str) -> dict:
        payload = self._get("option-chain", {"market": market.upper(), "underlying": underlying, "expiry": expiry})
        validate_chain_payload(payload, market, underlying, expiry)
        return payload


def validate_chain_payload(payload: dict, market: str, underlying: str, expiry: str) -> None:
    required = ("market", "underlying", "expiry", "source_timestamp", "session_date", "underlying_price", "rows")
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"Provider response missing fields: {', '.join(missing)}")
    if str(payload["market"]).upper() != market.upper() or str(payload["underlying"]).upper() != underlying.upper() or str(payload["expiry"]) != expiry:
        raise ValueError("Provider response contract does not match requested market, underlying and expiry.")
    timestamp = datetime.fromisoformat(str(payload["source_timestamp"]).replace("Z", "+00:00"))
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("source_timestamp must include a timezone offset.")
    session_day = date.fromisoformat(str(payload["session_date"]))
    if timestamp.astimezone(IST).date() != session_day:
        raise ValueError("Provider timestamp in Asia/Kolkata does not match session_date.")
    price = payload["underlying_price"]
    if not isinstance(price, (int, float)) or not math.isfinite(price) or price <= 0:
        raise ValueError("underlying_price must be a finite positive number.")
    if not isinstance(payload["rows"], list) or not payload["rows"]:
        raise ValueError("Provider option chain rows must be a non-empty array.")
    previous_strike = None
    for row in payload["rows"]:
        for key in ("strike", "call_oi", "put_oi", "call_coi", "put_coi", "call_ltp", "put_ltp"):
            if key not in row or not isinstance(row[key], (int, float)) or not math.isfinite(row[key]):
                raise ValueError(f"Each row must contain finite numeric {key}.")
        if row["strike"] <= 0 or row["call_oi"] < 0 or row["put_oi"] < 0 or row["call_ltp"] < 0 or row["put_ltp"] < 0:
            raise ValueError("Strike, total OI and LTP values must be non-negative; strike must be positive.")
        if previous_strike is not None and row["strike"] <= previous_strike:
            raise ValueError("Provider rows must be sorted by strictly increasing strike.")
        previous_strike = row["strike"]
