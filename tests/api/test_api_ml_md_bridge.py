"""HTTP ML / MD bridge meta routes (optional ``fastapi``)."""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from qchem_stack.api.app import create_app

_SAMPLE_QMEF = {
    "frames": [
        {
            "atomic_numbers": [1, 1],
            "positions_bohr": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
            "energy_hartree": -1.0,
            "forces_hartree_bohr": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
            "method_tag": "RHF",
        }
    ],
    "provenance_yaml": "test: api\n",
}


def test_ml_md_bridge_surface_v1() -> None:
    client = TestClient(create_app())
    r = client.get("/v1/meta/ml-md-bridge")
    assert r.status_code == 200
    d = r.json()
    assert d.get("schema") == "ml_md_bridge_surface_v1"
    assert d.get("qchem_stack_version")
    qmf = d.get("qmframe_fields")
    assert isinstance(qmf, dict) and "atomic_numbers" in qmf
    routes = d.get("http_routes") or {}
    assert routes.get("surface") == "GET /v1/meta/ml-md-bridge"
    assert "repro_attachment" in d


def test_qmef_validate_ok_and_invalid() -> None:
    client = TestClient(create_app())
    ok = client.post("/v1/meta/qmef-validate", json={"qmef": _SAMPLE_QMEF})
    assert ok.status_code == 200
    body = ok.json()
    assert body.get("schema") == "qmef_validate_v1"
    assert body.get("n_frames") == 1
    assert body.get("qmframe_field_names")

    bad = client.post(
        "/v1/meta/qmef-validate",
        json={"qmef": {"frames": [{"atomic_numbers": "not-a-list"}]}},
    )
    assert bad.status_code == 422


def test_trainer_stub_fit_via_http() -> None:
    client = TestClient(create_app())
    r = client.post(
        "/v1/meta/ml-md-trainer-stub-fit",
        json={"qmef": _SAMPLE_QMEF, "hyperparams": {"lr": 1e-3}},
    )
    assert r.status_code == 200
    out = r.json()
    assert out.get("schema") == "ml_md_trainer_stub_fit_v1"
    art = out.get("artifact") or {}
    assert art.get("path") == "stub_model.pt"
    assert art.get("metrics", {}).get("rmse_energy_mHa") == 0.0
    assert art.get("meta", {}).get("lr") == 1e-3
    assert art.get("meta", {}).get("n_frames") == 1


def test_product_surface_lists_ml_md_bridge_route() -> None:
    client = TestClient(create_app())
    pa = client.get("/v1/meta/product-surface").json()
    assert pa.get("ml_md_bridge") == "/v1/meta/ml-md-bridge"
    notes = "\n".join(str(x) for x in (pa.get("capability_notes") or []))
    assert "ml-md-bridge" in notes
