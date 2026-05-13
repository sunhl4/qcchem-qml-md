"""Machine-readable ML / MD bridge surface (HTTP helpers + payload builders)."""

from __future__ import annotations

from typing import Any

from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame


def ml_md_bridge_surface_v1() -> dict[str, Any]:
    """
    One-shot JSON for consoles: QMEF schema hooks, stub trainer, exporters, lightweight ML surrogate paths.

    Keeps narrative in ``docs/md_bridge_repro_freeze_list.md`` — this blob is for dashboards only.
    """
    from qchem_stack import __version__

    qmframe_fields: dict[str, str] = {}
    for name, finfo in QMFrame.model_fields.items():
        desc = getattr(finfo, "description", None) or ""
        qmframe_fields[name] = desc

    return {
        "schema": "ml_md_bridge_surface_v1",
        "qchem_stack_version": __version__,
        "qmframe_fields": qmframe_fields,
        "qmef_dataset": {
            "model": "qchem_stack.md_bridge.schema.QMEFDataset",
            "keys": ["frames", "provenance_yaml"],
        },
        "trainer_stub": {
            "class": "qchem_stack.md_bridge.contracts.StubTorchMLIPTrainer",
            "protocol": "qchem_stack.md_bridge.contracts.ForceFieldTrainerProtocol",
            "methods": ["fit", "export_openmm", "export_lammps", "score"],
        },
        "exporters": {
            "extended_xyz": "qchem_stack.md_bridge.exporter.export_extended_xyz",
            "training_npz_stub": "qchem_stack.md_bridge.exporter.write_hdf5_stub",
            "nequip_config_stub": "qchem_stack.md_bridge.hooks.write_nequip_yaml_stub",
            "mace_config_stub": "qchem_stack.md_bridge.hooks.write_mace_yaml_stub",
        },
        "surrogate_active_learning": {
            "ridge_energy_surrogate": "qchem_stack.ml.surrogate.SurrogateEnergyModel",
            "discrete_pool_loop": "qchem_stack.ml.active_learning.ActiveLearningLoop",
        },
        "http_routes": {
            "surface": "GET /v1/meta/ml-md-bridge",
            "validate_qmef": "POST /v1/meta/qmef-validate",
            "trainer_stub_fit": "POST /v1/meta/ml-md-trainer-stub-fit",
        },
        "repro_attachment": (
            "After pipeline: repro.qmef_ml_attachment_v1 when YAML sets md_ml_export.attach_single_frame_to_repro "
            "(primary frame + optional extra_coordinates_bohr / trajectory_theory_level / energy_reference incl. pauli_protocol)."
        ),
        "docs": ["docs/md_bridge_repro_freeze_list.md"],
    }


def validate_qmef_dict(raw: dict[str, Any]) -> QMEFDataset:
    """Parse user JSON into :class:`QMEFDataset`; raises :class:`pydantic.ValidationError` on failure."""
    return QMEFDataset.model_validate(raw)


def qmef_validate_response_dict(ds: QMEFDataset) -> dict[str, Any]:
    """Normalized JSON-safe payload for ``POST /v1/meta/qmef-validate``."""
    return {
        "schema": "qmef_validate_v1",
        "n_frames": len(ds.frames),
        "qmef": ds.model_dump(mode="json"),
        "qmframe_field_names": list(QMFrame.model_fields.keys()),
    }


def trainer_stub_fit_response_dict(ds: QMEFDataset, hyperparams: dict[str, Any]) -> dict[str, Any]:
    """Run :class:`StubTorchMLIPTrainer` in-process; no server-side artifact files."""
    from qchem_stack.md_bridge.contracts import StubTorchMLIPTrainer

    trainer = StubTorchMLIPTrainer()
    art = trainer.fit(ds, hyperparams)
    return {
        "schema": "ml_md_trainer_stub_fit_v1",
        "artifact": {
            "path": art.path,
            "metrics": art.metrics,
            "meta": art.meta,
        },
    }


__all__ = [
    "ml_md_bridge_surface_v1",
    "qmef_validate_response_dict",
    "trainer_stub_fit_response_dict",
    "validate_qmef_dict",
]
