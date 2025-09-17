from pydantic import BaseModel
from typing import Optional, Dict, Any

class CalculatorRequest(BaseModel):
    """
    Base class for all calculator request models.
    Subclass this in each calculator to define specific input fields and validation.
    Optionally provides a place for shared metadata or methods.
    """
    # Optionally, common metadata or methods can be added here
    metadata: Optional[Dict[str, Any]] = None
