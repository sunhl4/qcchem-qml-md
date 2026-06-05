#!/usr/bin/env python3
"""CLI wrapper for parity / Methods export (implementation in qchem_stack.protocols)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from qchem_stack.protocols.parity_criteria_export import export_parity_criteria_table


def main() -> None:
    ap = argparse.ArgumentParser(description="Export parity / falsifiability table fields.")
    ap.add_argument("config", type=Path, help="Experiment YAML path")
    ap.add_argument("--results", type=Path, default=None, help="Optional JSON with pipeline output")
    ap.add_argument(
        "--max-pauli-export",
        type=int,
        default=None,
        metavar="N",
        help="If set with --results, cap exported hamiltonian_pauli_strings mirror list length",
    )
    args = ap.parse_args()
    out = export_parity_criteria_table(
        args.config,
        results_path=args.results,
        max_pauli_export=args.max_pauli_export,
    )
    json.dump(out, sys.stdout, indent=2, sort_keys=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
