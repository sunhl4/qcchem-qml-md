"""Public build_pre_quantum_input API."""

from __future__ import annotations

import pytest

from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.scf_stage import run_scf_reference
from tests.helpers.paths import configs_path


def test_build_pre_quantum_input_supports_precomputed_driver() -> None:
    p = configs_path("example_h2_precomputed_bundle.yaml")
    cfg = load_experiment_config(p)
    ref = run_scf_reference(cfg)
    built = build_pre_quantum_input(cfg, ref, cfg_path=p)
    assert built.meta.get("source") == "precomputed_bundle"
    assert int(built.qubit_hamiltonian.n_qubits) > 0
    assert str(built.meta.get("precomputed_bundle_path") or "").endswith(
        "precomputed_classical_reference_h2.json"
    )


@pytest.mark.pyscf
def test_build_pre_quantum_input_pyscf_h2() -> None:
    pytest.importorskip("pyscf")
    from tests.fixtures.classical_reference import pyscf_rhf_from_config

    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    ref = pyscf_rhf_from_config(cfg)
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference

    cref = ClassicalMeanFieldReference(
        mf=ref.mf,
        e_tot=float(ref.e_tot),
        mo_energy=ref.mo_energy,
        molecular_system=ref.molecular_system,
        driver_meta=dict(ref.driver_meta),
    )
    built = build_pre_quantum_input(cfg, cref, cfg_path=configs_path("example_h2.yaml"))
    assert built.qubit_hamiltonian.n_qubits >= 2
