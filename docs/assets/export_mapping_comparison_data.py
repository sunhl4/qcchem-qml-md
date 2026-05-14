#!/usr/bin/env python3
"""Export real mapping comparison metrics from qchem-stack runs.

Writes: ``docs/assets/data/mapping_comparison_h2_sto3g.json``

Method:
- For each mapping (JW/BK/SCBK), run the pipeline on H2/sto-3g using
  ``configs/example_h2.yaml`` with that mapping.
- Read real ``resource_summary`` emitted by the Pauli protocol compiler/runtime:
  ``n_qubits``, ``max_depth``, ``sum_twoq``, ``n_circuits``, ``sum_shots``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_PATH = Path(__file__).resolve().parent / "data" / "mapping_comparison_h2_sto3g.json"
CFG_REL = "configs/example_h2.yaml"

MAPPINGS: list[tuple[str, str]] = [
    ("jordan_wigner", "Jordan-Wigner (JW)"),
    ("bravyi_kitaev", "Bravyi-Kitaev (BK)"),
    ("symmetry_conserving_bravyi_kitaev", "Sym.-Conserving BK (SCBK)"),
]


def main() -> None:
    sys.path.insert(0, str(ROOT / "src"))

    from qchem_stack.config import ExperimentConfig, load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg_path = ROOT / CFG_REL
    base_cfg = load_experiment_config(cfg_path)
    rows: list[dict[str, int | str | float | None]] = []

    for mapping_key, mapping_label in MAPPINGS:
        cdict = base_cfg.model_dump()
        cdict["experiment_id"] = f"{base_cfg.experiment_id}_mapping_{mapping_key}"
        cdict["active_space"]["fermion_qubit_mapping"] = mapping_key
        # Keep runtime practical while preserving a real pipeline run per mapping.
        cdict["quantum"]["vqe_maxiter"] = min(int(cdict["quantum"].get("vqe_maxiter", 40)), 40)
        cfg = ExperimentConfig.model_validate(cdict)

        out = run_pipeline_sync(cfg, cfg_path=cfg_path)
        rs = out.get("resource_summary")
        if not isinstance(rs, dict):
            raise RuntimeError(f"resource_summary missing for mapping={mapping_key}")

        rows.append(
            {
                "mapping_key": mapping_key,
                "mapping_label": mapping_label,
                "n_qubits": int(rs.get("n_qubits", 0)),
                "compiled_max_depth": int(rs.get("max_depth", 0)),
                "compiled_sum_twoq": int(rs.get("sum_twoq", 0)),
                "n_circuits": int(rs.get("n_circuits", 0)),
                "sum_shots": int(rs.get("sum_shots", 0)),
                "energy_pauli_protocol": (
                    float(out["energy_pauli_protocol"]) if out.get("energy_pauli_protocol") is not None else None
                ),
            }
        )

    payload = {
        "schema": "mapping_comparison_v1",
        "config_path": CFG_REL,
        "molecule_basis": base_cfg.molecule.basis,
        "rows": rows,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()

