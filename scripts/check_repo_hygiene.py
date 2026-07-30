#!/usr/bin/env python3
"""Fail when large transient artifacts are tracked at the repository root.

Catches the recurring pattern of agent session dumps (``*test.md``) and
binary archives (``*.tar.gz``) being committed into the main repo. These
belong outside the repo or in ``.gitignore``. Only tracked files are
flagged, so local-only scratch files do not trigger a failure.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Root-level glob patterns that should never be tracked.
FORBIDDEN_SUFFIXES = (".tar.gz",)
# Agent session dumps follow a ``<model>-test.md`` / ``<model>_test.md`` naming.
FORBIDDEN_NAME_CONTAINS = ("test.md",)


def _tracked_root_files() -> list[str]:
    """Return tracked files that live directly at the repo root (depth 1)."""
    try:
        out = subprocess.check_output(
            ["git", "-C", str(ROOT), "ls-files", "--cached", "--full-name"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not a git repo or git unavailable: nothing to flag.
        return []
    return [line for line in out.splitlines() if line and "/" not in line]


def main() -> int:
    offenders: list[str] = []
    for name in _tracked_root_files():
        lower = name.lower()
        if lower.endswith(FORBIDDEN_SUFFIXES):
            offenders.append(name)
            continue
        if any(tag in lower for tag in FORBIDDEN_NAME_CONTAINS):
            offenders.append(name)

    if offenders:
        print(
            "Transient artifacts tracked at repo root (remove via `git rm` and add to .gitignore):",
            file=sys.stderr,
        )
        for name in offenders:
            print(f"  {name}", file=sys.stderr)
        print(
            "Agent session dumps and archives belong outside the repo. "
            "See .gitignore root-pattern section.",
            file=sys.stderr,
        )
        return 1

    print("repo_hygiene_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
