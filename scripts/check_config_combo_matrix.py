#!/usr/bin/env python3
"""Validate representative YAML combos against config validators (pre-quantum + backend)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs"

# Representative configs covering backend providers and pre-quantum ingress.
SAMPLE_YAMLS = [
    "example_h2.yaml",
    "example_h2_precomputed_bundle.yaml",
    "example_h2_sampled.yaml",
    "example_h2_qiskit_shots.yaml",
]


def main() -> int:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.config.quantum_helpers import pauli_protocol_enabled

    failures: list[str] = []
    for name in SAMPLE_YAMLS:
        path = CONFIGS / name
        if not path.is_file():
            failures.append(f"missing sample config: {path}")
            continue
        try:
            cfg = load_experiment_config(path)
        except Exception as exc:
            failures.append(f"{name}: load failed: {exc}")
            continue
        provider = (cfg.backend.provider or "").strip().lower()
        if cfg.quantum.pauli.run_qiskit_shots and provider != "qiskit":
            failures.append(f"{name}: run_qiskit_shots requires backend.provider=qiskit")
        if cfg.quantum.pauli.run_sampled and provider not in ("statevector", "qiskit", ""):
            failures.append(f"{name}: run_sampled expects statevector-like provider")
        if pauli_protocol_enabled(cfg) and not cfg.quantum.pauli.use_protocol:
            failures.append(f"{name}: pauli protocol flags inconsistent")
    if failures:
        print("config combo matrix failures:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("config combo matrix OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
