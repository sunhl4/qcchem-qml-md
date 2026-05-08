#!/usr/bin/env python3
"""Tutorial 4: UCCSD variational energy at or below RHF on aligned active-space H (H₂).

Runs ``configs/example_h2_uccsd.yaml`` and checks ``energy_after_variational <= scf_energy``
(within a small tolerance). UCCSD state preparation projects onto the JW fixed–electron-number
subspace before expectations; CI tests also assert the variational energy is not below the
ground state of the **delivered** qubit Hamiltonian on that sector (which may still differ from
PySCF FCI until the PySCF↔OpenFermion two-body convention is fully closed). Not a claim of
computational or hardware quantum advantage.

Requires PySCF (``pip install qchem-stack[chem]``). ``PYTHONPATH`` must include ``src``
when running outside an editable install.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        print("tutorial_04: skip (install PySCF / pip install qchem-stack[chem])")
        return 0

    root = Path(__file__).resolve().parents[1]
    cfg_path = root / "configs" / "example_h2_uccsd.yaml"
    if not cfg_path.is_file():
        print("missing", cfg_path, file=sys.stderr)
        return 2

    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    out = run_pipeline_sync(load_experiment_config(cfg_path), cfg_path=cfg_path)
    scf_e = float(out["scf_energy"])
    ev = float(out["energy_after_variational"])
    print(f"tutorial_04: scf_energy={scf_e:.9f} Ha")
    print(f"tutorial_04: energy_after_variational={ev:.9f} Ha")
    if ev > scf_e + 1e-3:
        print(
            "tutorial_04: variational energy did not reach RHF reference "
            f"(delta={ev - scf_e:.6e} Ha)",
            file=sys.stderr,
        )
        return 1
    print("tutorial_04: OK (variational ≤ RHF + 1e-3 Ha)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
