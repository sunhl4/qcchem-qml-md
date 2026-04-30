#!/usr/bin/env python3
"""CI smoke: load packaged H2 config and run orchestration sync (requires PySCF).

Usage::

    python scripts/smoke_pipeline.py
    python scripts/smoke_pipeline.py --excited      # example_h2.yaml then excited smoke
    python scripts/smoke_pipeline.py --excited-only   # only configs/example_h2_excited_smoke.yaml
    python scripts/smoke_pipeline.py --sampled        # configs/example_h2_sampled.yaml
    python scripts/smoke_pipeline.py --qiskit-shots  # H2 with Qiskit Aer shot counts (needs pip install .[quantum])
    python scripts/smoke_pipeline.py --iqeb  # IQEB outer loop on H2 (PySCF)
    python scripts/smoke_pipeline.py --projection-trace  # projection L1 trace YAML
"""

from __future__ import annotations

import sys
from pathlib import Path


def _run_smoke_cfg(cfg_path: Path) -> int:
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_from_config

    cfg_obj = load_experiment_config(cfg_path)
    out = run_pipeline_from_config(cfg_path)
    e = out.get("energy_pauli_protocol")
    print(f"--- {cfg_path.name} ---")
    print("energy_pauli_protocol", e)
    print("resource_summary", out.get("resource_summary"))
    if out.get("pauli_measurement_ledger") is not None:
        print("pauli_measurement_ledger_n", len(out["pauli_measurement_ledger"]))
    print("repro.run_summary", (out.get("repro") or {}).get("run_summary"))
    if cfg_obj.quantum.use_pauli_protocol:
        ok = e is not None and out.get("resource_summary") is not None
    else:
        ok = out.get("energy_after_variational") is not None
        if ok and (
            cfg_obj.quantum.vqd_after_variational
            or cfg_obj.quantum.qse_after_variational
            or cfg_obj.quantum.sceom_after_variational
        ):
            ok = out.get("resource_summary") is not None
    return 0 if ok else 1


def main() -> int:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        print("smoke_pipeline: skip (install PySCF: pip install qchem-stack[chem])", file=sys.stderr)
        return 0
    if "--qiskit-shots" in sys.argv[1:]:
        try:
            import qiskit  # noqa: F401
            import qiskit_aer  # noqa: F401
        except ImportError:
            print("smoke_pipeline: skip --qiskit-shots (install: pip install qchem-stack[quantum])", file=sys.stderr)
            return 0
    root = Path(__file__).resolve().parents[1]
    argv = sys.argv[1:]
    if "--excited-only" in argv:
        paths = [root / "configs" / "example_h2_excited_smoke.yaml"]
    elif "--qiskit-shots" in argv:
        paths = [root / "configs" / "example_h2_qiskit_shots.yaml"]
    elif "--sampled" in argv:
        paths = [root / "configs" / "example_h2_sampled.yaml"]
    elif "--iqeb" in argv:
        paths = [root / "configs" / "example_h2_iqeb.yaml"]
    elif "--projection-trace" in argv:
        paths = [root / "configs" / "example_h2_projection_trace.yaml"]
    elif "--excited" in argv:
        paths = [
            root / "configs" / "example_h2.yaml",
            root / "configs" / "example_h2_excited_smoke.yaml",
        ]
    else:
        paths = [root / "configs" / "example_h2.yaml"]

    for cfg in paths:
        if not cfg.exists():
            print("missing", cfg, file=sys.stderr)
            return 2
        code = _run_smoke_cfg(cfg)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
