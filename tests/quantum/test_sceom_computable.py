"""SCEOMMatrixComputable UCCSD + HEA parity."""

from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
from qchem_stack.config import load_experiment_config
from qchem_stack.protocols.computables.base import EvaluationContext
from qchem_stack.protocols.computables.sceom_matrix import SCEOMMatrixComputable
from qchem_stack.quantum.algorithms.sceom import (
    run_sceom_nested_commutator_from_hea,
    run_sceom_nested_commutator_from_uccsd,
)
from qchem_stack.quantum.variational_branch import build_uccsd_variational_model
from tests.helpers.paths import configs_path
from tests.test_gap_closure_and_ucc import pyscf_rhf_from_config


def _qh():
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    ref = ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )
    return build_pre_quantum_input(cfg, ref).hamiltonian


def test_sceom_computable_hea_matches_direct() -> None:
    qh = _qh()
    angles = np.zeros(2 * qh.n_qubits, dtype=float)
    direct = run_sceom_nested_commutator_from_hea(
        qh, angles, 1, subspace_dim=2, generator_strategy_yaml="legacy"
    )
    comp = SCEOMMatrixComputable(
        "sceom",
        qh,
        subspace_dim=2,
        generator_strategy="legacy",
    )
    out = comp.evaluate(EvaluationContext(angles=angles, extra={"hea_depth": 1}))
    assert out.meta.get("computable_runtime") == "SCEOMMatrixComputable"
    assert out.meta.get("sceom_variety") == "hea"
    assert len(out.value["excitation_energies"]) == len(direct.energies)


def test_sceom_computable_uccsd_matches_direct() -> None:
    cfg = load_experiment_config(configs_path("example_h2_uccsd.yaml"))
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
    angles = np.zeros(model.n_params, dtype=float)
    direct = run_sceom_nested_commutator_from_uccsd(
        qh,
        angles,
        model.prepare_state,
        subspace_dim=2,
        generator_strategy_yaml="legacy",
    )
    comp = SCEOMMatrixComputable(
        "sceom",
        qh,
        subspace_dim=2,
        generator_strategy="legacy",
        prepare_state=model.prepare_state,
    )
    out = comp.evaluate(EvaluationContext(angles=angles))
    assert out.meta.get("sceom_variety") == "uccsd"
    assert len(out.value["excitation_energies"]) == len(direct.energies)
