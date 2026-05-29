"""Public build_pre_quantum_input API and legacy Hamiltonian deprecation."""

from __future__ import annotations

import warnings

import pytest

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_classical_reference
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.scf_stage import run_scf_reference
from tests.fixtures.classical_reference import pyscf_rhf_from_config
from tests.helpers.paths import configs_path


@pytest.mark.pyscf
def test_legacy_hamiltonian_helper_emits_deprecation_and_matches_build() -> None:
    pytest.importorskip("pyscf")
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    result = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=result.mf,
        e_tot=float(result.e_tot),
        mo_energy=result.mo_energy,
        molecular_system=result.molecular_system,
        driver_meta=dict(result.driver_meta),
    )
    built = build_pre_quantum_input(cfg, ref, cfg_path=configs_path("example_h2.yaml"))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", DeprecationWarning)
        legacy = molecular_hamiltonian_from_classical_reference(
            ref,
            n_active_orbitals=int(cfg.active_space.cas.n_orbitals),
            n_active_electrons=int(cfg.active_space.cas.n_electrons),
        )
    assert any(isinstance(w.message, DeprecationWarning) for w in caught)
    assert legacy.n_qubits == built.qubit_hamiltonian.n_qubits
    assert (legacy.meta or {}).get("hamiltonian_fingerprint") == (
        built.qubit_hamiltonian.meta or {}
    ).get("hamiltonian_fingerprint")


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
