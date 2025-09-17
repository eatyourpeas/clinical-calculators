from __future__ import annotations

import sys

def main(argv: list[str] | None = None) -> int:
    """Convenience main dispatcher.

    - `python -m clinical_calculators` will run the CLI
    - `python main.py api` will start the API with uvicorn (dev use)
    """
    from cli.main import main as cli_main

    argv = argv if argv is not None else sys.argv[1:]
    if argv and argv[0] == "api":
        # Lazy import to avoid FastAPI/uvicorn cost when unused
        from uvicorn import run
        from api.main import app

        host = "0.0.0.0"
        port = 8000
        run(app, host=host, port=port, reload=True)
        return 0

    return cli_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
