#!/usr/bin/env python3
"""CI smoke: load packaged config and run orchestration sync.

Default H2 path requires PySCF. ``--precomputed-only`` uses the offline bundle lane (no PySCF).

Usage::

    python scripts/smoke_pipeline.py
    python scripts/smoke_pipeline.py --precomputed-only  # example_h2_precomputed_bundle.yaml (no PySCF)
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
    if cfg_obj.quantum.pauli.use_protocol:
        ok = e is not None and out.get("resource_summary") is not None
    else:
        ok = out.get("energy_after_variational") is not None
        if ok and (
            cfg_obj.quantum.excited.vqd.after_variational
            or cfg_obj.quantum.excited.qse.after_variational
            or cfg_obj.quantum.excited.sceom.after_variational
        ):
            ok = out.get("resource_summary") is not None
    return 0 if ok else 1


def _run_precomputed_smoke(cfg_path: Path) -> int:
    """Offline pre-quantum lane: bundle → PreQuantumInput → VQE (no PySCF import)."""
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_from_config

    cfg_obj = load_experiment_config(cfg_path)
    if str(cfg_obj.scf.driver).strip().lower() != "precomputed":
        print(f"smoke_pipeline: expected scf.driver=precomputed in {cfg_path}", file=sys.stderr)
        return 2
    out = run_pipeline_from_config(cfg_path)
    pqi = out.get("pre_quantum_input") or {}
    print(f"--- {cfg_path.name} (precomputed) ---")
    print("pre_quantum_source", pqi.get("source"))
    print("hamiltonian_fingerprint", (pqi.get("hamiltonian_fingerprint") or "")[:16], "...")
    print("energy_after_variational", out.get("energy_after_variational"))
    print("pre_quantum_build_cache", out.get("pre_quantum_build_cache"))
    rs = (out.get("repro") or {}).get("run_summary") or {}
    print("repro.run_summary.pre_quantum_source", rs.get("pre_quantum_source"))
    ok = (
        pqi.get("source") == "precomputed_bundle"
        and out.get("energy_after_variational") is not None
        and bool(pqi.get("hamiltonian_fingerprint"))
    )
    return 0 if ok else 1


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    argv = sys.argv[1:]
    if "--precomputed-only" in argv:
        cfg = root / "configs" / "example_h2_precomputed_bundle.yaml"
        if not cfg.exists():
            print("missing", cfg, file=sys.stderr)
            return 2
        return _run_precomputed_smoke(cfg)
    try:
        import pyscf  # noqa: F401
    except ImportError:
        print(
            "smoke_pipeline: skip (install PySCF: pip install qchem-stack[chem])", file=sys.stderr
        )
        return 0
    if "--qiskit-shots" in argv:
        try:
            import qiskit  # noqa: F401
            import qiskit_aer  # noqa: F401
        except ImportError:
            print(
                "smoke_pipeline: skip --qiskit-shots (install: pip install qchem-stack[quantum])",
                file=sys.stderr,
            )
            return 0
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
