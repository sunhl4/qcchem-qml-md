"""Unit tests for md_bridge.from_pipeline attachment builders (mock runner)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from qchem_stack.config import ExperimentConfig
from qchem_stack.contracts.schema_ids import QMEF_ML_ATTACHMENT_V1
from qchem_stack.md_bridge.from_pipeline import build_qmef_ml_attachment_repro_block
from qchem_stack.md_bridge.schema import QMFrame


def _h2_cfg() -> ExperimentConfig:
    return ExperimentConfig.model_validate(
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
            "md_ml_export": {
                "attach_single_frame_to_repro": True,
                "energy_reference": "variational",
            },
        }
    )


def test_build_qmef_ml_attachment_repro_block_primary_frame(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference

    cfg = _h2_cfg()
    out = {
        "scf_energy": -1.1,
        "energy_after_variational": -1.2,
        "repro": {"config_sha256_prefix": "abc", "parity_snapshot": {}},
    }
    reference = MagicMock(spec=ClassicalMeanFieldReference)
    mock_rhf = MagicMock()
    mock_rhf.e_tot = -1.1
    mock_rhf.mol = MagicMock()
    mock_rhf.mol.atom = [(1, (0, 0, 0)), (1, (0, 0, 0.74))]
    frame = QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]],
        energy_hartree=-1.2,
        forces_hartree_bohr=[],
        charge=0,
        multiplicity=1,
        box=None,
        method_tag="test",
        active_space_hash="h",
        protocol_hash="p",
        repro_config_sha256_prefix="abc",
        backend_noise_tag="statevector",
    )
    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.as_pyscf_rhf",
        lambda _ref: mock_rhf,
    )
    monkeypatch.setattr(
        "qchem_stack.md_bridge.from_pipeline.primary_qmframe",
        lambda _cfg, _out, _rhf: frame,
    )
    block = build_qmef_ml_attachment_repro_block(cfg, out, reference)
    assert block["schema"] == QMEF_ML_ATTACHMENT_V1
    assert block["frame_meta"][0]["index"] == 0
    assert len(block["dataset"]["frames"]) == 1
