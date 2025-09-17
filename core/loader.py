from __future__ import annotations

import importlib
import inspect
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional


DOC_TOML_START = re.compile(r"^\"\"\"", re.MULTILINE)


@dataclass
class CalculatorSpec:
    name: str
    doc_config: str


def load_calculator_module(name: str):
    """Import a calculator module by name from the calculators package.

    Example: name="bmi" loads calculators.bmi
    """
    mod_name = f"calculators.{name}"
    return importlib.import_module(mod_name)


def get_doc_config(module) -> str:
    """Return the top-level docstring which contains TOML-like spec.

    If absent, returns an empty string.
    """
    doc = inspect.getdoc(module) or ""
    return doc


def get_calculator_spec(name: str) -> Optional[CalculatorSpec]:
    try:
        mod = load_calculator_module(name)
    except ModuleNotFoundError:
        return None
    doc_config = get_doc_config(mod)
    return CalculatorSpec(name=name, doc_config=doc_config)


def available_calculators() -> Dict[str, str]:
    """Return a mapping of calculator names to their titles from docstrings.

    This does not guarantee that calculators are valid, only that they exist.
    """
    # Lazy import pkgutil to avoid heavy startup
    import pkgutil
    import calculators

    results: Dict[str, str] = {}
    for m in pkgutil.iter_modules(calculators.__path__):  # type: ignore[attr-defined]
        name = m.name
        try:
            mod = load_calculator_module(name)
            title = (inspect.getdoc(mod) or "").splitlines()[0] if inspect.getdoc(mod) else name
        except Exception:
            title = name
        results[name] = title
    return results
