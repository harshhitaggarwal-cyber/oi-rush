import pytest

from app.nse_csv_import import parse_nse_option_chain_csv


def test_parse_nse_csv_strike_oi_ltp_and_change_in_oi():
    row = [""] * 22
    row[1] = "12,345"
    row[2] = "123"
    row[5] = "101.25"
    row[11] = "25,000.00"
    row[17] = "98.50"
    row[20] = "-45"
    row[21] = "23,456"
    csv_text = ",".join(["CALLS"] + [""] * 21) + "\n" + ",".join(row)
    parsed = parse_nse_option_chain_csv(csv_text)
    assert parsed == [{
        "strike": 25000.0,
        "call_oi": 12345.0,
        "call_coi": 123.0,
        "call_ltp": 101.25,
        "put_ltp": 98.5,
        "put_coi": -45.0,
        "put_oi": 23456.0,
    }]


def test_parse_nse_csv_rejects_empty_or_unrecognized_data():
    with pytest.raises(ValueError):
        parse_nse_option_chain_csv("")
    with pytest.raises(ValueError):
        parse_nse_option_chain_csv("not an option chain")
