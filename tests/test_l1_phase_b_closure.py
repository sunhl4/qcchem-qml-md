"""L1 phase B (序 1–6): Protocols, resource semantics, Qermit analog, tensornet stub.

Complements ``test_protocols_jobs.py`` and ``test_tier2_inquanto_frontier.py`` with
contract-level checks tied to ``docs/InQuanto_B_J_逐项闭合计划.md``.
"""

from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.config import (
    ActiveSpaceSpec,
    ExperimentConfig,
    MitigationSpec,
    MoleculeSpec,
    QuantumSpec,
)
from qchem_stack.protocols.inquanto_contract import (
    PAULI_PATH_DISABLED,
    PAULI_PATH_EXACT,
    PAULI_PATH_QISKIT_COUNTS,
    PAULI_PATH_STATEVECTOR_SHOT_SIM,
    PARITY_SNAPSHOT_DOCUMENTED_KEYS,
    classify_pauli_expectation_path,
    mitigation_execution_model_public,
)
from qchem_stack.protocols.protocol import PauliAveragingProtocol, ProtocolPhase
from qchem_stack.mitigation.qermit_analog import build_qermit_style_mitigation_report
from qchem_stack.mitigation.qermit_runtime import execute_mitigation_dag_runtime
from qchem_stack.tensornet import run_cutensornet_expectation_stub


def test_protocol_phase_enum_is_five_stage_sequence() -> None:
    phases = list(ProtocolPhase)
    assert [p.value for p in phases] == ["instantiate", "build", "compile", "run", "evaluate"]


def test_classify_pauli_expectation_path_three_executor_families() -> None:
    q_disabled = QuantumSpec(use_pauli_protocol=False)
    assert classify_pauli_expectation_path(q_disabled) == PAULI_PATH_DISABLED

    q_exact = QuantumSpec(
        use_pauli_protocol=True,
        run_sampled_pauli_protocol=False,
        run_qiskit_shots_pauli_protocol=False,
    )
    assert classify_pauli_expectation_path(q_exact) == PAULI_PATH_EXACT

    q_sv = QuantumSpec(
        use_pauli_protocol=True,
        run_sampled_pauli_protocol=True,
        run_qiskit_shots_pauli_protocol=False,
    )
    assert classify_pauli_expectation_path(q_sv) == PAULI_PATH_STATEVECTOR_SHOT_SIM

    q_qk = QuantumSpec(
        use_pauli_protocol=True,
        run_sampled_pauli_protocol=False,
        run_qiskit_shots_pauli_protocol=True,
    )
    assert classify_pauli_expectation_path(q_qk) == PAULI_PATH_QISKIT_COUNTS

    with pytest.raises(ValueError):
        classify_pauli_expectation_path(
            QuantumSpec(
                use_pauli_protocol=True,
                run_sampled_pauli_protocol=True,
                run_qiskit_shots_pauli_protocol=True,
            )
        )


def test_mitigation_execution_model_public_stable_schema() -> None:
    mm = mitigation_execution_model_public()
    assert mm["schema"] == "mitigation_execution_model_v1"
    assert "sync_dag" in mm and "async_batch_execution" in mm
    assert isinstance(mm.get("public_doc_urls"), list)


def test_qermit_analog_report_with_zne_only_has_schema() -> None:
    cfg = ExperimentConfig(
        experiment_id="l1_b",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H"], coordinates_bohr=[[0.0, 0.0, 0.0]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=1, n_active_electrons=1),
        mitigation=MitigationSpec(zne_enabled=True, zne_scales=[1.0, 1.5]),
    )
    r = build_qermit_style_mitigation_report(cfg)
    assert r is not None
    assert r["schema"] == "qermit_analog_v2"
    assert "nodes" in r and "edges" in r and "topological_order" in r


def test_qermit_analog_spam_only_includes_spam_node() -> None:
    cfg = ExperimentConfig(
        experiment_id="l1_spam",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H"], coordinates_bohr=[[0.0, 0.0, 0.0]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=1, n_active_electrons=1),
        mitigation=MitigationSpec(spam_calibration_enabled=True),
    )
    r = build_qermit_style_mitigation_report(cfg)
    assert r is not None
    kinds = [n.get("kind") for n in r["nodes"]]
    assert "SPAM_readout_calibration_stub" in kinds


def test_mitigation_runtime_spam_trace_matches_graph_order() -> None:
    cfg = ExperimentConfig(
        experiment_id="l1_spam_rt",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H"], coordinates_bohr=[[0.0, 0.0, 0.0]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=1, n_active_electrons=1),
        mitigation=MitigationSpec(spam_calibration_enabled=True),
    )
    graph = build_qermit_style_mitigation_report(cfg)
    assert graph is not None
    out = {"energy_after_variational": -0.5, "mitigation_graph_report": graph}
    rt = execute_mitigation_dag_runtime(cfg, out)
    assert rt is not None
    assert rt["trace"][0]["node"] == "SPAM_readout_calibration_stub"


def test_tensornet_stubs_whitelisted() -> None:
    assert "tensornet_engine_resolved" in PARITY_SNAPSHOT_DOCUMENTED_KEYS
    assert "tensornet_fallback_reason" in PARITY_SNAPSHOT_DOCUMENTED_KEYS
    assert "iqeb_max_rounds" in PARITY_SNAPSHOT_DOCUMENTED_KEYS
    assert "projection_embedding_open_trace" in PARITY_SNAPSHOT_DOCUMENTED_KEYS
    assert "fermion_qubit_mapping" in PARITY_SNAPSHOT_DOCUMENTED_KEYS


def test_tensornet_stub_status_matches_engine_documentation() -> None:
    st = run_cutensornet_expectation_stub(2)
    assert st.get("schema") == "cutensornet_protocol_stub_v1"
    assert "status" in st


def test_pauli_protocol_skips_evaluate_guard() -> None:
    """After five stages, phase is evaluate."""
    h = QubitOperator(((0, "Z"),), 0.4) + QubitOperator((), 0.1)
    from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle

    proto = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=1,
        backend=BackendSpec(name="sim", shots_per_circuit=32),
        pass_bundle=CompilerPassBundle(),
    )
    proto.instantiate()
    proto.build(np.zeros(2), hea_depth=1)
    proto.compile()
    proto.run()
    proto.evaluate()
    assert proto._phase == ProtocolPhase.EVALUATE
