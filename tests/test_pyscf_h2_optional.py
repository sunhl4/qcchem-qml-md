from __future__ import annotations

import pytest

pyscf = pytest.importorskip("pyscf")

from qchem_stack.config import ActiveSpaceSpec, ExperimentConfig, MoleculeSpec, load_experiment_config
from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_pyscf
from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.qpe_qec_demo import FaultTolerantDemoAdapter


def test_h2_active_space_vqe(tmp_path_factory) -> None:
    root = tmp_path_factory.mktemp("cfg")
    cfg_path = root / "h2.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: t
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    drv = PySCFDriver.from_config(cfg)
    r = drv.run_rhf()
    qh = molecular_hamiltonian_from_pyscf(r, n_active_orbitals=2, n_active_electrons=2)
    assert qh.meta.get("fermion_to_qubit_map") == "jordan_wigner"
    assert qh.meta.get("integral_source") == "pyscf_active_space"
    assert qh.meta.get("n_active_electrons") == 2
    v = VQE(qh, depth=1).run(maxiter=200, seed=0)
    ad = FaultTolerantDemoAdapter()
    e_dense = ad.ground_energy_dense(qh)
    assert abs(v.energy - e_dense) < 0.2


def test_h2_active_space_bravyi_kitaev_meta() -> None:
    cfg = ExperimentConfig(
        experiment_id="bk_meta",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]]),
        active_space=ActiveSpaceSpec(
            n_active_orbitals=2,
            n_active_electrons=2,
            fermion_qubit_mapping="bravyi_kitaev",
        ),
    )
    drv = PySCFDriver.from_config(cfg)
    r = drv.run_rhf()
    qh = molecular_hamiltonian_from_pyscf(
        r,
        n_active_orbitals=2,
        n_active_electrons=2,
        fermion_qubit_mapping="bravyi_kitaev",
    )
    assert qh.meta.get("fermion_to_qubit_map") == "bravyi_kitaev"


def test_h2_active_space_symmetry_conserving_bravyi_kitaev_dimension() -> None:
    cfg = ExperimentConfig(
        experiment_id="scbk_meta",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]]),
        active_space=ActiveSpaceSpec(
            n_active_orbitals=2,
            n_active_electrons=2,
            fermion_qubit_mapping="symmetry_conserving_bravyi_kitaev",
        ),
    )
    drv = PySCFDriver.from_config(cfg)
    r = drv.run_rhf()
    qh = molecular_hamiltonian_from_pyscf(
        r,
        n_active_orbitals=2,
        n_active_electrons=2,
        fermion_qubit_mapping="symmetry_conserving_bravyi_kitaev",
    )
    assert qh.meta.get("fermion_to_qubit_map") == "symmetry_conserving_bravyi_kitaev"
    assert qh.n_qubits == 2
    assert qh.meta.get("n_qubits") == 2
