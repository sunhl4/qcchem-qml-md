#!/usr/bin/env python3
"""Optional PySCF vs Psi4 closed-shell HF energy baseline (writes JSON to stdout).

Requires ``chem`` extras for PySCF. Psi4 is detected at runtime via ``import psi4``:
when missing, rows still report finite PySCF energies and ``psi4_skip_reason``.
"""

from __future__ import annotations

import argparse
import json

from qchem_stack.integrations.cross_solver_parity import build_cross_solver_parity_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--atol",
        type=float,
        default=5e-4,
        help="Absolute Hartree tolerance for PySCF vs Psi4 when Psi4 runs (default: 5e-4).",
    )
    args = parser.parse_args()
    report = build_cross_solver_parity_report(atol=float(args.atol))
    print(json.dumps(report, indent=2, sort_keys=True))
    summary = report.get("summary") or {}
    aw = summary.get("all_within_atol")
    if summary.get("psi4_installed") and aw is False:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
