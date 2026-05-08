#!/usr/bin/env python3
"""Validate a solver adapter against the unified ChemIntegralSolver contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qchem_stack.chem.solvers import create_solver, validate_solver_adapter_contract
from qchem_stack.config import load_experiment_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "config",
        nargs="?",
        default="configs/example_h2.yaml",
        help="Experiment YAML path (default: configs/example_h2.yaml).",
    )
    parser.add_argument(
        "--driver",
        type=str,
        default=None,
        help="Override scf.driver before creating the solver (e.g. pyscf, psi4).",
    )
    parser.add_argument(
        "--run-mean-field",
        action="store_true",
        help="Run solver.compute_mean_field and validate runtime output shape.",
    )
    parser.add_argument(
        "--periodic",
        action="store_true",
        help="Use periodic=True when --run-mean-field is set.",
    )
    parser.add_argument(
        "--require-mean-field-success",
        action="store_true",
        help="Treat NotImplementedError from compute_mean_field as a hard failure.",
    )
    args = parser.parse_args()
    cfg_path = Path(args.config)
    cfg = load_experiment_config(cfg_path)
    if args.driver:
        cfg.scf.driver = str(args.driver)
    solver = create_solver(cfg)
    report = validate_solver_adapter_contract(
        solver,
        run_mean_field=bool(args.run_mean_field),
        periodic=bool(args.periodic),
        not_implemented_is_error=bool(args.require_mean_field_success),
    )
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
