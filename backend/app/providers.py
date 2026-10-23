"""Normalized provider adapter for a licensed NSE/MCX market-data service.

The upstream service must normalize its licensed source into the documented OI Rush
JSON contract. This module does not scrape exchange websites and never invents data.
"""
from dataclasses import dataclass
from datetime import date, datetime
import os
from typing import Protocol
from urllib.parse import urljoin

import httpx


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
    """Adapter for a vendor gateway implementing the OI Rush normalized JSON contract.

    Required environment variables:
      OI_RUSH_PROVIDER_BASE_URL=https://your-authorized-vendor.example/api/
      OI_RUSH_PROVIDER_TOKEN=...
      OI_RUSH_PROVIDER_NAME=Vendor name (optional)

    Endpoints:
      GET /instruments?market=NSE|MCX -> {"instruments":[{"symbol":"NIFTY",
          "name":"NIFTY","expiries":["YYYY-MM-DD"]}]}
      GET /option-chain?market=NSE&underlying=NIFTY&expiry=YYYY-MM-DD -> normalized
      chain payload described in docs/provider-contract.md.
    """
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
        return ProviderStatus(True, self.provider_name, "Provider credentials configured; upstream reachability is checked on fetch.")

    def _get(self, path: str, params: dict) -> dict:
        url = urljoin(self.base_url, path.lstrip("/"))
        response = httpx.get(url, params=params, headers={"Authorization": f"Bearer {self.token}", "Accept": "application/json"}, timeout=20.0)
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
    session_day = date.fromisoformat(str(payload["session_date"]))
    if timestamp.date() != session_day:
        raise ValueError("Provider timestamp date does not match session_date; normalize timestamps to Asia/Kolkata before sending.")
    if not isinstance(payload["rows"], list) or not payload["rows"]:
        raise ValueError("Provider option chain rows must be a non-empty array.")
    for row in payload["rows"]:
        for key in ("strike", "call_oi", "put_oi", "call_coi", "put_coi", "call_ltp", "put_ltp"):
            if key not in row or not isinstance(row[key], (int, float)):
                raise ValueError(f"Each row must contain numeric {key}.")
