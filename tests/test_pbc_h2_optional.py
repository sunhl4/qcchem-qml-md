from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_classical_reference
from qchem_stack.config import load_experiment_config

pyscf = pytest.importorskip("pyscf")


def test_pbc_h2_cell_rhf_to_qubit_h(tmp_path) -> None:
    cfg_path = tmp_path / "h2pbc.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: pbc_h2
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
chemistry_extended:
  pbc_cell_vectors_bohr:
    - [5.0, 0.0, 0.0]
    - [0.0, 5.0, 0.0]
    - [0.0, 0.0, 5.0]
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    drv = PySCFDriver.from_config(cfg)
    r = drv.run_pbc_rhf()
    assert r.driver_meta.get("pbc") is True
    assert r.e_tot < 0.0
    ref = ClassicalMeanFieldReference(
        mf=r.mf,
        e_tot=float(r.e_tot),
        mo_energy=r.mo_energy,
        molecular_system=r.molecular_system,
        driver_meta=dict(r.driver_meta),
    )
    qh = molecular_hamiltonian_from_classical_reference(ref, n_active_orbitals=2, n_active_electrons=2)
    assert qh.n_qubits == 4
    assert "pyscf_driver" in qh.meta
    mol = r.mf.mol
    a = np.asarray(getattr(mol, "a", getattr(mol, "lattice_vecs", None)), dtype=float)
    assert a.shape == (3, 3)
    assert abs(float(a[0, 0]) - 5.0) < 0.1
