from app.snapshot_job import latest_snapshot, persist_snapshot

def chain():
    return {"market":"NSE","underlying":"NIFTY","expiry":"2026-10-27","source_timestamp":"2026-10-23T18:00:01+05:30","session_date":"2026-10-23","underlying_price":25450.5,"rows":[
      {"strike":25400,"call_oi":100,"put_oi":200,"call_coi":40,"put_coi":60,"call_ltp":10,"put_ltp":12},
      {"strike":25450,"call_oi":150,"put_oi":250,"call_coi":45,"put_coi":50,"call_ltp":11,"put_ltp":13}
    ]}

def test_snapshot_roundtrip_and_idempotency(tmp_path):
    db=tmp_path/"test.sqlite3"
    first=persist_snapshot(chain(),db)
    second=persist_snapshot(chain(),db)
    saved=latest_snapshot("NSE","NIFTY","2026-10-27",db)
    assert first["session_date"] == "2026-10-23"
    assert second["rows"][0]["oi_pcr"] == 2.0
    assert saved["underlying_price"] == 25450.5
    assert len(saved["rows"]) == 2
