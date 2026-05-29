#!/usr/bin/env python3
"""Minimal HTTP client for qchem-stack FastAPI runs API (P4-B18/B-19 / D-05)."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request
from pathlib import Path


def _request(method: str, url: str, body: dict | None = None) -> dict:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {detail}") from exc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base-url", default="http://127.0.0.1:8000")
    ap.add_argument(
        "--config", required=True, help="Experiment YAML text (inline) or path on server"
    )
    ap.add_argument("--project", default="tutorial")
    ap.add_argument("--workspace", default="default")
    ap.add_argument("--sync", action="store_true", help="Use deprecated sync path for local debug")
    args = ap.parse_args()

    base = args.base_url.rstrip("/")
    yaml_text = args.config
    if not yaml_text.lstrip().startswith("schema_version"):
        yaml_text = Path(args.config).read_text(encoding="utf-8")

    submit = _request(
        "POST",
        f"{base}/v1/runs{'/sync' if args.sync else ''}",
        {
            "experiment_yaml": yaml_text,
            "sync": bool(args.sync),
            "project_slug": args.project,
            "workspace_label": args.workspace,
        },
    )
    job_id = submit.get("job_id")
    if args.sync:
        repro = (submit.get("repro") or {}).get("run_summary") or {}
        print(
            json.dumps(
                {"submit_keys": list(submit.keys()), "run_summary_keys": sorted(repro.keys())},
                indent=2,
            )
        )
        return 0
    if not job_id:
        print(json.dumps(submit, indent=2))
        raise SystemExit("submit response missing job_id")

    for _ in range(30):
        status = _request("GET", f"{base}/v1/runs/{job_id}/status")
        if status.get("status") == "DONE":
            repro = _request("GET", f"{base}/v1/runs/{job_id}/repro")
            rs = (repro.get("repro") or {}).get("run_summary") or {}
            print(
                json.dumps(
                    {
                        "job_id": job_id,
                        "api_workspace_label": rs.get("api_workspace_label"),
                        "api_project_slug": rs.get("api_project_slug"),
                    },
                    indent=2,
                )
            )
            return 0
        if status.get("status") == "FAILED":
            raise SystemExit(json.dumps(status, indent=2))
        time.sleep(0.5)
    raise SystemExit("timeout waiting for job DONE")


if __name__ == "__main__":
    raise SystemExit(main())
