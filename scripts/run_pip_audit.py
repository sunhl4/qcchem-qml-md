#!/usr/bin/env python3
"""Run pip-audit; optionally apply ignore list from pip-audit.toml.

Usage:
  python scripts/run_pip_audit.py              # with pip-audit.toml allowlist
  python scripts/run_pip_audit.py --no-allowlist
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]


def _ignore_vuln_ids() -> list[str]:
    cfg_path = ROOT / "pip-audit.toml"
    if not cfg_path.is_file():
        return []
    data = tomllib.loads(cfg_path.read_text(encoding="utf-8"))
    raw = data.get("pip-audit", {}).get("ignore-vuln", [])
    return [str(v) for v in raw]


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    use_allowlist = True
    if "--no-allowlist" in args:
        use_allowlist = False
        args = [a for a in args if a != "--no-allowlist"]
    cmd = ["pip-audit", "--skip-editable", "--desc", "on", *args]
    if use_allowlist:
        for vuln_id in _ignore_vuln_ids():
            cmd.extend(["--ignore-vuln", vuln_id])
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
