"""Rough counts for ledger §3 metrics (main parity tables §1–3 only)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def classify(cell: str) -> str:
    """Primary badge is usually the first backtick status on the qchem_stack cell."""
    s = cell.strip()
    if s.startswith("`yes`") or "`yes`：" in s[:48]:
        return "yes"
    if s.startswith("`partial`") or "`partial`：" in s[:48] or s.startswith("partial`→"):
        return "partial"
    if s.startswith("`n/a`") or "`n/a`" in s[:24]:
        return "n/a"
    if "`no`" in s[:12]:
        return "no"
    if "`partial`" in s or "`partial" in s:
        return "partial"
    if "`n/a`" in s:
        return "n/a"
    if "`yes`" in s:
        return "yes"
    return "other"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[1]
    text = (root / "docs" / "inquanto_public_parity_matrix.md").read_text(encoding="utf-8")
    chunk = text.split("## 4.", 1)[0]
    if "## 1." in chunk:
        chunk = chunk.split("## 1.", 1)[1]
    lines = [
        ln
        for ln in chunk.splitlines()
        if ln.strip().startswith("|") and "---" not in ln and ln.count("|") >= 3
    ]
    yes = partial = na = no = other = 0
    skip_headers = {"公开能力", "公开类", "能力", "备注", "qchem_stack"}
    for ln in lines:
        parts = [p.strip() for p in ln.split("|")]
        if len(parts) < 4:
            continue
        col1 = parts[1]
        col2 = parts[2]
        if col1 in skip_headers or col2 in skip_headers:
            continue
        # §1: | key | official_link | qchem | ; §2 two-col: | Algorithm | qchem |
        # §3: | capability | qchem | remark |
        if "Algorithm" in col1 or col1.startswith("`Algorithm"):
            cell = parts[2]
        elif (
            "http" in col2
            or "docs.quantinuum.com" in col2
            or col2 in ("同上", "—")
            or col2.startswith("[")
        ):
            cell = parts[3]
        else:
            cell = parts[2]
        if classify(cell) == "other" and len(parts) > 4:
            alt = parts[3] if cell == parts[2] else parts[2]
            if classify(alt) != "other":
                cell = alt
        s = classify(cell)
        if s == "yes":
            yes += 1
        elif s == "partial":
            partial += 1
        elif s == "n/a":
            na += 1
        elif s == "no":
            no += 1
        else:
            other += 1
            if args.verbose:
                print(f"OTHER {col1[:50]} :: {cell[:120]}", file=sys.stderr)
    print(f"main_table_rows={len(lines)} yes={yes} partial={partial} n/a={na} no={no} other={other}")


if __name__ == "__main__":
    main()
