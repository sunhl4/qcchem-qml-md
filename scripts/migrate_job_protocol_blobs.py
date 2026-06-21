#!/usr/bin/env python3
"""Scan SQLite job store for legacy unsigned protocol pickles (dry-run by default)."""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path


def _classify_blob(blob: bytes) -> str:
    if not blob:
        return "empty"
    if blob[:1] == b"\x80":
        return "legacy_unsigned_pickle"
    if len(blob) >= 32:
        payload = blob[32:]
        try:
            doc = json.loads(payload.decode("utf-8"))
            if isinstance(doc, dict) and doc.get("protocol_blob_version") == 2:
                return "signed_json_v2"
        except (UnicodeDecodeError, json.JSONDecodeError):
            pass
        return "signed_pickle_v1"
    try:
        json.loads(blob.decode("utf-8"))
        return "unsigned_json_v2"
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "unknown"
    return "unknown"


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
        rows = conn.execute("SELECT id, payload FROM jobs WHERE payload IS NOT NULL").fetchall()
    except sqlite3.OperationalError as exc:
        print(f"Could not query jobs table: {exc}", file=sys.stderr)
        return 1
    finally:
        conn.close()

    counts: dict[str, int] = {}
    for _id, blob in rows:
        kind = _classify_blob(blob if isinstance(blob, bytes) else b"")
        counts[kind] = counts.get(kind, 0) + 1

    print(f"jobs with payload: {len(rows)}")
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}")
    legacy = counts.get("legacy_unsigned_pickle", 0)
    if legacy:
        print(
            f"action: {legacy} legacy unsigned pickle row(s); "
            "drain worker with QCHEM_ALLOW_LEGACY_PICKLE=1 then re-enqueue",
            file=sys.stderr,
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
