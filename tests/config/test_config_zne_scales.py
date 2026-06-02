"""ZNE scale factor validation."""

from __future__ import annotations

from qchem_stack.config import ExperimentConfig
from qchem_stack.config.mitigation_specs import MitigationZneSpec
from tests.helpers.h2_yaml import h2_yaml_dict

_CAS = {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
_MOLECULE = h2_yaml_dict()["molecule"] | {"coordinates": [[0, 0, 0], [0, 0, 0.74]]}


def test_zne_default_scales_are_positive() -> None:
    zne = MitigationZneSpec(enabled=True)
    assert all(s > 0 for s in zne.scales)
    assert zne.scales[0] == 1.0


def test_zne_custom_scales_roundtrip() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "zne-test",
            "molecule": _MOLECULE,
            "active_space": _CAS,
            "mitigation": {"zne": {"enabled": True, "scales": [1.0, 2.0, 3.0]}},
        }
    )
    assert cfg.mitigation.zne.scales == [1.0, 2.0, 3.0]


def test_zne_disabled_by_default() -> None:
    cfg = ExperimentConfig.model_validate(
        {
            "experiment_id": "zne-off",
            "molecule": _MOLECULE,
            "active_space": _CAS,
        }
    )
    assert cfg.mitigation.zne.enabled is False
