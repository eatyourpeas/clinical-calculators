from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from core.loader import available_calculators, load_calculator_module


def run_list(_: argparse.Namespace) -> int:
    calcs = available_calculators()
    for name, title in calcs.items():
        print(f"{name}\t{title}")
    return 0


def run_calc(ns: argparse.Namespace) -> int:
    name: str = ns.calculator
    params_str: str | None = ns.params
    if params_str:
        try:
            params: Dict[str, Any] = json.loads(params_str)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON for --params: {e}", file=sys.stderr)
            return 2
    else:
        params = {}

    try:
        mod = load_calculator_module(name)
    except ModuleNotFoundError:
        print(f"Calculator '{name}' not found", file=sys.stderr)
        return 1

    if not hasattr(mod, "calculate"):
        print(f"Calculator '{name}' has no calculate() function", file=sys.stderr)
        return 1

    result = mod.calculate(params)  # type: ignore[attr-defined]
    # pydantic BaseModel has .json(); if simple dict, dump directly
    try:
        print(result.json())
    except AttributeError:
        print(json.dumps(result, ensure_ascii=False))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="clinical-calculators", description="Clinical calculators CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List available calculators")
    p_list.set_defaults(func=run_list)

    p_calc = sub.add_parser("run", help="Run a calculator by name")
    p_calc.add_argument("calculator", help="Calculator name (e.g., bmi)")
    p_calc.add_argument("--params", help="JSON object with parameters", required=False)
    p_calc.set_defaults(func=run_calc)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    return ns.func(ns)


if __name__ == "__main__":
    raise SystemExit(main())
