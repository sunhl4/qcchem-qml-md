from __future__ import annotations

import numpy as np
import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from qchem_stack.protocols.computables.base import EvaluationContext
from qchem_stack.protocols.computables.expectation import ExpectationValueComputable
from qchem_stack.protocols.computables.qse_matrices import QSEMatricesComputable
from qchem_stack.protocols.protocol_list import ProtocolList
from qchem_stack.quantum.algorithms.excited_basis import build_qse_basis_from_vqe_hea
from tests.fixtures.classical_reference import pyscf_rhf_from_config


def test_protocol_list_runs_energy_and_qse() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    qh = build_pre_quantum_input(cfg, ref).hamiltonian
    angles = np.zeros(2 * qh.n_qubits, dtype=float)
    basis = build_qse_basis_from_vqe_hea(angles, qh.n_qubits, 1, max_basis=4)
    from qchem_stack.backends.executor_base import StatevectorHeaExecutor

    exe = StatevectorHeaExecutor()
    plist = ProtocolList.from_computables(
        [
            ExpectationValueComputable(
                "energy",
                qh.operator,
                qh.n_qubits,
                hea_depth=1,
                executor=exe,
            ),
            QSEMatricesComputable(
                "qse",
                qh.operator,
                qh.n_qubits,
                basis=basis,
                shot_mode="exact",
            ),
        ]
    )
    out = plist.run_all(EvaluationContext(angles=angles))
    assert "energy" in out["results"]
    assert "qse" in out["results"]
    assert out["results"]["qse"]["H"].shape[0] == len(basis)


@pytest.mark.skipif(
    __import__("importlib").util.find_spec("qiskit") is None,
    reason="qiskit not installed",
)
def test_protocol_list_qse_qiskit_computable_smoke() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    qh = build_pre_quantum_input(cfg, ref).hamiltonian
    angles = np.zeros(2 * qh.n_qubits, dtype=float)
    basis = build_qse_basis_from_vqe_hea(angles, qh.n_qubits, 1, max_basis=3)
    comp = QSEMatricesComputable(
        "qse_qiskit",
        qh.operator,
        qh.n_qubits,
        basis=basis,
        shot_mode="pauli_transitions_qiskit",
        shots_per_ij_term=512,
    )
    out = comp.evaluate(EvaluationContext(angles=angles))
    assert out.value["H"].shape[0] == len(basis)
    assert out.meta.get("shot_noise_model") == "qiskit_histogram_per_ij_term"
