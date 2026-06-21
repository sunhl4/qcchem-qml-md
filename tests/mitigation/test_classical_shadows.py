"""Classical shadows runtime: fixed-seed H2 expectation vs statevector reference."""

from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input_with_context
from qchem_stack.config import load_experiment_config
from qchem_stack.mitigation.classical_shadows import classical_shadows_hamiltonian_expectation
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.orchestration.scf_stage import run_scf_reference
from qchem_stack.quantum.statevector import hea_state
from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")


def test_classical_shadows_h2_expectation_near_statevector() -> None:
    p = configs_path("example_h2_classical_shadows_stub.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    angles = np.asarray(out["angles"], dtype=float)
    depth = int(cfg.quantum.vqe.depth)
    rhf = run_scf_reference(cfg)
    pre, _ctx = build_pre_quantum_input_with_context(cfg, rhf)
    qh = pre.qubit_hamiltonian
    st = hea_state(angles, qh.n_qubits, depth)
    exact = StatevectorHeaExecutor().expectation_state(st, qh.operator, qh.n_qubits)
    shadow = classical_shadows_hamiltonian_expectation(
        st,
        qh.operator,
        qh.n_qubits,
        budget_pairs=8192,
        seed=int(cfg.random_seed),
    )
    assert shadow["expectation"] == pytest.approx(exact, abs=0.35)


def test_classical_shadows_pipeline_stub_trace() -> None:
    p = configs_path("example_h2_classical_shadows_stub.yaml")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    runtime = out.get("classical_shadows_computable_runtime")
    assert isinstance(runtime, dict)
    meta = runtime.get("computable_meta") or {}
    assert meta.get("estimator") == "local_random_pauli_classical_shadows_median_of_means_v1"
    dex = out.get("mitigation_dag_execution")
    assert isinstance(dex, dict)
    cs_nodes = [
        t
        for t in dex.get("trace", [])
        if isinstance(t, dict) and t.get("node") == "classical_shadows_expectation_stub"
    ]
    assert len(cs_nodes) == 1
    assert cs_nodes[0].get("computable_runtime") == "classical_shadows_hamiltonian_expectation"
