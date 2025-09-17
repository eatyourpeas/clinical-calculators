import pytest
from calculators.dcct_ifcc import calculate, DCCTIFCCRequest

def test_dcct_to_ifcc():
    # Example: 7% DCCT should be about 53 mmol/mol IFCC
    req = {"input_unit": "dcct", "value": 7.0}
    resp = calculate(req)
    assert abs(resp.result - 53) < 0.5
    assert resp.working["formula"] == "IFCC = (DCCT - 2.15) × 10.929"
    assert "mmol/mol" in resp.working["calculation"]
    assert "DCCT" in resp.working["formula"]
    assert resp.interpretation.startswith("7.0% DCCT")

def test_ifcc_to_dcct():
    # Example: 53 mmol/mol IFCC should be about 7% DCCT
    req = {"input_unit": "ifcc", "value": 53.0}
    resp = calculate(req)
    assert abs(resp.result - 7.0) < 0.05
    assert resp.working["formula"] == "DCCT = (IFCC / 10.929) + 2.15"
    assert "%" in resp.working["calculation"]
    assert resp.interpretation.endswith("Diabetes")

def test_invalid_unit():
    with pytest.raises(ValueError):
        calculate({"input_unit": "foo", "value": 10})

def test_invalid_value():
    with pytest.raises(ValueError, match="value must be > 0"):
        calculate({"input_unit": "dcct", "value": -1})
    with pytest.raises(ValueError, match="value must be > 0"):
        calculate({"input_unit": "ifcc", "value": 0})

def test_dcct_upper_limit():
    with pytest.raises(ValueError, match="DCCT value must be ≤ 20%"):
        calculate({"input_unit": "dcct", "value": 21})
    # 20 is valid
    resp = calculate({"input_unit": "dcct", "value": 20})
    assert resp.result >= 0

def test_ifcc_upper_limit():
    with pytest.raises(ValueError, match="IFCC value must be ≤ 200 mmol/mol"):
        calculate({"input_unit": "ifcc", "value": 201})
    # 200 is valid
    resp = calculate({"input_unit": "ifcc", "value": 200})
    assert resp.result >= 0
