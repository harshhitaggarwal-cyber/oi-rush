"""Server-side OI Rush strategy engine. Signed values represent COI, not total OI."""
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class StrikeData:
    strike: float
    call_oi: float
    put_oi: float
    call_coi: float
    put_coi: float
    call_ltp: float
    put_ltp: float

def ratio(numerator: float, denominator: float) -> Optional[float]:
    return None if denominator <= 0 else numerator / denominator

def classify_pair(previous: StrikeData, current: StrikeData) -> str:
    vals = (previous.call_coi, previous.put_coi, current.call_coi, current.put_coi)
    if previous.call_coi > 0 and previous.put_coi < 0 and current.call_coi > 0 and current.put_coi < 0:
        return "Strong Bullish"
    if previous.call_coi < 0 and previous.put_coi > 0 and current.call_coi < 0 and current.put_coi > 0:
        return "Strong Bearish"
    if all(v > 0 for v in vals):
        if (previous.put_coi > previous.call_coi and current.put_coi > current.call_coi and previous.put_coi == max(vals) and previous.call_coi == min(vals)):
            return "Initially Bullish"
        if (previous.call_coi > previous.put_coi and current.call_coi > current.put_coi and current.call_coi == max(vals) and current.put_coi == min(vals)):
            return "Initially Bearish"
    return "Neutral / No Setup"

def make_row(data: StrikeData, analysis: str) -> dict:
    return {"strike": data.strike, "oi_pcr": ratio(data.put_oi, data.call_oi), "ltp_pcr": ratio(data.put_ltp, data.call_ltp), "oi_analysis": analysis}
