"""Tests for config schema migrations (v1 flat → v2 nested)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.config.migrations import (
    SCHEMA_VERSION_CURRENT,
    MigrationError,
    MigrationV1ToV2,
    get_schema_version,
    migrate_config,
)

ROOT = Path(__file__).resolve().parents[2]
V1_FIXTURE = ROOT / "tests/fixtures/config_v1_flat_minimal.yaml"
H2_V2 = ROOT / "configs/example_h2.yaml"


@pytest.mark.parametrize(
    ("flat_key", "nested_path"),
    [
        ("quantum_algorithm", ("quantum", "algorithm")),
        ("scf_driver", ("scf", "driver")),
        ("backend_provider", ("backend", "provider")),
        ("active_space_n_orbitals", ("active_space", "manual", "n_orbitals")),
    ],
)
def test_v1_to_v2_key_mapping_samples(flat_key: str, nested_path: tuple[str, ...]) -> None:
    migration = MigrationV1ToV2()
    assert migration.KEY_MAPPINGS[flat_key] == nested_path


def test_migrate_v1_fixture_to_v2() -> None:
    raw = yaml.safe_load(V1_FIXTURE.read_text(encoding="utf-8"))
    assert get_schema_version(raw) in ("0", "1")
    migrated = migrate_config(raw)
    assert migrated["schema_version"] == "2"
    assert migrated["quantum"]["algorithm"] == "vqe"
    assert migrated["scf"]["driver"] == "pyscf"
    assert migrated["backend"]["provider"] == "statevector"
    cfg = ExperimentConfig.from_yaml_dict(migrated)
    assert cfg.experiment_id == "v1_flat_minimal"


def test_load_experiment_config_auto_migrates_v1_fixture() -> None:
    cfg = load_experiment_config(V1_FIXTURE)
    assert cfg.schema_version == "2"
    assert cfg.quantum.algorithm == "vqe"


def test_load_experiment_config_v2_unchanged() -> None:
    cfg_before = load_experiment_config(H2_V2)
    raw_v2 = yaml.safe_load(H2_V2.read_text(encoding="utf-8"))
    assert raw_v2.get("schema_version") == "2"
    cfg_after = load_experiment_config(H2_V2)
    assert cfg_after.experiment_id == cfg_before.experiment_id
    assert cfg_after.quantum.algorithm == cfg_before.quantum.algorithm


def test_migrate_config_idempotent_at_v2() -> None:
    raw = yaml.safe_load(H2_V2.read_text(encoding="utf-8"))
    once = migrate_config(raw)
    twice = migrate_config(once)
    assert twice["schema_version"] == SCHEMA_VERSION_CURRENT


def test_migrate_config_unreachable_version_raises() -> None:
    with pytest.raises(MigrationError, match="No migration path"):
        migrate_config({"schema_version": "99"})


def test_v1_to_v2_rollback_roundtrip_preserves_mapped_keys() -> None:
    migration = MigrationV1ToV2()
    raw = yaml.safe_load(V1_FIXTURE.read_text(encoding="utf-8"))
    migrated = migration.migrate(raw)
    rolled = migration.rollback(migrated)
    assert rolled.get("quantum_algorithm") == "vqe"
    assert rolled.get("scf_driver") == "pyscf"
    assert "schema_version" not in rolled or rolled.get("schema_version") is None
