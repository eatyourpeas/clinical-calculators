from __future__ import annotations

import math

from calculators.bmi import BMIRequest, calculate


def test_bmi_metric_normal():
    resp = calculate({"unit_system": "metric", "weight": 70, "height": 1.75})
    assert abs(resp.result - 22.86) < 0.01
    assert resp.interpretation == "Normal"
    assert resp.metadata["calculator_name"] == "bmi"


def test_bmi_imperial():
    # 154.324 lb, 68.8976 in ~ 70kg, 1.75m
    resp = calculate({"unit_system": "imperial", "weight": 154.324, "height": 68.8976})
    assert abs(resp.result - 22.86) < 0.02


def test_invalid_height_imperial():
    try:
        calculate({"unit_system": "imperial", "weight": 150, "height": 200})
    except Exception as e:
        assert "height (in)" in str(e)
