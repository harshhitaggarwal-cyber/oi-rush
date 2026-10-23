"""Market-data provider boundary.

Connect only an exchange-approved or otherwise authorized data source here.
This deliberately fails closed instead of scraping public pages or fabricating prices.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class ProviderStatus:
    configured: bool
    provider_name: str | None
    message: str


class MarketDataProvider(Protocol):
    def status(self) -> ProviderStatus: ...
    def fetch_option_chain(self, market: str, underlying: str, expiry: str) -> dict: ...


class UnconfiguredProvider:
    def status(self) -> ProviderStatus:
        return ProviderStatus(False, None, "No authorized market-data provider configured.")

    def fetch_option_chain(self, market: str, underlying: str, expiry: str) -> dict:
        raise RuntimeError("Market-data provider is not configured; live data is unavailable.")


def validate_snapshot_timestamp(timestamp: datetime, expected_session_date) -> None:
    """Reject mismatched session dates; callers should persist the source timestamp."""
    if timestamp.date() != expected_session_date:
        raise ValueError("Snapshot timestamp does not match the expected exchange session date.")
