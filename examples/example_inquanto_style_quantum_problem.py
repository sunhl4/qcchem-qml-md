#!/usr/bin/env python3
"""InQuanto-style chemistry → quantum problem construction (open-stack analog).

Run from repo root::

    python examples/example_inquanto_style_quantum_problem.py

Website narrative: /guide/chemistry-and-embedding/inquanto-pyscf-problem-analog
"""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    try:
        import pyscf  # noqa: F401
    except ImportError:
        print("Install PySCF extras: pip install 'qchem-stack[chem]'")
        return 1

    import numpy as np

    from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
    from qchem_stack.config import load_experiment_config
    from qchem_stack.tensornet.dense_expectation_reference import expectation_qubit_operator_dense

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)

    print("=== Restricted active-space tuple (cf. InQuanto get_system) ===")
    prob = drv.get_restricted_active_space_quantum_problem(
        int(cfg.active_space.n_active_orbitals),
        int(cfg.active_space.n_active_electrons),
        fermion_qubit_mapping=cfg.active_space.fermion_qubit_mapping,
    )
    print("meta:", prob.meta)
    print("qubit_hamiltonian.meta jw_build:", prob.qubit_hamiltonian.meta.get("jw_build"))
    print(
        "FermionSpace:",
        prob.fermion_space.n_spin_orbitals,
        "spin orbitals,",
        prob.fermion_space.n_electrons,
        "electrons",
    )
    print("JW HF state dimension:", prob.hartree_fock_state_jw.shape)
    print("QubitHamiltonian n_qubits:", prob.qubit_hamiltonian.n_qubits)

    e_hf = expectation_qubit_operator_dense(
        prob.qubit_hamiltonian.operator,
        prob.hartree_fock_state_jw,
        n_qubits=prob.qubit_hamiltonian.n_qubits,
    )
    print(
        f"Hartree–Fock energy expectation (JW state, dense reference): {float(np.real(e_hf)):.8f} Ha"
    )

    co = prob.compact_mo_operator
    print(
        "compact ERIs:",
        co.symmetry_meta.get("eri_raw_ndim"),
        "D, size",
        co.symmetry_meta.get("eri_raw_n_elements"),
    )
    print(
        "MO integral table (head):\n",
        co.df_mo_integrals(max_two_body=30).head(12).to_string(index=False),
    )

    print("\n=== AO-wrapped SCF (cf. InQuanto get_system_ao) ===")
    ao = drv.get_system_ao(run_hf=True)
    print("integral_representation:", ao.driver_meta.get("integral_representation"))
    print("ao_run_hf:", ao.driver_meta.get("ao_run_hf"), "e_tot:", ao.e_tot)
    print("AO summary df:\n", ao.ao_driver_summary_df().to_string(index=False))

    print("\n=== Optional PySCF molecular symmetry (cf. classical-side savings) ===")
    cx = cfg.chemistry_extended.model_copy(update={"pyscf_symmetry": True})
    cfg_sym = cfg.model_copy(update={"chemistry_extended": cx})
    drv_sym = PySCFDriver.from_config(cfg_sym)
    prob_sym = drv_sym.get_restricted_active_space_quantum_problem(2, 2)
    print(
        "symmetry snapshot:",
        {
            k: prob_sym.meta[k]
            for k in ("pyscf_symmetry_detected", "pyscf_symmetry_subgroup")
            if k in prob_sym.meta
        },
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
