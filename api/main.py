from __future__ import annotations

from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
import markdown as md
import json

from core.loader import (
    available_calculators,
    load_calculator_module,
    DependencyError,
    get_calculator_spec,
    parse_inputs_spec,
)

app = FastAPI(title="Clinical Calculators API", summary="Clinical calculators, standardised and reusable.", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home():
        return HTMLResponse(
                """
                <!DOCTYPE html>
                <html lang=\"en\">
                    <head>
                        <meta charset=\"utf-8\" />
                        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
                        <title>Clinical Calculators</title>
                        <style>
                            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 2rem auto; max-width: 900px; padding: 0 1rem; }
                            a { color: #0969da; text-decoration: none; }
                            a:hover { text-decoration: underline; }
                            ul { line-height: 1.8; }
                        </style>
                    </head>
                    <body>
                        <h1>Clinical Calculators</h1>
                        <p>Welcome! Choose where to go:</p>
                        <ul>
                            <li><a href=\"/docs\">Swagger UI</a> (interactive API docs)</li>
                            <li><a href=\"/redoc\">ReDoc</a> (alternative API docs)</li>
                            <li><a href=\"/openapi.json\">OpenAPI JSON</a></li>
                            <li><a href=\"/docs/calculators\">Calculators documentation index</a></li>
                            <li><a href=\"/calculators\">List calculators (JSON)</a></li>
                        </ul>
                    </body>
                </html>
                """
        )


@app.get("/calculators")
def list_calculators():
    return available_calculators()


@app.get("/calculators/{name}/doc")
def calculator_doc(name: str):
    spec = get_calculator_spec(name)
    if not spec:
        raise HTTPException(status_code=404, detail=f"Calculator '{name}' not found")
    return {"name": name, "doc": spec.doc_config}


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


@app.get("/calculators/{name}/doc.html", response_class=HTMLResponse)
def calculator_doc_html(name: str):
        spec = get_calculator_spec(name)
        if not spec:
                raise HTTPException(status_code=404, detail=f"Calculator '{name}' not found")
        body_md = spec.doc_config or f"# {name}\n\nNo documentation available."
        body_html = md.markdown(body_md, extensions=["fenced_code", "tables", "toc"])
        html = f"""
        <!DOCTYPE html>
        <html lang=\"en\">
            <head>
                <meta charset=\"utf-8\" />
                <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
                <title>{name} – Clinical Calculator Docs</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 2rem auto; max-width: 900px; padding: 0 1rem; }}
                    pre {{ background: #0d1117; color: #c9d1d9; padding: 1rem; overflow: auto; border-radius: 6px; }}
                    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; }}
                    table {{ border-collapse: collapse; width: 100%; }}
                    th, td {{ border: 1px solid #ccc; padding: 0.5rem; text-align: left; }}
                    h1, h2, h3 {{ line-height: 1.2; }}
                    .container {{ display: block; }}
                </style>
            </head>
            <body>
                <div class=\"container\">{body_html}</div>
            </body>
        </html>
        """
        return HTMLResponse(html)


@app.get("/docs/calculators", response_class=HTMLResponse)
def calculators_docs_index():
    calcs = available_calculators()
    items = "\n".join(
        f"<li><strong>{name}</strong> — {title} [<a href='/calculators/{name}/doc.html'>docs</a>] [<a href='/calculators/{name}/form'>form</a>]</li>"
        for name, title in sorted(calcs.items(), key=lambda x: x[0])
    )
    html = f"""
        <!DOCTYPE html>
        <html lang=\"en\">
            <head>
                <meta charset=\"utf-8\" />
                <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
                <title>Clinical Calculators – Docs Index</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 2rem auto; max-width: 900px; padding: 0 1rem; }}
                    h1 {{ margin-bottom: 1rem; }}
                    ul {{ line-height: 1.8; }}
                    a {{ text-decoration: none; color: #0969da; }}
                    a:hover {{ text-decoration: underline; }}
                </style>
            </head>
            <body>
                <h1>Clinical Calculators – Documentation</h1>
                <p>Click a calculator to view its documentation:</p>
                <ul>
                    {items}
                </ul>
            </body>
        </html>
        """
    return HTMLResponse(html)


@app.get("/calculators/{name}/form", response_class=HTMLResponse)
def calculator_form(name: str):
        spec = get_calculator_spec(name)
        if not spec:
            raise HTTPException(status_code=404, detail=f"Calculator '{name}' not found")
        fields = parse_inputs_spec(spec.doc_config)
        def input_control(f: Dict[str, Any]) -> str:
            label = f.get("description") or f.get("name")
            fname = f.get("name")
            ftype = (f.get("type") or "string").lower()
            required = "required" if f.get("required") else ""
            placeholder = f.get("unit") or ""
            if isinstance(f.get("enum"), list) and f["enum"]:
                opts = "".join(f"<option value='{opt}'>{opt}</option>" for opt in f["enum"])
                return f"<label>{label}: <select name='{fname}' {required}>{opts}</select></label>"
            input_type = "number" if ftype in {"number", "float", "int"} else "text"
            min_attr = f" min='{f['min']}'" if isinstance(f.get("min"), (int, float)) else ""
            max_attr = f" max='{f['max']}'" if isinstance(f.get("max"), (int, float)) else ""
            step_attr = " step='any'" if input_type == "number" else ""
            return f"<label>{label}: <input name='{fname}' type='{input_type}' placeholder='{placeholder}' {required}{min_attr}{max_attr}{step_attr}></label>"
        controls = "<br>\n".join(input_control(f) for f in fields)
        html = f"""
        <!DOCTYPE html>
        <html lang=\"en\"><head>
          <meta charset=\"utf-8\" />
          <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
          <title>{name} – Form</title>
        </head><body>
          <h1>{name} – Calculator</h1>
          <form method=\"post\" action=\"/calculators/{name}/submit\">
            {controls}
            <br><br>
            <button type=\"submit\">Calculate</button>
          </form>
          <p>Docs: <a href=\"/calculators/{name}/doc.html\">View documentation</a></p>
        </body></html>
        """
        return HTMLResponse(html)


@app.post("/calculators/{name}/submit", response_class=HTMLResponse)
async def calculator_submit(name: str, request: Request):
    # Accept form or JSON payload and coerce simple numeric types
    try:
        ctype = request.headers.get("content-type", "")
        if "application/json" in ctype:
            params: Dict[str, Any] = await request.json()
        else:
            form = await request.form()
            params = {k: v for k, v in form.items()}

        spec = get_calculator_spec(name)
        if not spec:
            return HTMLResponse(f"<pre>Calculator '{name}' not found</pre>", status_code=404)

        fields = parse_inputs_spec(spec.doc_config or "")
        numeric_names: set[str] = set()
        for f in fields:
            ftype = str(f.get("type", "")).lower()
            fname = f.get("name")
            if fname and ftype in {"number", "float", "int"}:
                numeric_names.add(fname)

        for k, v in list(params.items()):
            if k in numeric_names:
                try:
                    params[k] = float(v)  # best-effort float coercion
                except Exception:
                    pass
    except Exception as e:
        return HTMLResponse(f"<pre>Unexpected error while reading input: {str(e)}</pre>", status_code=500)

    try:
        mod = load_calculator_module(name)
    except ModuleNotFoundError:
        return HTMLResponse(f"<pre>Calculator '{name}' not found</pre>", status_code=404)
    except DependencyError as de:
        return HTMLResponse(f"<pre>{str(de)}</pre>", status_code=424)

    try:
        resp = mod.calculate(params)  # type: ignore[attr-defined]
        data = resp.dict() if hasattr(resp, "dict") else resp
        body = json.dumps(data, indent=2, ensure_ascii=False)
        return HTMLResponse(f"<pre>{body}</pre>")
    except Exception as e:
        return HTMLResponse(f"<pre>Error: {str(e)}</pre>", status_code=400)
