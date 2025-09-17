from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict


PACKAGE_VERSION = os.environ.get("CLINICAL_CALCULATORS_VERSION", "0.1.0")


def build_metadata(calculator_name: str) -> Dict[str, Any]:
    """Return common metadata for responses.

    Includes ISO8601 timestamp (UTC), version, and calculator name.
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": PACKAGE_VERSION,
        "calculator_name": calculator_name,
    }
