#!/usr/bin/env python3
"""Scan SQLite job store for legacy unsigned protocol pickles (dry-run by default)."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, required=True, help="SQLite job database path")
    ap.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite blobs with HMAC (requires QCHEM_PROTOCOL_HMAC_KEY)",
    )
    args = ap.parse_args()
    if not args.db.is_file():
        print(f"Database not found: {args.db}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(args.db)
    try:
        rows = conn.execute(
            "SELECT id, length(payload) FROM jobs WHERE payload IS NOT NULL"
        ).fetchall()
    except sqlite3.OperationalError as exc:
        print(f"Could not query jobs table: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    legacy = sum(1 for _id, blob in rows if blob and blob[:1] == b"\x80")
    signed = len(rows) - legacy
    print(
        f"jobs with payload: {len(rows)} (signed_or_unknown={signed}, legacy_pickle_heuristic={legacy})"
    )
    if args.apply:
        print(
            "Apply mode: re-run jobs via qchem-jobs-worker or re-enqueue; "
            "automatic blob rewrite is not implemented in this script.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
