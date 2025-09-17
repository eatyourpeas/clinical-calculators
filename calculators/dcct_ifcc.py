"""
# DCCT/IFCC Converter

## 📂 Configuration (TOML-style in docstring)

[inputs]
- name: value
  type: number
  required: true
  description: Value to convert (either DCCT % or IFCC mmol/mol)
- name: input_unit
  type: string
  enum: ["dcct", "ifcc"]
  required: true
  description: Input unit: 'dcct' for DCCT (%), 'ifcc' for IFCC (mmol/mol)

## 📂 Output (TOML-style)

[result]
  type: number
  description: Converted value

[working]
  type: string
  description: Step-by-step calculation

[interpretation]
  type: string
  description: Conversion summary

[reference]
  type: string
  default: "NGSP/IFCC 2023 Guidelines"

[metadata]
  type: object
  fields:
    timestamp: string (ISO8601)
    version: string (e.g., "1.0")
    calculator_name: string

## 📂 Validation Rules
- value must be > 0
- input_unit must be one of: dcct, ifcc

"""

from __future__ import annotations
from typing import Literal
from core.response.response import CalculationResponse
from pydantic import Field, root_validator
from core.request.request import CalculatorRequest
from core.metadata import build_metadata

class DCCTIFCCRequest(CalculatorRequest):
  input_unit: Literal["dcct", "ifcc"]
  value: float = Field(..., gt=0, description="Value to convert")

  @root_validator
  def validate_ranges(cls, values):
    unit = values.get("input_unit")
    v = values.get("value")
    if unit not in ("dcct", "ifcc"):
      raise ValueError("input_unit must be one of: dcct, ifcc")
    if v is None or v <= 0:
      raise ValueError("value must be > 0")
    if unit == "dcct" and v > 20:
      raise ValueError("DCCT value must be ≤ 20%")
    if unit == "ifcc" and v > 200:
      raise ValueError("IFCC value must be ≤ 200 mmol/mol")
    return values


def calculate(params: DCCTIFCCRequest | dict) -> CalculationResponse:
  """Convert between DCCT (%) and IFCC (mmol/mol)."""
  req = params if isinstance(params, DCCTIFCCRequest) else DCCTIFCCRequest(**params)
  if req.input_unit == "dcct":
    # DCCT (%) to IFCC (mmol/mol): IFCC = (DCCT - 2.15) × 10.929
    result = round((req.value - 2.15) * 10.929, 2)
    working = {
      "formula": "IFCC = (DCCT - 2.15) × 10.929",
      "calculation": f"({req.value} - 2.15) × 10.929 = {result} mmol/mol"
    }
    interpretation = f"{req.value}% DCCT = {result} mmol/mol IFCC: {normal_range(result, 'ifcc')}"
  else:
    # IFCC (mmol/mol) to DCCT (%): DCCT = (IFCC / 10.929) + 2.15
    result = round((req.value / 10.929) + 2.15, 2)
    working = {
      "formula": "DCCT = (IFCC / 10.929) + 2.15",
      "calculation": f"({req.value} / 10.929) + 2.15 = {result}%"
    }
    interpretation = f"{req.value} mmol/mol IFCC = {result}% DCCT: {normal_range(result, 'dcct')}"
  return CalculationResponse(
    result=result,
    working=working,
    interpretation=interpretation,
    reference="NGSP/IFCC 2023 Guidelines",
    metadata=build_metadata("dcct_ifcc"),
    tags=["dcct", "ifcc", "hba1c", "conversion"]
  )

def normal_range(value: float, unit: str) -> str:
  """Return interpretation of the result."""
  if unit == "dcct":
    if value <= 6:
      return "Normal"
    elif value < 6.5:
      return "Prediabetes"
    else:
      return "Diabetes"
  elif unit == "ifcc":
    if value < 42:
      return "Normal"
    elif value < 48:
      return "Prediabetes"
    else:
      return "Diabetes"
  return "Unknown"
