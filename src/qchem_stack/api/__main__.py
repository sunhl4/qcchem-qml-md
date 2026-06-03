"""Run the optional FastAPI service: ``python -m qchem_stack.api``."""

from __future__ import annotations

import argparse
import os


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="qchem-stack HTTP API (FastAPI + uvicorn).")
    ap.add_argument("--host", default=os.environ.get("QCHEM_API_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("QCHEM_API_PORT", "8000")))
    ap.add_argument(
        "--db",
        type=str,
        default=os.environ.get("QCHEM_JOB_DB", "/data/jobs.sqlite"),
        help="SQLite job database path (used by run routes)",
    )
    args = ap.parse_args(argv)
    if args.db:
        os.environ.setdefault("QCHEM_JOB_DB", args.db)
    import uvicorn

    uvicorn.run(
        "qchem_stack.api.app:app",
        host=args.host,
        port=args.port,
        log_level=os.environ.get("QCHEM_API_LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    main()
