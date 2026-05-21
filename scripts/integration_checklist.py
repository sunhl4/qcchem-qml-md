#!/usr/bin/env python3
"""Run the multi-backend integration checklist for a registered ``scf.driver``."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qchem_stack.chem.integration.checklist import run_integration_checklist
from qchem_stack.chem.solvers import create_solver, validate_solver_adapter_contract
from qchem_stack.config import load_experiment_config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/example_h2.yaml"),
        help="Experiment YAML (default: configs/example_h2.yaml).",
    )
    parser.add_argument(
        "--driver",
        type=str,
        required=True,
        help="scf.driver backend id (e.g. pyscf, psi4, custom_external_template).",
    )
    parser.add_argument(
        "--run-scf",
        action="store_true",
        help="Execute compute_mean_field and validate driver_meta.kernel_bindings.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON only.",
    )
    args = parser.parse_args()
    cfg = load_experiment_config(args.config)
    cfg.scf.driver = str(args.driver)
    solver = create_solver(cfg)
    contract = validate_solver_adapter_contract(
        solver, run_mean_field=bool(args.run_scf), not_implemented_is_error=False
    )
    report = run_integration_checklist(solver, run_mean_field=bool(args.run_scf))
    payload = {
        "adapter_contract": contract.as_dict(),
        "integration_checklist": report.as_dict(),
    }
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"backend_id={report.backend_id} ready_for_smoke={report.ready_for_smoke}")
        for item in report.items:
            req = "required" if item.get("required") else "optional"
            print(f"  [{item['status']}] {item['id']} ({req}): {item['detail']}")
        print("adapter_contract.ok =", contract.ok)
    ok = report.ready_for_smoke and contract.ok
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
