#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Re-encode project text files to UTF-8 (no BOM).

Use when WSL / pip reports UnicodeDecodeError because files were saved as
GBK/GB18030 on Windows. Skips .git, .venv*, node_modules, etc.

Usage::

    python3 scripts/normalize_repo_text_utf8.py --dry-run
    python3 scripts/normalize_repo_text_utf8.py
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

TEXT_SUFFIXES = frozenset(
    {".md", ".toml", ".py", ".yaml", ".yml", ".json", ".txt", ".cfg", ".ini", ".rst"}
)
SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        ".venv",
        ".tox",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        ".vitepress",
    }
)

FALLBACK_ENCODINGS = ("gb18030", "gbk", "cp936")


def _decode_as_utf8(data: bytes) -> str | None:
    for sig in ("utf-8-sig", "utf-8"):
        try:
            return data.decode(sig)
        except UnicodeDecodeError:
            continue
    return None


def _decode_with_fallback(data: bytes) -> tuple[str, str] | None:
    for enc in FALLBACK_ENCODINGS:
        try:
            return data.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return None


def _skip_dir(name: str) -> bool:
    if name in SKIP_DIR_NAMES:
        return True
    return name.startswith(".venv")


def _iter_candidate_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = sorted(d for d in dirnames if not _skip_dir(d))
        base = Path(dirpath)
        for name in sorted(filenames):
            out.append(base / name)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Normalize text files under repo root to UTF-8.")
    ap.add_argument(
        "root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Repo root (default: parent of this script)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Print actions only, do not write.")
    args = ap.parse_args()
    root: Path = args.root.resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2

    changed: list[tuple[Path, str]] = []
    failed: list[Path] = []
    skipped_ok: int = 0

    for path in _iter_candidate_files(root):
        try:
            if not path.is_file():
                continue
        except OSError:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if not data:
            skipped_ok += 1
            continue

        if b"\x00" in data:
            failed.append(path)
            continue

        text_utf8 = _decode_as_utf8(data)
        if text_utf8 is not None:
            out = text_utf8.encode("utf-8")
            if out != data:
                changed.append((path, "utf-8-sig->utf-8"))
                if not args.dry_run:
                    path.write_bytes(out)
            else:
                skipped_ok += 1
            continue

        decoded = _decode_with_fallback(data)
        if decoded is None:
            failed.append(path)
            continue
        text, enc = decoded
        out = text.encode("utf-8")
        changed.append((path, enc))
        if not args.dry_run:
            path.write_bytes(out)

    prefix = "[dry-run] " if args.dry_run else ""
    for p, enc in changed:
        print(f"{prefix}UTF-8 from {enc}: {p.relative_to(root)}")
    for p in failed:
        print(f"FAILED: {p.relative_to(root)}", file=sys.stderr)

    print(
        f"Done: {len(changed)} would change / changed, "
        f"{skipped_ok} already UTF-8, {len(failed)} failed.",
        file=sys.stderr,
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
