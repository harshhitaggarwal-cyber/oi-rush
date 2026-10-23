import pytest
from app.providers import validate_chain_payload

def payload():
    return {"market":"NSE","underlying":"NIFTY","expiry":"2026-10-27","source_timestamp":"2026-10-23T18:00:01+05:30","session_date":"2026-10-23","underlying_price":25450.5,"rows":[{"strike":25400,"call_oi":100,"put_oi":200,"call_coi":10,"put_coi":20,"call_ltp":100.0,"put_ltp":90.0}]}

def test_valid_payload(): validate_chain_payload(payload(),"NSE","NIFTY","2026-10-27")
def test_wrong_underlying():
    with pytest.raises(ValueError): validate_chain_payload(payload(),"NSE","BANKNIFTY","2026-10-27")
def test_timestamp_session_mismatch():
    p=payload(); p["session_date"]="2026-10-22"
    with pytest.raises(ValueError): validate_chain_payload(p,"NSE","NIFTY","2026-10-27")
def test_empty_rows():
    p=payload(); p["rows"]=[]
    with pytest.raises(ValueError): validate_chain_payload(p,"NSE","NIFTY","2026-10-27")
