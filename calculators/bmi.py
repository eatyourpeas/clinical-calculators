
"""
# BMI Calculator

## 📂 Configuration (TOML-style in docstring)

[inputs]
- name: weight
  type: number
  unit: kg (UCUM: kg) | lb (UCUM: [lb_av])
  required: true
  min: 0.0
  max: 500.0
  description: Patient's weight (in kg or lb)

- name: height
  type: number
  unit: m (UCUM: m) | in (UCUM: [in_i])
  required: true
  min: 0.0
  max: 3.0
  description: Patient's height (in meters or inches)

- name: unit_system
  type: string
  enum: ["metric", "imperial"]
  required: true
  description: Unit system for input (UCUM codes: metric, imperial)

## 📂 Output (TOML-style)

[result]
  type: number
  description: BMI (rounded to 2 decimals)

[working]
  type: string
  description: Step-by-step calculation

[interpretation]
  type: string
  enum: ["Underweight", "Normal", "Overweight", "Obese"]
  description: WHO-based classification

[reference]
  type: string
  default: "WHO 2023 Guidelines"

[metadata]
  type: object
  fields:
    timestamp: string (ISO8601)
    version: string (e.g., "1.0")
    calculator_name: string

## 📂 Validation Rules
- Height must be > 0 and ≤ 3 m (or 118 in)
- Weight must be > 0 and ≤ 500 kg (or 1100 lb)
- unit_system must be one of: metric, imperial

## 📂 Usage (CLI or API)

CLI: 
  calc bmi --weight 70 --height 1.75 --unit-system metric

API:
  POST /calculate
  {
    "calculator": "bmi",
    "params": {
      "weight": 70,
      "height": 1.75,
      "unit_system": "metric"
    }
  }

"""

from __future__ import annotations

from typing import Literal

# Import the generic CalculationResponse
from core.response.response import CalculationResponse


from pydantic import Field, root_validator
from core.request.request import CalculatorRequest

from core.metadata import build_metadata



class BMIRequest(CalculatorRequest):
  # Place unit_system first so validation can depend on it
  unit_system: Literal["metric", "imperial"]
  weight: float = Field(..., gt=0, description="Weight in kg or lb (UCUM)")
  height: float = Field(..., gt=0, description="Height in m or in (UCUM)")

  @root_validator
  def validate_ranges(cls, values):
    unit = values.get("unit_system")
    w = values.get("weight")
    h = values.get("height")
    if unit == "metric":
      if w is not None and not (0 < w <= 500):
        raise ValueError("weight (kg) must be in (0, 500]")
      if h is not None and not (0 < h <= 3.0):
        raise ValueError("height (m) must be in (0, 3.0]")
    elif unit == "imperial":
      if w is not None and not (0 < w <= 1100):
        raise ValueError("weight (lb) must be in (0, 1100]")
      if h is not None and not (0 < h <= 118):
        raise ValueError("height (in) must be in (0, 118]")
    else:
      raise ValueError("unit_system must be one of: metric, imperial")
    return values





def _classify_bmi(bmi: float) -> Literal["Underweight", "Normal", "Overweight", "Obese"]:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def calculate(params: BMIRequest | dict) -> CalculationResponse:
  """Calculate BMI from request parameters.

  Accepts either a BMIRequest or a plain dict (which will be validated).
  """
  req = params if isinstance(params, BMIRequest) else BMIRequest(**params)
  if req.unit_system == "imperial":
    weight_kg = req.weight * 0.45359237
    height_m = req.height * 0.0254
  else:
    weight_kg = req.weight
    height_m = req.height

  bmi = round(weight_kg / (height_m ** 2), 2)
  interp = _classify_bmi(bmi)
  working = {
    "description": f"Weight: {weight_kg:.2f} kg, Height: {height_m:.2f} m → BMI = {bmi:.2f}"
  }
  return CalculationResponse(
    result=bmi,
    working=working,
    interpretation=interp,
    reference="WHO 2023 Guidelines",
    metadata=build_metadata("bmi"),
  )
