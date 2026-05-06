#!/usr/bin/env python3
"""Smoke-check parity export JSON (config-only) for L1 regression.

Runs ``export_parity_criteria_table`` (config-only) on ``SAMPLE_CONFIGS_REL`` and asserts
stable keys + ``parity_matrix_anchor`` on every gap row.

Does not require PySCF or a pipeline results file.

When adding parity-driven ``configs/*.yaml``, extend ``SAMPLE_CONFIGS_REL`` so CI keeps
schema coverage (see ``docs/P1_completion_audit.md`` §5 item 12).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from qchem_stack.protocols.inquanto_contract import PARITY_EXPORT_V2_STABLE_KEYS

# M2-style sampling: VQE + ADAPT + excited + IQEB + projection + Pauli shot-path YAMLs (config-only export).
SAMPLE_CONFIGS_REL = (
    "configs/example_h2.yaml",
    "configs/tutorial_inquanto_chain_h2.yaml",
    "configs/example_h2_excited_smoke.yaml",
    "configs/example_h2_iqeb.yaml",
    "configs/example_h2_projection_trace.yaml",
    "configs/example_h4_projection_mulliken.yaml",
    "configs/example_h2_sampled.yaml",
    "configs/example_h2_qiskit_shots.yaml",
    "configs/example_h2_uccsd.yaml",
    "configs/example_h2_uccsd_trotter.yaml",
    "configs/example_h2_zne_circuit_fold.yaml",
    "configs/qpe_dual_track_demo.yaml",
    "configs/example_decomposition_plugin_toy.yaml",
    "configs/example_h2_pbc_gamma.yaml",
    "configs/example_oniom_toy.yaml",
    "configs/example_h4_dmet_fragment_exact_small.yaml",
    "configs/example_h2_qpe_track.yaml",
    "configs/example_h2_qpe_track_parity_integrations.yaml",
    "configs/example_h2_casscf_audit.yaml",
    "configs/example_h2_embedding_parity.yaml",
)


def _run_export(root: Path, cfg_rel: str, env: dict[str, str]) -> tuple[int, dict]:
    script = root / "scripts" / "export_parity_criteria_table.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(root / cfg_rel)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if proc.returncode != 0:
        return proc.returncode or 1, {}
    return 0, json.loads(proc.stdout)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONPATH": f"{root / 'src'}" + os.pathsep + os.environ.get("PYTHONPATH", "")}
    for cfg_rel in SAMPLE_CONFIGS_REL:
        code, data = _run_export(root, cfg_rel, env)
        if code != 0:
            sys.stderr.write(f"export failed for {cfg_rel}\n")
            return code
        missing = sorted(PARITY_EXPORT_V2_STABLE_KEYS - set(data.keys()))
        if missing:
            sys.stderr.write(f"{cfg_rel}: export missing stable keys: {missing}\n")
            return 1
        if data.get("parity_export_schema_version") != "2":
            sys.stderr.write(f"{cfg_rel}: unexpected parity_export_schema_version\n")
            return 1
        gaps = data.get("inquanto_gap_categories")
        if not isinstance(gaps, list) or not gaps:
            sys.stderr.write(f"{cfg_rel}: inquanto_gap_categories empty\n")
            return 1
        for g in gaps:
            if not isinstance(g, dict) or not g.get("parity_matrix_anchor"):
                sys.stderr.write(f"{cfg_rel}: gap row missing parity_matrix_anchor\n")
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
