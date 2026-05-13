#!/usr/bin/env python3
"""Sample regression over packaged YAMLs (plan D75).

Runs config-only ``export_parity_criteria_table`` on every path (no PySCF).

When ``--pipeline`` is passed *and* PySCF is importable, also runs
``run_pipeline_from_config`` for each YAML (may be slow).

Usage::

    python scripts/sample_pipeline_configs.py
    python scripts/sample_pipeline_configs.py --pipeline
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

# Ten representative packaged configs (Methods / parity / embedding / mitigation spread).
SAMPLE_CONFIGS_REL: tuple[str, ...] = (
    "configs/example_h2.yaml",
    "configs/example_h2_uccsd.yaml",
    "configs/example_h2_uccsd_trotter.yaml",
    "configs/example_h2_qpe_track_parity_integrations.yaml",
    "configs/example_h2_excited_smoke.yaml",
    "configs/example_decomposition_plugin_toy.yaml",
    "configs/example_h2_embedding_parity.yaml",
    "configs/example_h2_zne_circuit_fold.yaml",
    "configs/example_h2_pec_literature_stub.yaml",
    "configs/example_oniom_toy.yaml",
)


def _run_export(cfg_rel: str) -> int:
    script = _ROOT / "scripts" / "export_parity_criteria_table.py"
    env = {**os.environ, "PYTHONPATH": str(_ROOT / "src")}
    proc = subprocess.run(
        [sys.executable, str(script), str(_ROOT / cfg_rel)],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr or proc.stdout or "")
        return proc.returncode or 1
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError:
        sys.stderr.write(f"invalid JSON from export for {cfg_rel}\n")
        return 1
    if data.get("parity_export_schema_version") != "2":
        sys.stderr.write(f"{cfg_rel}: unexpected parity_export_schema_version\n")
        return 1
    return 0


def _run_pipeline(cfg_rel: str) -> int:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_from_config

    p = _ROOT / cfg_rel
    cfg = load_experiment_config(p)
    out = run_pipeline_from_config(p)
    if cfg.quantum.use_pauli_protocol:
        ok = out.get("energy_pauli_protocol") is not None
    else:
        ok = out.get("energy_after_variational") is not None
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Sample parity export / pipeline over 10 YAMLs.")
    ap.add_argument(
        "--pipeline",
        action="store_true",
        help="Also run full pipeline (requires PySCF where chemistry is needed)",
    )
    args = ap.parse_args()
    run_pipe = args.pipeline
    if run_pipe:
        try:
            import pyscf  # noqa: F401
        except ImportError:
            print("sample_pipeline_configs: skip --pipeline (PySCF not installed)", file=sys.stderr)
            run_pipe = False

    for rel in SAMPLE_CONFIGS_REL:
        code = _run_export(rel)
        if code != 0:
            sys.stderr.write(f"export failed: {rel}\n")
            return code
        if run_pipe:
            try:
                pc = _run_pipeline(rel)
            except Exception as exc:  # noqa: BLE001
                sys.stderr.write(f"pipeline error {rel}: {exc}\n")
                return 1
            if pc != 0:
                sys.stderr.write(f"pipeline failed: {rel}\n")
                return pc
        print("ok", rel)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
