from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException

from core.loader import available_calculators, load_calculator_module, DependencyError

app = FastAPI(title="Clinical Calculators API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/calculators")
def list_calculators():
    return available_calculators()


@app.post("/calculate")
def calculate(payload: Dict[str, Any]):
    name = payload.get("calculator")
    params = payload.get("params", {})
    if not name:
        raise HTTPException(status_code=400, detail="Missing 'calculator' in payload")

    try:
        mod = load_calculator_module(name)
    except ModuleNotFoundError:
        raise HTTPException(status_code=404, detail=f"Calculator '{name}' not found")
    except DependencyError as de:
        # 424 Failed Dependency conveys installation issue
        raise HTTPException(status_code=424, detail=str(de))

    if not hasattr(mod, "calculate"):
        raise HTTPException(status_code=500, detail=f"Calculator '{name}' missing calculate()")

    try:
        resp = mod.calculate(params)  # type: ignore[attr-defined]
        return resp.dict() if hasattr(resp, "dict") else resp
    except Exception as e:  # validation errors surfaced as 400
        raise HTTPException(status_code=400, detail=str(e))
