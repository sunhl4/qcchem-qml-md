"""Classical (no jax-md) coverage for md_bridge HTTP helpers."""

from __future__ import annotations

from qchem_stack.md_bridge.constants import FS_TO_PS, MORSE_LOWER_DE
from qchem_stack.md_bridge.http_surface import (
    ml_md_bridge_surface_v1,
    qmef_validate_response_dict,
    trainer_stub_fit_response_dict,
    validate_qmef_dict,
)
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame


def test_constants_exports() -> None:
    assert FS_TO_PS == 1e-3
    assert MORSE_LOWER_DE > 0


def test_ml_md_bridge_surface_v1_shape() -> None:
    surf = ml_md_bridge_surface_v1()
    assert surf.get("schema") == "ml_md_bridge_surface_v1"
    assert "qmframe_fields" in surf
    assert "http_routes" in surf


def test_validate_qmef_dict_and_responses() -> None:
    raw = {
        "frames": [
            {
                "atomic_numbers": [1, 1],
                "positions_bohr": [[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]],
                "energy_hartree": -1.0,
            }
        ],
        "provenance_yaml": "test: true\n",
    }
    ds = validate_qmef_dict(raw)
    assert isinstance(ds, QMEFDataset)
    val = qmef_validate_response_dict(ds)
    assert val["schema"] == "qmef_validate_v1"
    assert val["n_frames"] == 1
    fit = trainer_stub_fit_response_dict(ds, {"epochs": 1})
    assert fit["schema"] == "ml_md_trainer_stub_fit_v1"
    assert fit["artifact"]["path"]


def test_qmframe_model_fields_documented() -> None:
    assert "atomic_numbers" in QMFrame.model_fields
