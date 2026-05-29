from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.molecular_system_config import molecular_system_from_experiment
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.chem.solvers.registry import create_solver
from qchem_stack.config import load_experiment_config
from tests.helpers.paths import configs_path

pyscf = pytest.importorskip("pyscf")


def test_pbc_h2_cell_rhf_to_qubit_h() -> None:
    cfg = load_experiment_config(configs_path("example_h2_pbc_gamma.yaml"))
    solver = create_solver(cfg)
    pack = solver.compute_mean_field(periodic=True)
    ref = ClassicalMeanFieldReference.from_mean_field_pack(
        pack,
        molecular_system=molecular_system_from_experiment(cfg),
    )
    assert ref.driver_meta.get("pbc") is True
    assert float(ref.e_tot) < 0.0
    qh = build_pre_quantum_input(cfg, ref).qubit_hamiltonian
    assert qh.n_qubits == 4
    assert "pyscf_driver" in qh.meta
    mol = ref.mf.mol
    a = np.asarray(getattr(mol, "a", getattr(mol, "lattice_vecs", None)), dtype=float)
    assert a.shape == (3, 3)
    assert abs(float(a[0, 0]) - 8.0) < 0.1
