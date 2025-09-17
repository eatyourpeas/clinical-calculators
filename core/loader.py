from __future__ import annotations

import importlib
import importlib.util
import inspect
import io
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


_INSTALL_CACHE: set[str] = set()


@dataclass
class CalculatorSpec:
    name: str
    doc_config: str


class DependencyError(Exception):
    """Raised when calculator-declared dependencies cannot be installed."""

    def __init__(self, missing: List[str], calculator: Optional[str] = None, detail: Optional[str] = None):
        self.missing = missing
        self.calculator = calculator
        self.detail = detail
        calc = f" for calculator '{calculator}'" if calculator else ""
        msg = f"Failed to install dependencies{calc}: {missing}"
        if detail:
            msg += f"\n{detail}"
        super().__init__(msg)


def _find_calculator_file(name: str) -> Optional[str]:
    """Return absolute path to the calculator module file without importing it."""
    spec = importlib.util.find_spec(f"calculators.{name}")
    if not spec or not spec.origin:
        return None
    return spec.origin


def _read_top_docstring(source_text: str) -> str:
    """Extract the first triple-quoted docstring content from a source file."""
    m = re.search(r"^[\s\n]*([\"\']{3})([\s\S]*?)\1", source_text)
    return m.group(2).strip() if m else ""


def _parse_dependencies_from_doc(doc: str) -> List[str]:
    """Parse a [dependencies] block from the docstring and return packages.

    Supported formats within the block (until next [section] or blank line boundary):
    - one per line: `scipy` or with version `pydantic>=1.10,<2`
    - bullet lines: `- numpy` or `* numpy`
    - comma-separated list: `numpy, pandas`
    """
    if not doc:
        return []
    lines = doc.splitlines()
    deps: List[str] = []
    in_block = False
    for raw in lines:
        line = raw.strip()
        if not in_block:
            if line.lower().startswith("[dependencies]"):
                in_block = True
            continue
        # inside dependencies block
        if not line:
            # stop at blank separating blocks
            if deps:
                break
            else:
                continue
        if re.match(r"^\[[^\]]+\]", line):
            # next section reached
            break
        # normalize bullets
        line = re.sub(r"^[-*]\s+", "", line)
        # Split comma-separated values
        parts = [p.strip() for p in line.split(",") if p.strip()]
        deps.extend(parts)
    # Deduplicate while preserving order
    seen: set[str] = set()
    result: List[str] = []
    for d in deps:
        if d not in seen:
            seen.add(d)
            result.append(d)
    return result


def _ensure_dependencies_installed(packages: List[str], calculator_name: Optional[str] = None) -> None:
    """Ensure the given packages are installed. Installs missing ones via pip.

    This performs a best-effort check using importlib.util.find_spec for top-level
    module names (derived from the package string up to the first non-module char).
    It then runs a single `python -m pip install ...` for missing packages.
    """
    if not packages:
        return
    missing: List[str] = []
    for pkg in packages:
        if pkg in _INSTALL_CACHE:
            continue
        # derive a plausible module name from the package spec (before [<=> ])
        modname = re.split(r"[<>!=\[ ]", pkg, maxsplit=1)[0].strip().replace("-", "_")
        try:
            found = importlib.util.find_spec(modname) is not None
        except Exception:
            found = False
        if not found:
            missing.append(pkg)
        else:
            _INSTALL_CACHE.add(pkg)

    if not missing:
        return

    # Install all missing in one call
    cmd = [sys.executable, "-m", "pip", "install", *missing]
    try:
        subprocess.check_call(cmd)
        for pkg in missing:
            _INSTALL_CACHE.add(pkg)
    except subprocess.CalledProcessError as e:
        raise DependencyError(missing, calculator=calculator_name, detail=str(e))


def _read_doc_config_without_import(name: str) -> str:
    path = _find_calculator_file(name)
    if not path or not os.path.isfile(path):
        return ""
    with io.open(path, "r", encoding="utf-8") as f:
        src = f.read()
    return _read_top_docstring(src)


def load_calculator_module(name: str):
    """Import a calculator module by name from the calculators package.

    Ensures any docstring-declared [dependencies] are installed first to avoid
    import errors when calculators import optional libraries at module scope.
    """
    # Try reading docstring without importing to get dependencies early
    doc_pre = _read_doc_config_without_import(name)
    deps = _parse_dependencies_from_doc(doc_pre)
    _ensure_dependencies_installed(deps, calculator_name=name)

    mod_name = f"calculators.{name}"
    return importlib.import_module(mod_name)


def get_doc_config(module) -> str:
    """Return the top-level docstring which contains TOML-like spec.

    If absent, returns an empty string.
    """
    doc = inspect.getdoc(module) or ""
    return doc


def get_calculator_spec(name: str) -> Optional[CalculatorSpec]:
    # Read doc without importing to avoid dependency issues
    doc_pre = _read_doc_config_without_import(name)
    if not doc_pre:
        # Fall back to importing (may still work) to get a docstring
        try:
            mod = load_calculator_module(name)
            return CalculatorSpec(name=name, doc_config=get_doc_config(mod))
        except ModuleNotFoundError:
            return None
    return CalculatorSpec(name=name, doc_config=doc_pre)


def available_calculators() -> Dict[str, str]:
    """Return a mapping of calculator names to their titles from docstrings.

    This does not guarantee that calculators are valid, only that they exist.
    """
    import pkgutil
    import calculators

    results: Dict[str, str] = {}
    for m in pkgutil.iter_modules(calculators.__path__):  # type: ignore[attr-defined]
        name = m.name
        try:
            # Prefer reading doc without import
            doc = _read_doc_config_without_import(name)
            title = doc.splitlines()[0] if doc else name
        except Exception:
            title = name
        results[name] = title
    return results
