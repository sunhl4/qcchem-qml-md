"""Fragment Mulliken projection Hamiltonian (PySCF CASCI + JW)."""

from __future__ import annotations

import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.embedding.projection_hamiltonian import (
    molecular_hamiltonian_fragment_mulliken_projection,
)
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import (
    ActiveSpaceSpec,
    BackendSpecConfig,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
    SCFSpec,
)
from tests.embedding_nested import embedding_projection
from tests.fixtures.classical_reference import pyscf_rhf_from_config


def _h2_cfg(*, fragment_atoms: list[int]) -> ExperimentConfig:
    return ExperimentConfig(
        experiment_id="proj_h2",
        random_seed=0,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=QuantumSpec(),
        embedding=embedding_projection(
            quantum_hamiltonian="fragment_mulliken_mo",
            fragment_atom_indices=list(fragment_atoms),
        ),
    )


def test_projection_mulliken_h2_full_system_matches_global() -> None:
    cfg = _h2_cfg(fragment_atoms=[0, 1])
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    g = build_pre_quantum_input(cfg, ref).hamiltonian
    p, audit = molecular_hamiltonian_fragment_mulliken_projection(ref, cfg)
    assert g.meta["hamiltonian_fingerprint"] == p.meta["hamiltonian_fingerprint"]
    assert p.meta["integral_source"] == "pyscf_projection_fragment_mulliken_v1"
    assert p.meta["integral_openfermion_bridge"] == "pyscf_spatial_openfermion_v1"
    assert audit["selected_mo_indices"]


def test_projection_mulliken_h4_subfragment_changes_hamiltonian() -> None:
    molecule = MoleculeSpec(
        symbols=["H", "H", "H", "H"],
        coordinates=[
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 1.4],
            [0.0, 0.0, 2.8],
            [0.0, 0.0, 4.2],
        ],
        basis="6-31g",
    )
    base = dict(
        experiment_id="proj_h4",
        random_seed=0,
        molecule=molecule,
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=QuantumSpec(),
    )
    cfg_global = ExperimentConfig(
        **base,
        embedding=embedding_projection(
            quantum_hamiltonian="fragment_mulliken_mo",
            fragment_atom_indices=[0, 1, 2, 3],
        ),
    )
    cfg_sub = ExperimentConfig(
        **base,
        embedding=embedding_projection(
            quantum_hamiltonian="fragment_mulliken_mo",
            fragment_atom_indices=[0],
        ),
    )
    rhf = pyscf_rhf_from_config(cfg_global)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    g = build_pre_quantum_input(cfg_global, ref).hamiltonian
    p_sub, audit = molecular_hamiltonian_fragment_mulliken_projection(ref, cfg_sub)
    assert audit["selected_mo_indices"]
    assert g.meta["hamiltonian_fingerprint"] != p_sub.meta["hamiltonian_fingerprint"]
