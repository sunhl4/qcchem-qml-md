"""HTTP API (optional ``fastapi``)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
import json

from fastapi.testclient import TestClient

from qchem_stack.api.app import app


def _have_pyscf() -> bool:
    try:
        import pyscf  # noqa: F401

        return True
    except ImportError:
        return False


def _minimal_experiment_yaml() -> str:
    root = Path(__file__).resolve().parents[1]
    return (root / "configs" / "example_h2.yaml").read_text(encoding="utf-8")


def test_post_run_async_returns_202_and_trace() -> None:
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name
    try:
        client = TestClient(app)
        r = client.post(
            "/v1/runs",
            json={
                "experiment_yaml": _minimal_experiment_yaml(),
                "sync": False,
                "job_db_path": db_path,
            },
            headers={
                "X-Request-ID": "from-test",
                "traceparent": "00-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa-b709e3e139b531b3-01",
            },
        )
        assert r.status_code == 202
        data = r.json()
        assert data.get("schema") == "run_enqueue_response_v1"
        assert data.get("status") == "QUEUED"
        assert data.get("job_id")
        assert data.get("trace_id") == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        assert data.get("client_request_id") == "from-test"
        assert data.get("experiment_id") == "h2_sto3g_001"
        assert r.headers.get("x-trace-id") == "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        assert r.headers.get("x-request-id") == "from-test"
        g = client.get(f"/v1/runs/{data['job_id']}", params={"job_db_path": db_path})
        assert g.status_code == 200
        assert g.json().get("status") == "QUEUED"
        assert g.json().get("job_kind") == "full_pipeline"
        assert g.json().get("meta", {}).get("trace_id") == data.get("trace_id")
        assert g.json().get("meta", {}).get("experiment_id") == "h2_sto3g_001"
        st = client.get(f"/v1/runs/{data['job_id']}/status", params={"job_db_path": db_path})
        assert st.status_code == 200
        stj = st.json()
        assert stj.get("schema") == "job_status_v1"
        assert stj.get("status") == "QUEUED"
        assert stj.get("meta", {}).get("experiment_id") == "h2_sto3g_001"
        ev = client.get(f"/v1/runs/{data['job_id']}/events", params={"job_db_path": db_path})
        assert ev.status_code == 200
        evj = ev.json()
        assert evj.get("schema") == "job_events_v1"
        assert len(evj.get("events") or []) >= 1
        assert evj.get("note") == "sqlite_timeline_json_v1"
        assert (evj.get("events") or [{}])[0].get("kind") == "submitted"
    finally:
        Path(db_path).unlink(missing_ok=True)


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_post_run_sync_returns_job_result_schema_and_json() -> None:
    client = TestClient(app)
    r = client.post(
        "/v1/runs",
        json={"experiment_yaml": _minimal_experiment_yaml(), "sync": True},
        headers={"X-Request-ID": "sync-cli"},
    )
    assert r.status_code == 200
    payload = r.json()
    assert payload.get("schema") == "full_pipeline_job_result_v1"
    json.dumps(payload)
    repro = payload.get("repro") or {}
    assert repro.get("run_context", {}).get("client_request_id") == "sync-cli"
    assert r.headers.get("x-request-id") == "sync-cli"
    assert r.headers.get("x-trace-id")


def test_product_analog_and_workflow_preview() -> None:
    client = TestClient(app)
    pa = client.get("/v1/meta/product-analog")
    assert pa.status_code == 200
    assert pa.json().get("schema") == "product_analog_v1"
    w = client.post(
        "/v1/meta/workflow-preview", json={"experiment_yaml": _minimal_experiment_yaml()}
    )
    assert w.status_code == 200
    b = w.json()
    assert b.get("schema") == "workflow_preview_v1"
    assert len(b.get("protocol_stages") or []) == 5
    cg = b.get("computable_graph") or {}
    assert cg.get("schema") == "computable_graph_v2"
    assert cg.get("edge_model") == "semantic_dataflow_v1"


def test_capability_surface_v1() -> None:
    client = TestClient(app)
    r = client.get("/v1/meta/capability-surface")
    assert r.status_code == 200
    d = r.json()
    assert d.get("schema") == "capability_surface_v1"
    assert d.get("qchem_stack_version")
    assert isinstance(d.get("object_map"), dict) and d["object_map"]
    assert isinstance(d.get("gaps"), list) and d["gaps"]
    diff = d.get("open_stack_differentiators")
    assert isinstance(diff, dict)
    assert diff.get("schema") == "open_stack_differentiators_v1"
    assert (
        isinstance(diff.get("beyond_public_doc_bundle"), list) and diff["beyond_public_doc_bundle"]
    )
    tgt = d.get("tangelo_public_mapping_alias_surface_v1")
    assert isinstance(tgt, dict) and tgt.get("schema") == "tangelo_public_mapping_alias_surface_v1"
    pools = d.get("operator_pool_registry_export_v1")
    assert isinstance(pools, dict) and pools.get("schema") == "operator_pool_registry_export_v1"
    uccsd = d.get("uccsd_mapping_support_matrix_v1")
    assert isinstance(uccsd, dict) and uccsd.get("schema") == "uccsd_mapping_support_matrix_v1"
    gai = d.get("gap_anchor_index_v1")
    assert isinstance(gai, dict) and gai.get("schema") == "inquanto_gap_anchor_index_v1"


def test_capability_surface_matches_inquanto_contract() -> None:
    """Export / parity scripts must stay aligned with the one-shot HTTP surface (single source of truth)."""
    from qchem_stack import __version__
    from qchem_stack.chem.fermion_mapping_registry import (
        tangelo_public_mapping_alias_surface_v1,
    )
    from qchem_stack.protocols.inquanto_contract import (
        inquanto_gap_anchor_index_v1,
        inquanto_gap_categories,
        inquanto_object_map_for_docs,
        mitigation_execution_model_public,
        open_stack_differentiators_public,
    )
    from qchem_stack.quantum.algorithm_registry import algorithm_registry_export
    from qchem_stack.quantum.algorithms.uccsd_vqe import uccsd_mapping_support_matrix_v1
    from qchem_stack.quantum.operator_pool_registry import operator_pool_registry_export_v1
    from qchem_stack.quantum.variational_plugins.registry import variational_registry_export

    client = TestClient(app)
    r = client.get("/v1/meta/capability-surface")
    assert r.status_code == 200
    body = r.json()
    expected = {
        "schema": "capability_surface_v1",
        "qchem_stack_version": __version__,
        "object_map": inquanto_object_map_for_docs(),
        "gaps": inquanto_gap_categories(),
        "gap_anchor_index_v1": inquanto_gap_anchor_index_v1(),
        "mitigation_execution_model": mitigation_execution_model_public(),
        "open_stack_differentiators": open_stack_differentiators_public(),
        "tangelo_public_mapping_alias_surface_v1": tangelo_public_mapping_alias_surface_v1(),
        "operator_pool_registry_export_v1": operator_pool_registry_export_v1(),
        "algorithm_registry_export_v1": algorithm_registry_export(),
        "variational_registry_export_v1": variational_registry_export(),
        "uccsd_mapping_support_matrix_v1": uccsd_mapping_support_matrix_v1(),
    }
    assert body == expected


def test_post_project_slug_meta_and_list_filter() -> None:
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name
    try:
        client = TestClient(app)
        p = client.post(
            "/v1/runs",
            json={
                "experiment_yaml": _minimal_experiment_yaml(),
                "sync": False,
                "job_db_path": db_path,
                "workspace_label": "lab-a",
                "project_slug": "mol-opt-2026",
            },
        )
        assert p.status_code == 202
        jid = p.json()["job_id"]
        row = client.get(f"/v1/runs/{jid}", params={"job_db_path": db_path}).json()
        m = row.get("meta") or {}
        assert m.get("api_workspace_label") == "lab-a"
        assert m.get("api_project_slug") == "mol-opt-2026"
        lst = client.get(
            "/v1/runs",
            params={"job_db_path": db_path, "api_project_slug": "mol-opt-2026", "limit": 5},
        ).json()
        assert any(j.get("job_id") == jid for j in (lst.get("jobs") or []))
        sm = client.get(f"/v1/runs/{jid}/summary", params={"job_db_path": db_path}).json()
        assert sm.get("api_labels", {}).get("api_project_slug") == "mol-opt-2026"
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_run_summary_ux_partial_while_queued() -> None:
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name
    try:
        client = TestClient(app)
        p = client.post(
            "/v1/runs",
            json={
                "experiment_yaml": _minimal_experiment_yaml(),
                "sync": False,
                "job_db_path": db_path,
            },
        )
        assert p.status_code == 202
        jid = p.json()["job_id"]
        s = client.get(f"/v1/runs/{jid}/summary", params={"job_db_path": db_path})
        assert s.status_code == 200
        sj = s.json()
        assert sj.get("schema") == "run_product_summary_v1"
        assert sj.get("partial") is True
        assert sj.get("job_id") == jid
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_health_ready_ok() -> None:
    client = TestClient(app)
    r = client.get("/health/ready")
    assert r.status_code == 200
    body = r.json()
    assert body.get("status") == "ready"
    assert "job_db_default" in body


def test_job_list_includes_limit_offset() -> None:
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name
    try:
        client = TestClient(app)
        client.post(
            "/v1/runs",
            json={
                "experiment_yaml": _minimal_experiment_yaml(),
                "sync": False,
                "job_db_path": db_path,
            },
        )
        r = client.get("/v1/runs", params={"job_db_path": db_path, "limit": 5, "offset": 0})
        assert r.status_code == 200
        body = r.json()
        assert body.get("limit") == 5
        assert body.get("offset") == 0
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_health_ok() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_post_run_invalid_yaml_400() -> None:
    client = TestClient(app)
    r = client.post(
        "/v1/runs",
        json={"experiment_yaml": "{\n  bad_indent: [", "sync": False, "job_db_path": None},
    )
    assert r.status_code == 400
    assert "YAML" in (r.json().get("detail") or "")


def test_post_run_invalid_config_422() -> None:
    client = TestClient(app)
    r = client.post(
        "/v1/runs",
        json={
            "experiment_yaml": "quantum:\n  vqe_depth: not_a_number\n",
            "sync": False,
        },
    )
    assert r.status_code == 422
    detail = r.json().get("detail")
    assert isinstance(detail, list)


def test_list_runs_after_enqueue() -> None:
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name
    try:
        client = TestClient(app)
        client.post(
            "/v1/runs",
            json={
                "experiment_yaml": _minimal_experiment_yaml(),
                "sync": False,
                "job_db_path": db_path,
            },
        )
        r = client.get("/v1/runs", params={"job_db_path": db_path, "limit": 10})
        assert r.status_code == 200
        body = r.json()
        assert body.get("schema") == "job_list_v1"
        assert len(body.get("jobs") or []) >= 1
        assert body["jobs"][0].get("job_kind") == "full_pipeline"
        rf = client.get(
            "/v1/runs",
            params={"job_db_path": db_path, "experiment_id": "h2_sto3g_001", "limit": 10},
        )
        assert rf.status_code == 200
        assert len(rf.json().get("jobs") or []) >= 1
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_parity_gaps_meta() -> None:
    client = TestClient(app)
    r = client.get("/v1/meta/parity-gaps")
    assert r.status_code == 200
    d = r.json()
    assert d.get("schema") == "inquanto_gap_export_v1"
    assert d.get("qchem_stack_version")
    gaps = d.get("gaps")
    assert isinstance(gaps, list) and gaps
    gai = d.get("gap_anchor_index_v1")
    assert isinstance(gai, dict)
    assert gai.get("schema") == "inquanto_gap_anchor_index_v1"


def test_computables_preview_v1() -> None:
    client = TestClient(app)
    r = client.post(
        "/v1/meta/computables-preview", json={"experiment_yaml": _minimal_experiment_yaml()}
    )
    assert r.status_code == 200
    b = r.json()
    assert b.get("schema") == "computables_preview_v1"
    assert b.get("experiment_id") == "h2_sto3g_001"
    ca = b.get("computable_abstract") or {}
    assert ca.get("schema") == "qchem_computable_abstract_v2"
    assert isinstance(b.get("computables"), list) and b["computables"]


def test_meta_queue_stats() -> None:
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name
    try:
        client = TestClient(app)
        r0 = client.get("/v1/meta/queue-stats", params={"job_db_path": db_path})
        assert r0.status_code == 200
        assert r0.json().get("schema") == "queue_stats_v1"
        client.post(
            "/v1/runs",
            json={
                "experiment_yaml": _minimal_experiment_yaml(),
                "sync": False,
                "job_db_path": db_path,
            },
        )
        r1 = client.get("/v1/meta/queue-stats", params={"job_db_path": db_path})
        assert r1.status_code == 200
        assert int((r1.json().get("counts") or {}).get("QUEUED", 0)) >= 1
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_repro_endpoint_409_while_queued() -> None:
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name
    try:
        client = TestClient(app)
        p = client.post(
            "/v1/runs",
            json={
                "experiment_yaml": _minimal_experiment_yaml(),
                "sync": False,
                "job_db_path": db_path,
            },
        )
        assert p.status_code == 202
        jid = p.json()["job_id"]
        r = client.get(f"/v1/runs/{jid}/repro", params={"job_db_path": db_path})
        assert r.status_code == 409
        assert (r.json().get("detail") or {}).get("status") == "QUEUED"
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_post_workspace_label_meta_and_list_filter() -> None:
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = f.name
    try:
        client = TestClient(app)
        p = client.post(
            "/v1/runs",
            json={
                "experiment_yaml": _minimal_experiment_yaml(),
                "sync": False,
                "job_db_path": db_path,
                "workspace_label": " competitor-demo ",
            },
        )
        assert p.status_code == 202
        jid = p.json()["job_id"]
        row = client.get(f"/v1/runs/{jid}", params={"job_db_path": db_path}).json()
        assert row.get("meta", {}).get("api_workspace_label") == " competitor-demo ".strip()
        lst = client.get(
            "/v1/runs",
            params={"job_db_path": db_path, "api_workspace_label": "competitor-demo", "limit": 5},
        ).json()
        assert any(j.get("job_id") == jid for j in (lst.get("jobs") or []))
    finally:
        Path(db_path).unlink(missing_ok=True)


def test_list_runs_invalid_status_400() -> None:
    with tempfile.TemporaryDirectory() as ddir:
        db_path = f"{ddir}/j.sqlite"
        client = TestClient(app)
        r = client.get("/v1/runs", params={"job_db_path": db_path, "status": "BOGUS"})
        assert r.status_code == 400


def test_status_unknown_404() -> None:
    with tempfile.TemporaryDirectory() as d:
        db_path = f"{d}/empty.sqlite"
        client = TestClient(app)
        r = client.get("/v1/runs/nonexistent/status", params={"job_db_path": db_path})
        assert r.status_code == 404


def test_get_run_unknown_404() -> None:
    with tempfile.TemporaryDirectory() as d:
        db_path = f"{d}/empty.sqlite"
        client = TestClient(app)
        r = client.get("/v1/runs/nonexistent-job-id", params={"job_db_path": db_path})
        assert r.status_code == 404


def test_capability_surface_has_mitigation_execution_model() -> None:
    client = TestClient(app)
    r = client.get("/v1/meta/capability-surface")
    assert r.status_code == 200
    j = r.json()
    assert j.get("schema") == "capability_surface_v1"
    mm = j.get("mitigation_execution_model")
    assert isinstance(mm, dict)
    assert mm.get("schema") == "mitigation_execution_model_v1"


def test_workflow_preview_include_computables_rich() -> None:
    client = TestClient(app)
    r = client.post(
        "/v1/meta/workflow-preview",
        json={"experiment_yaml": _minimal_experiment_yaml(), "include_computables_rich": True},
    )
    assert r.status_code == 200
    body = r.json()
    cr = body.get("computables_rich")
    assert isinstance(cr, dict)
    assert cr.get("schema") == "computables_rich_v1"
