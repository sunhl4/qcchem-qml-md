from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from qchem_stack.protocols.ansatz_prep import AnsatzPrepSpec
from qchem_stack.protocols.computables.expectation import ExpectationValueComputable
from qchem_stack.quantum.algorithms.vqe import VQE
from qchem_stack.quantum.variational_branch import build_uccsd_variational_model
from tests.test_gap_closure_and_ucc import pyscf_rhf_from_config


def _qh():
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    return build_pre_quantum_input(cfg, ref).hamiltonian


def test_expectation_computable_hea_matches_vqe() -> None:
    qh = _qh()
    exe = StatevectorHeaExecutor()
    v = VQE(qh, depth=1, executor=exe).run(seed=1, maxiter=30)
    comp = ExpectationValueComputable(
        "ground_energy",
        qh.operator,
        qh.n_qubits,
        hea_depth=1,
        executor=exe,
    )
    from qchem_stack.protocols.computables.base import EvaluationContext

    out = comp.evaluate(EvaluationContext(angles=np.asarray(v.angles, dtype=float)))
    assert abs(float(out.value) - float(v.energy)) < 1e-8


def test_expectation_computable_uccsd_ansatz_prep() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_uccsd.yaml")
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    qh = build_pre_quantum_input(cfg, ref).hamiltonian
    exe = StatevectorHeaExecutor()
    model = build_uccsd_variational_model(qh, exe, trotter_steps=None)
    angles = np.zeros(model.n_params)
    prep = AnsatzPrepSpec.uccsd(hamiltonian=qh, angles=angles, trotter_steps=None)
    comp = ExpectationValueComputable("e", qh.operator, qh.n_qubits)
    from qchem_stack.protocols.computables.base import EvaluationContext

    e_comp = float(comp.evaluate(EvaluationContext(angles=angles, ansatz_prep=prep)).value)
    e_ref = float(exe.expectation_state(model.prepare_state(angles), qh.operator, qh.n_qubits))
    assert abs(e_comp - e_ref) < 1e-8
