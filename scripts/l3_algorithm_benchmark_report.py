#!/usr/bin/env python3
"""Emit ``algorithm_benchmark_bundle_v1`` (+ optional merge) for Methods / paper tables.

Requires PySCF for chemistry YAMLs. Typical use (opt-in heavy gate)::

    QCHEM_RUN_L3=1 pytest -m l3 -q
    python scripts/l3_algorithm_benchmark_report.py
    python scripts/l3_algorithm_benchmark_report.py --config configs/example_h2.yaml

``--merged`` appends :func:`merged_experiment_benchmark_v1` (totals + ``by_quantum_algorithm_yaml`` rollup).

**Config sources**

- Default YAML list: ``DEFAULT_BENCHMARK_YAMLS`` in :mod:`qchem_stack.integrations.l3_algorithm_benchmark`.
- L3 pytest gate list (subset): ``L3_PYTEST_YAMLS`` — same module (baseline VQE + ADAPT/IQEB/excited representatives).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    ap = argparse.ArgumentParser(description="Algorithm L3 benchmark JSON report.")
    ap.add_argument(
        "--config",
        action="append",
        dest="configs",
        metavar="REL_PATH",
        help="Relative config path (repeatable); default: bundled representative set",
    )
    ap.add_argument(
        "--merged", action="store_true", help="Also print merged_experiment_benchmark_v1 summary"
    )
    args = ap.parse_args()
    rels = list(args.configs) if args.configs else []
    if not rels:
        from qchem_stack.quantum.l3_algorithm_benchmark import DEFAULT_BENCHMARK_YAMLS

        rels = list(DEFAULT_BENCHMARK_YAMLS)

    sys.path.insert(0, str(_ROOT / "src"))
    from qchem_stack.quantum.l3_algorithm_benchmark import (
        algorithm_benchmark_bundle_v1,
        merged_experiment_benchmark_v1,
    )

    bundle = algorithm_benchmark_bundle_v1(repo_root=_ROOT, config_rels=rels)
    out_obj: dict = {
        "bundle_schema_version": "1",
        "algorithm_benchmark_bundle_v1": bundle,
    }
    if args.merged:
        out_obj["merged_experiment_benchmark_v1"] = merged_experiment_benchmark_v1(bundle)
    json.dump(out_obj, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
