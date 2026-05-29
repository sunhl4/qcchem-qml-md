"""Backend profile selection (UQC cloud, mock, Cirq, Braket, ...)."""

from __future__ import annotations

import pytest

from qchem_stack.backends.profiles import (
    apply_backend_profile,
    backend_profile_catalog_v1,
    get_backend_profile,
    list_backend_profile_ids,
)
from qchem_stack.config import load_experiment_config
from tests.helpers.paths import configs_path


def test_backend_profile_catalog_lists_uqc_and_simulators() -> None:
    ids = list_backend_profile_ids()
    assert "uqc_cloud" in ids
    assert "uqc_mock" in ids
    assert "cirq" in ids
    assert "braket" in ids
    cat = backend_profile_catalog_v1()
    assert cat["schema"] == "backend_profile_catalog_v1"
    assert len(cat["profiles"]) >= len(ids)


def test_apply_uqc_cloud_profile() -> None:
    cfg = load_experiment_config(configs_path("example_h2_uqc_mock_md_ml.yaml"))
    prof = apply_backend_profile(cfg, "uqc_cloud")
    assert prof.profile_id == "uqc_cloud"
    assert cfg.backend.provider == "uqc"
    assert cfg.backend.uqc_mode == "real"
    assert cfg.backend.meta.get("uqc_target") == "iontrap-sim"


def test_apply_cirq_profile() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    prof = apply_backend_profile(cfg, "cirq")
    assert prof.provider == "cirq"
    assert cfg.backend.provider == "cirq"


def test_unknown_profile_raises() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    with pytest.raises(ValueError, match="Unknown backend profile"):
        apply_backend_profile(cfg, "not_a_backend")


def test_get_backend_profile() -> None:
    p = get_backend_profile("uqc_mock")
    assert p.uqc_mode == "mock"
