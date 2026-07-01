"""Additional md_bridge unit tests targeting coverage gaps (no qmlff/jax required)."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from qchem_stack.exceptions import PipelineError
from qchem_stack.md_bridge.classical_h2_ff import (
    ClassicalH2MorseModel,
    ClassicalH2MorseParams,
    _bond_length_ang,
    build_classical_h2_handle,
    train_classical_h2_on_qmef,
)
from qchem_stack.md_bridge.qchem_labeler import (
    LabelingFailure,
    LabelingResult,
    label_geometries_with_pipeline,
    merge_qmef_datasets,
)
from qchem_stack.md_bridge.qmlff_builders import (
    atomic_number_to_symbol,
    build_force_field_handle,
    symbol_to_atomic_number,
)
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame


def _h2_frame(r_bohr: float = 0.74, energy: float = -1.0) -> QMFrame:
    return QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, r_bohr]],
        energy_hartree=energy,
        forces_hartree_bohr=[],
        method_tag="test",
    )


def test_symbol_lookup_helpers() -> None:
    assert atomic_number_to_symbol(1) == "H"
    assert atomic_number_to_symbol(999) == "X"
    assert symbol_to_atomic_number("H") == 1
    assert symbol_to_atomic_number("Xy") == 0


def test_build_force_field_handle_classical_h2() -> None:
    handle = build_force_field_handle(["H"], backend="classical_h2")
    assert handle.backend == "classical_h2"
    idx = handle.species_indices([1, 1])
    assert idx.tolist() == [0, 0]


def test_classical_h2_morse_model_parameter_roundtrip() -> None:
    model = ClassicalH2MorseModel()
    model.set_parameters({"de_ev": 5.0, "a_inv_ang": 2.0, "re_ang": 0.8, "shift_ev": -1.0})
    params = model.get_parameters()
    assert params["de_ev"] == pytest.approx(5.0)
    e = ClassicalH2MorseModel._morse_energy_ev(
        np.array([0.74]), ClassicalH2MorseParams(re_ang=0.74)
    )
    assert float(e[0]) < 0


def test_bond_length_ang_and_train_errors() -> None:
    assert _bond_length_ang(np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]])) > 0
    with pytest.raises(ValueError, match="2 atoms"):
        _bond_length_ang(np.array([[0.0, 0.0, 0.0]]))
    with pytest.raises(ValueError, match="at least one frame"):
        train_classical_h2_on_qmef(build_classical_h2_handle(["H"]), QMEFDataset(frames=[]))
    with pytest.raises(ValueError, match="at least 2 diatomic"):
        train_classical_h2_on_qmef(
            build_classical_h2_handle(["H"]), QMEFDataset(frames=[_h2_frame()])
        )


def test_species_indices_unknown_raises() -> None:
    handle = build_classical_h2_handle(["H"])
    with pytest.raises(ValueError, match="species"):
        handle.species_indices([6, 6])


def test_merge_qmef_datasets_empty_and_dedupe_off() -> None:
    assert merge_qmef_datasets().frames == []
    single = QMEFDataset(frames=[_h2_frame()], provenance_yaml="a\n")
    assert merge_qmef_datasets(single, dedupe_decimals=None) is single


def test_merge_qmef_datasets_skips_empty_frame_blocks() -> None:
    empty = QMEFDataset(frames=[], provenance_yaml="empty\n")
    merged = merge_qmef_datasets(QMEFDataset(frames=[_h2_frame()], provenance_yaml="a\n"), empty)
    assert len(merged.frames) == 1
    assert "empty" in merged.provenance_yaml


def test_label_geometries_missing_yaml(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        label_geometries_with_pipeline(tmp_path / "missing.yaml", [])


def test_label_geometries_failure_isolation(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    yaml_path = tmp_path / "exp.yaml"
    yaml_path.write_text("experiment_id: x\n", encoding="utf-8")
    base_frame = _h2_frame()
    base_result = LabelingResult(
        dataset=QMEFDataset(frames=[base_frame], provenance_yaml="p\n"),
        failures=[],
        epistemic_bound="e",
        primary_repro_config_sha256_prefix="sha",
    )
    extra_ok = LabelingResult(
        dataset=QMEFDataset(frames=[base_frame, _h2_frame(r_bohr=1.2)], provenance_yaml="p\n"),
        failures=[],
        epistemic_bound="e",
        primary_repro_config_sha256_prefix="sha",
    )

    calls = {"n": 0}

    def _fake_run(*_a, **kwargs):
        calls["n"] += 1
        extras = kwargs.get("extras") or []
        if calls["n"] == 1:
            raise RuntimeError("batch boom")
        if len(extras) == 0:
            return base_result
        if extras == [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.2]]]:
            return extra_ok
        raise RuntimeError("geom fail")

    monkeypatch.setattr("qchem_stack.config.load_experiment_config", lambda _p: MagicMock())
    monkeypatch.setattr("qchem_stack.md_bridge.qchem_labeler._run_with_extras", _fake_run)

    res = label_geometries_with_pipeline(
        yaml_path,
        [[[0.0, 0.0, 0.0], [0.0, 0.0, 1.2]], [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]],
        failure_isolation=True,
    )
    assert len(res.dataset.frames) == 2
    assert len(res.failures) == 1
    assert isinstance(res.failures[0], LabelingFailure)


def test_energy_hartree_scf_missing_raises() -> None:
    from qchem_stack.config import ExperimentConfig, MdMlExportSpec
    from qchem_stack.md_bridge.from_pipeline_extract import energy_hartree_from_pipeline_out

    cfg = ExperimentConfig.model_validate(
        {
            "schema_version": "2",
            "experiment_id": "e",
            "random_seed": 0,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0, 0, 0], [0, 0, 0.74]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "active_space": {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
            "md_ml_export": MdMlExportSpec(energy_reference="scf").model_dump(),
        }
    )
    with pytest.raises(PipelineError, match="scf_energy"):
        energy_hartree_from_pipeline_out(cfg, {})


def test_train_classical_h2_skips_non_diatomic_frames() -> None:
    frames = [_h2_frame(r_bohr=0.9, energy=-1.0), _h2_frame(r_bohr=1.1, energy=-1.01)]
    frames.append(
        QMFrame(
            atomic_numbers=[1, 1, 1],
            positions_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [0.0, 1.0, 0.0]],
            energy_hartree=-1.5,
            forces_hartree_bohr=[],
            method_tag="skip",
        )
    )
    handle = train_classical_h2_on_qmef(
        build_classical_h2_handle(["H"]), QMEFDataset(frames=frames)
    )
    assert handle.train_meta["n_train_frames"] == 2


def test_hf_nuclear_forces_with_pyscf() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.reference_factory import pyscf_rhf_result_from_config
    from qchem_stack.config import ExperimentConfig
    from qchem_stack.md_bridge.from_pipeline_extract import (
        hf_nuclear_forces_neg_gradient_hartree_bohr,
    )

    cfg = ExperimentConfig.model_validate(
        {
            "schema_version": "2",
            "experiment_id": "e",
            "random_seed": 0,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0, 0, 0], [0, 0, 0.74]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "scf": {"driver": "pyscf", "method": "RHF"},
            "active_space": {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}},
            "quantum": {"algorithm": "vqe", "vqe": {"depth": 1, "maxiter": 5}},
        }
    )
    rhf = pyscf_rhf_result_from_config(cfg)
    forces = hf_nuclear_forces_neg_gradient_hartree_bohr(rhf, "RHF")
    assert forces is not None
    assert len(forces) == 2


def test_from_pipeline_extract_helpers() -> None:
    from qchem_stack.md_bridge.from_pipeline_extract import as_out_dict, protocol_hash_prefix

    assert as_out_dict({"scf_energy": -1.0})["scf_energy"] == -1.0
    assert protocol_hash_prefix({}) == ""
    assert (
        protocol_hash_prefix(
            {"repro": {"parity_snapshot": {"compiler_bundle_signature": "abc123"}}}
        )
        == "abc123"
    )


def test_pipeline_runner_registry_injection() -> None:
    from qchem_stack.exceptions import PipelineError
    from qchem_stack.md_bridge.pipeline_runner import (
        register_pipeline_runner,
        reset_pipeline_runner,
        resolve_pipeline_runner,
    )

    reset_pipeline_runner()
    with pytest.raises(PipelineError, match="No pipeline runner registered"):
        resolve_pipeline_runner()

    def _fake(**kwargs):
        return {"ok": True, **kwargs}

    register_pipeline_runner(_fake)
    runner = resolve_pipeline_runner()
    assert runner(cfg=None)["ok"] is True
    reset_pipeline_runner()
    import qchem_stack.orchestration  # noqa: F401 — restore default runner


def test_active_learning_max_std_proxy() -> None:
    import numpy as np

    from qchem_stack.md_bridge.active_learning import (
        ActiveLearningLoop,
        SurrogateEnergyModel,
        max_std_proxy,
    )

    X = np.array([[0.0], [1.0], [2.0]])
    y = np.array([0.0, 1.0, 2.0])
    model = SurrogateEnergyModel()
    model.fit(X, y)
    loop = ActiveLearningLoop(pool_features=X, acquisition=max_std_proxy)
    idx = loop.next_index(model)
    assert idx in (0, 1, 2)
