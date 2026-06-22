#!/usr/bin/env python3
"""Run pip-audit with ignore list from pip-audit.toml."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _ignore_vuln_ids() -> list[str]:
    cfg_path = ROOT / "pip-audit.toml"
    if not cfg_path.is_file():
        return []
    data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    raw = data.get("pip-audit", {}).get("ignore-vuln", [])
    return [str(v) for v in raw]


def main(argv: list[str] | None = None) -> int:
    cmd = ["pip-audit", "--skip-editable", "--desc", "on", *(argv or sys.argv[1:])]
    for vuln_id in _ignore_vuln_ids():
        cmd.extend(["--ignore-vuln", vuln_id])
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
