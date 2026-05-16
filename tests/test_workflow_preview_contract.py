"""Workflow preview contract tests (no FastAPI)."""

from __future__ import annotations

from qchem_stack.config import (
    ActiveSpaceSpec,
    ComputableGraphEdgeDecl,
    ComputableGraphEdgeRemove,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
)
from qchem_stack.integrations.workflow_preview import (
    computable_graph_v1,
    computable_graph_v2,
    protocol_stages_preview_v1,
    slim_product_summary_from_pipeline_result,
    workflow_preview_payload,
)
from qchem_stack.protocols.computable import (
    ComputableRef,
    ComputableSpec,
    list_computable_specs_for_config,
    list_computables_for_config,
    refs_from_computable_graph_v2,
    specs_from_computable_graph_v2,
)


def _cfg() -> ExperimentConfig:
    return ExperimentConfig(
        experiment_id="h2_test",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=QuantumSpec(algorithm="vqe", use_pauli_protocol=True),
    )


def test_computable_spec_roundtrip() -> None:
    r = ComputableRef("a", "energy", {"x": 1})
    s = ComputableSpec.from_ref(r)
    r2 = s.to_ref()
    assert r2.name == r.name and r2.kind == r.kind and r2.details == r.details
    specs = list_computable_specs_for_config(_cfg())
    refs = list_computables_for_config(_cfg())
    assert len(specs) == len(refs)


def test_protocol_stages_five_keys() -> None:
    stages = protocol_stages_preview_v1(_cfg())
    assert [s["stage_key"] for s in stages] == [
        "instantiate",
        "build",
        "compile",
        "run",
        "evaluate",
    ]
    assert all("hints" in s for s in stages)


def test_computable_graph_edges_linear() -> None:
    refs = list_computables_for_config(_cfg())
    g = computable_graph_v1(refs)
    assert g["schema"] == "computable_graph_v1"
    assert len(g["nodes"]) == len(refs)
    assert len(g["edges"]) == max(0, len(refs) - 1)


def test_workflow_preview_computables_rich_optional() -> None:
    p0 = workflow_preview_payload(_cfg())
    assert "computables_rich" not in p0
    p1 = workflow_preview_payload(_cfg(), include_computables_rich=True)
    cr = p1.get("computables_rich")
    assert isinstance(cr, dict)
    assert cr.get("schema") == "computables_rich_v1"
    assert cr.get("n_items") == len(cr.get("items", []))


def test_workflow_preview_schema() -> None:
    p = workflow_preview_payload(_cfg())
    assert p["schema"] == "workflow_preview_v1"
    assert p["experiment_id"] == "h2_test"
    cg = p["computable_graph"]
    assert cg.get("schema") == "computable_graph_v2"
    assert cg.get("roots")
    assert p["computable_abstract"]["schema"] == "qchem_computable_abstract_v2"


def test_computable_graph_v2_ground_to_pauli() -> None:
    refs = list_computables_for_config(_cfg())
    g = computable_graph_v2(refs)
    assert g["edge_model"] == "semantic_dataflow_v1"
    edges = g["edges"]
    assert any(
        e["from"] == "computable_0" and e["to"] == "computable_1" and "variational" in e["kind"]
        for e in edges
    )


def test_computable_graph_v2_vqd_after_pauli() -> None:
    q = QuantumSpec(algorithm="vqe", use_pauli_protocol=True, vqd_after_variational=True)
    cfg = ExperimentConfig(
        experiment_id="x",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=q,
    )
    refs = list_computables_for_config(cfg)
    g = computable_graph_v2(refs)
    # vqd is last; depends on pauli (computable_2), not directly only ground
    assert any(
        e["to"] == "computable_2"
        and e["from"] == "computable_1"
        and e["kind"] == "requires_reference_state"
        for e in g["edges"]
    )


def test_computable_graph_v2_vqd_without_pauli() -> None:
    q = QuantumSpec(algorithm="vqe", use_pauli_protocol=False, vqd_after_variational=True)
    cfg = ExperimentConfig(
        experiment_id="x",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=q,
    )
    refs = list_computables_for_config(cfg)
    g = computable_graph_v2(refs)
    assert any(
        e["from"] == "computable_0"
        and e["to"] == "computable_1"
        and e["kind"] == "requires_reference_state"
        for e in g["edges"]
    )


def _semantic_graph_fingerprint(g: dict) -> dict:
    nodes = [
        {"name": n["name"], "kind": n["kind"], "details": dict(n.get("details") or {})}
        for n in g["nodes"]
    ]
    edges = sorted((e["from"], e["to"], e["kind"]) for e in g["edges"])
    roots = sorted(g.get("roots") or [])
    out: dict = {
        "schema": g.get("schema"),
        "edge_model": g.get("edge_model"),
        "nodes": nodes,
        "edges": edges,
        "roots": roots,
    }
    if g.get("declarative_edge_overrides"):
        out["declarative_edge_overrides"] = True
    ve = g.get("variational_execution")
    if isinstance(ve, dict):
        snap = {
            k: ve[k]
            for k in ("schema", "algorithm_factory", "algorithm_label", "dag_note")
            if k in ve
        }
        if snap:
            out["variational_execution"] = snap
    return out


def test_computable_graph_v2_roundtrip_refs_re_emit_identical() -> None:
    cfg = _cfg()
    refs = list_computables_for_config(cfg)
    g = computable_graph_v2(refs, cfg)
    refs2 = refs_from_computable_graph_v2(g)
    assert refs2 == refs
    specs2 = specs_from_computable_graph_v2(g)
    assert [s.to_ref() for s in specs2] == refs
    g2 = computable_graph_v2(refs2, cfg)
    assert _semantic_graph_fingerprint(g) == _semantic_graph_fingerprint(g2)


def test_computable_declarative_extra_and_remove() -> None:
    q = QuantumSpec(
        algorithm="vqe",
        use_pauli_protocol=True,
        vqd_after_variational=True,
        computable_remove_edges=[
            ComputableGraphEdgeRemove(
                from_ref="hamiltonian_expectation_pauli_protocol",
                to_ref="excited_energies_vqd",
            )
        ],
        computable_extra_edges=[
            ComputableGraphEdgeDecl(
                from_ref="ground_state_energy",
                to_ref="excited_energies_vqd",
                kind="custom_fork",
            )
        ],
    )
    cfg = ExperimentConfig(
        experiment_id="decl",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=q,
    )
    refs = list_computables_for_config(cfg)
    g = computable_graph_v2(refs, cfg)
    assert g.get("declarative_edge_overrides") is True
    edges = g["edges"]
    assert not any(
        e["from"] == "computable_1"
        and e["to"] == "computable_2"
        and e["kind"] == "requires_reference_state"
        for e in edges
    )
    assert any(
        e["from"] == "computable_0" and e["to"] == "computable_2" and e["kind"] == "custom_fork"
        for e in edges
    )
    refs2 = refs_from_computable_graph_v2(g)
    g2 = computable_graph_v2(refs2, cfg)
    assert _semantic_graph_fingerprint(g) == _semantic_graph_fingerprint(g2)


def test_slim_summary_api_labels() -> None:
    slim = slim_product_summary_from_pipeline_result(
        {
            "status": "QUEUED",
            "job_kind": "full_pipeline",
            "meta": {
                "experiment_id": "e1",
                "api_workspace_label": "ws",
                "api_project_slug": "proj-a",
            },
        }
    )
    assert slim.get("api_labels", {}).get("api_project_slug") == "proj-a"


def test_slim_summary_partial_and_done() -> None:
    slim_q = slim_product_summary_from_pipeline_result(
        {"status": "QUEUED", "job_kind": "full_pipeline", "meta": {}}
    )
    assert slim_q["partial"] is True
    assert slim_q["schema"] == "run_product_summary_v1"

    row = {
        "status": "DONE",
        "job_kind": "full_pipeline",
        "scf_energy": -1.0,
        "energy_after_variational": -1.1,
        "repro": {
            "experiment_id": "x",
            "run_summary": {"stages_completed": ["scf", "variational"], "quantum_algorithm": "vqe"},
            "parity_snapshot": {"tket_first_compiled_circuit_probe": {}},
        },
    }
    slim_d = slim_product_summary_from_pipeline_result(row)
    assert slim_d["partial"] is False
    assert slim_d["experiment_id"] == "x"
    assert slim_d["scf_energy"] == -1.0
    assert "parity_snapshot_keys" in slim_d


def test_computable_graph_v2_unknown_name_uses_sequential() -> None:
    refs = [
        ComputableRef("custom_a", "energy", {}),
        ComputableRef("custom_b", "energy", {}),
    ]
    g = computable_graph_v2(refs)
    assert g["edges"] == [{"from": "computable_0", "to": "computable_1", "kind": "sequential"}]


def test_workflow_preview_and_graph_mark_yaml_plugin_factory() -> None:
    fac = "qchem_stack.quantum.variational_plugins.examples.echo_runner:echo_runner_factory"
    cfg = ExperimentConfig(
        experiment_id="plugin_wf",
        random_seed=0,
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates_bohr=[[0, 0, 0], [0, 0, 1.4]]),
        active_space=ActiveSpaceSpec(n_active_orbitals=2, n_active_electrons=2),
        quantum=QuantumSpec(
            algorithm="echo_label",
            algorithm_factory=fac,
            use_pauli_protocol=False,
            vqe_depth=1,
        ),
    )
    refs = list_computables_for_config(cfg)
    assert refs[0].details.get("variational_dispatch") == "yaml_algorithm_factory_v1"
    assert refs[0].details.get("algorithm_factory") == fac
    p = workflow_preview_payload(cfg)
    assert p.get("variational_execution", {}).get("schema") == "variational_yaml_plugin_dispatch_v1"
    cg = p["computable_graph"]
    assert cg.get("variational_execution", {}).get("algorithm_factory") == fac


def test_computable_graph_single_node_no_edges() -> None:
    refs = [ComputableRef("only", "energy", {})]
    g = computable_graph_v1(refs)
    assert len(g["nodes"]) == 1
    assert g["edges"] == []
