"""InQuanto *public* contract helpers (no closed-source dependency)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from qchem_stack.config import ActiveSpaceSpec, ExperimentConfig, MoleculeSpec, QuantumSpec
from qchem_stack.protocols.inquanto_contract import (
    PAULI_PATH_DISABLED,
    PAULI_PATH_EXACT,
    PAULI_PATH_QISKIT_COUNTS,
    PAULI_PATH_STATEVECTOR_SHOT_SIM,
    classify_pauli_expectation_path,
    inquanto_gap_categories,
    inquanto_object_map_for_docs,
    pauli_protocol_expectation_path_for_config,
    protocol_expectation_semantics_public,
    validate_inquanto_gap_categories,
)


def _exp_cfg(**q: object) -> ExperimentConfig:
    return ExperimentConfig(
        experiment_id="t",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=QuantumSpec(**q),
    )


def test_classify_pauli_paths() -> None:
    q0 = QuantumSpec()
    assert classify_pauli_expectation_path(q0) == PAULI_PATH_EXACT
    assert (
        classify_pauli_expectation_path(QuantumSpec(use_pauli_protocol=False))
        == PAULI_PATH_DISABLED
    )
    assert (
        classify_pauli_expectation_path(QuantumSpec(run_sampled_pauli_protocol=True))
        == PAULI_PATH_STATEVECTOR_SHOT_SIM
    )
    assert (
        classify_pauli_expectation_path(QuantumSpec(run_qiskit_shots_pauli_protocol=True))
        == PAULI_PATH_QISKIT_COUNTS
    )


def test_pauli_path_for_experiment() -> None:
    p = pauli_protocol_expectation_path_for_config(_exp_cfg())
    assert p == PAULI_PATH_EXACT
    p2 = pauli_protocol_expectation_path_for_config(_exp_cfg(run_qiskit_shots_pauli_protocol=True))
    assert p2 == PAULI_PATH_QISKIT_COUNTS


def test_inquanto_map_and_gaps_non_empty() -> None:
    m = inquanto_object_map_for_docs()
    assert "Protocol (five stages)" in m
    assert "Noise mitigation (Qermit-style)" in m
    assert "YAML quantum.algorithm_factory (variational plugins)" in m
    assert "Operator pool registry (ADAPT/IQEB)" in m
    assert "Molecule geometry (Cartesian vs Z-matrix)" in m
    assert "Algorithm*QPE (track)" in m
    assert "AlgorithmVQS / AlgorithmMcLachlan*" in m
    assert "IntegralSolver (Tangelo toolbox shape)" in m
    assert "Fermion→qubit names (Tangelo / tutorial aliases)" in m
    g = inquanto_gap_categories()
    assert any(x.get("id") == "cloud_nexus" for x in g)
    assert any(x.get("id") == "http_submit_poll_workspace" for x in g)
    assert any(x.get("id") == "evaluate_support_set" for x in g)
    assert any(x.get("id") == "adapt_iqeb_operator_pool_surface" for x in g)
    assert any(x.get("id") == "compiler_pass_bundle" for x in g)
    assert any(x.get("id") == "integrations_closure_layer" for x in g)
    comp = next(x for x in g if x.get("id") == "composable_computable")
    assert comp.get("status") == "analog_v2_semantic_graph_rich_optional"
    qg = next(x for x in g if x.get("id") == "qermit_graph")
    assert isinstance(qg.get("mitigation_execution_model"), dict)
    assert qg["mitigation_execution_model"].get("schema") == "mitigation_execution_model_v1"


def test_gap_categories_unique_ids_and_anchors() -> None:
    g = inquanto_gap_categories()
    ids = [x.get("id") for x in g]
    assert len(ids) == len(set(ids))
    for row in g:
        assert row.get("parity_matrix_anchor")


def test_gap_categories_contract_validator_has_no_errors() -> None:
    assert validate_inquanto_gap_categories() == []


def test_parity_export_stable_keys_present() -> None:
    from qchem_stack.protocols.inquanto_contract import PARITY_EXPORT_V2_STABLE_KEYS

    cfg = _exp_cfg()
    from qchem_stack.chem.bridges.facade import molecular_system_from_experiment
    from qchem_stack.orchestration.pipeline import build_excited_resource_summary_for_export
    from qchem_stack.protocols.computable import computables_export_dict

    ms = molecular_system_from_experiment(cfg)
    geo = str(ms.meta.get("geometry_source") or "cartesian")

    blob = {
        "parity_export_schema_version": "2",
        "experiment_id": cfg.experiment_id,
        "computable_abstract": computables_export_dict(cfg, protocol_counts=None),
        "excited_resource_from_config": build_excited_resource_summary_for_export(cfg),
        "inquanto_gap_categories": inquanto_gap_categories(),
        "iqeb_implementation_path": "qchem_stack.quantum.algorithms.iqeb.IQEBVQE",
        "pauli_protocol_expectation_path": pauli_protocol_expectation_path_for_config(cfg),
        "protocol_expectation_semantics_v1": protocol_expectation_semantics_public(),
        "geometry_source": geo,
        "embedding": cfg.embedding.model_dump(),
    }
    assert PARITY_EXPORT_V2_STABLE_KEYS <= set(blob.keys())


def test_open_stack_differentiators_schema() -> None:
    from qchem_stack.protocols.inquanto_contract import open_stack_differentiators_public

    d = open_stack_differentiators_public()
    assert d.get("schema") == "open_stack_differentiators_v1"
    assert isinstance(d.get("scope_excludes"), list) and d["scope_excludes"]
    rows = d.get("beyond_public_doc_bundle")
    assert isinstance(rows, list) and len(rows) >= 3
    assert any(row.get("id") == "molecular_geometry_lineage_l1" for row in rows)
    assert any(row.get("id") == "tangelo_fermion_mapping_alias_surface" for row in rows)
    for row in rows:
        assert row.get("id")
        assert row.get("summary")
        assert isinstance(row.get("evidence_modules"), list)


def test_both_shot_flags_invalid_in_config() -> None:
    with pytest.raises(ValidationError):
        _exp_cfg(run_sampled_pauli_protocol=True, run_qiskit_shots_pauli_protocol=True)
