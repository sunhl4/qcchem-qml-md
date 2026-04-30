"""Fragment Mulliken projection Hamiltonian (PySCF CASCI + JW)."""

from __future__ import annotations

import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.chem.embedding.projection_hamiltonian import (
    molecular_hamiltonian_fragment_mulliken_projection,
)
from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_pyscf
from qchem_stack.config import (
    ActiveSpaceSpec,
    BackendSpecConfig,
    EmbeddingSpec,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
    SCFSpec,
)


def _h2_cfg(*, fragment_atoms: list[int]) -> ExperimentConfig:
    return ExperimentConfig(
        experiment_id="proj_h2",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]]),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=QuantumSpec(),
        embedding=EmbeddingSpec(
            mode="projection",
            projection_quantum_hamiltonian="fragment_mulliken_mo",
            projection_fragment_atom_indices=list(fragment_atoms),
        ),
    )


def test_projection_mulliken_h2_full_system_matches_global() -> None:
    cfg = _h2_cfg(fragment_atoms=[0, 1])
    rhf = PySCFDriver.from_config(cfg).run_rhf()
    g = molecular_hamiltonian_from_pyscf(rhf, 2, 2)
    p, audit = molecular_hamiltonian_fragment_mulliken_projection(rhf, cfg)
    assert g.meta["hamiltonian_fingerprint"] == p.meta["hamiltonian_fingerprint"]
    assert audit["selected_mo_indices"]


def test_projection_mulliken_h4_subfragment_changes_hamiltonian() -> None:
    molecule = MoleculeSpec(
        symbols=["H", "H", "H", "H"],
        coordinates_bohr=[
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
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=QuantumSpec(),
    )
    cfg_global = ExperimentConfig(
        **base,
        embedding=EmbeddingSpec(
            mode="projection",
            projection_quantum_hamiltonian="fragment_mulliken_mo",
            projection_fragment_atom_indices=[0, 1, 2, 3],
        ),
    )
    cfg_sub = ExperimentConfig(
        **base,
        embedding=EmbeddingSpec(
            mode="projection",
            projection_quantum_hamiltonian="fragment_mulliken_mo",
            projection_fragment_atom_indices=[0],
        ),
    )
    rhf = PySCFDriver.from_config(cfg_global).run_rhf()
    g = molecular_hamiltonian_from_pyscf(
        rhf,
        n_active_orbitals=2,
        n_active_electrons=2,
    )
    p_sub, audit = molecular_hamiltonian_fragment_mulliken_projection(rhf, cfg_sub)
    assert audit["selected_mo_indices"]
    assert g.meta["hamiltonian_fingerprint"] != p_sub.meta["hamiltonian_fingerprint"]
