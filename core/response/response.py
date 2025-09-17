from pydantic import BaseModel, Field
from typing import Any, Dict, Optional

class CalculationResponse(BaseModel):
    result: Any = Field(..., description="The main result of the calculation.")
    working: Optional[Dict[str, Any]] = Field(None, description="Intermediate calculation steps or details.")
    interpretation: Optional[str] = Field(None, description="Interpretation of the result.")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata about the calculation.")
    reference: Optional[str] = Field(None, description="Reference or source for the calculation.")
