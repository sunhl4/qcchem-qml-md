"""Compile scenario-first v3 YAML fragments into v2-compatible dicts."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING, Any

from qchem_stack.config.scenarios import (
    SCENARIOS,
    scenario_base_config_path,
    scenario_config_path,
)

if TYPE_CHECKING:
    from qchem_stack.config.migrations import ConfigMigration


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = deepcopy(value)
    return out


def _parse_dotted_set(spec: str) -> tuple[list[str], str]:
    if "=" not in spec:
        raise ValueError(f"--set expects key=value, got {spec!r}")
    key_part, raw_val = spec.split("=", 1)
    keys = [p for p in key_part.strip().split(".") if p]
    if not keys:
        raise ValueError(f"empty key in --set {spec!r}")
    return keys, raw_val


def _coerce_scalar(raw: str) -> object:
    lowered = raw.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    try:
        if "." in raw:
            return float(raw)
        return int(raw)
    except ValueError:
        return raw


def apply_dotted_set(cfg: dict[str, Any], spec: str) -> dict[str, Any]:
    keys, raw_val = _parse_dotted_set(spec)
    val = _coerce_scalar(raw_val)
    out = deepcopy(cfg)
    node: dict[str, Any] = out
    for key in keys[:-1]:
        child = node.get(key)
        if not isinstance(child, dict):
            child = {}
            node[key] = child
        node = child
    node[keys[-1]] = val
    return out


def _load_yaml_mapping(path: Path, *, label: str) -> dict[str, Any]:
    import yaml

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{label} root must be mapping: {path}")
    return raw


def _is_thin_v3_stub(raw: dict[str, Any], scenario_id: str) -> bool:
    return str(raw.get("schema_version", "")) == "3" and raw.get("scenario") == scenario_id


def compile_scenario_v3(
    *,
    scenario_id: str,
    overrides: dict[str, Any] | None = None,
    dotted_sets: list[str] | None = None,
    configs_dir: Path | None = None,
) -> dict[str, Any]:
    """Build a YAML-ready dict from scenario id + overrides."""
    if scenario_id not in SCENARIOS:
        known = ", ".join(sorted(SCENARIOS))
        raise ValueError(f"unknown scenario {scenario_id!r}; choose from: {known}")

    path = scenario_config_path(scenario_id, configs_dir=configs_dir)
    raw = _load_yaml_mapping(path, label="scenario YAML")
    file_overrides: dict[str, Any] | None = None
    if _is_thin_v3_stub(raw, scenario_id):
        base_path = scenario_base_config_path(scenario_id, configs_dir=configs_dir)
        cfg = _load_yaml_mapping(base_path, label="scenario base YAML")
        stub_overrides = raw.get("overrides")
        if stub_overrides is not None:
            if not isinstance(stub_overrides, dict):
                raise ValueError("'overrides' must be a mapping when present")
            file_overrides = deepcopy(stub_overrides)
    else:
        cfg = deepcopy(raw)
    cfg["schema_version"] = "3"
    cfg["scenario"] = scenario_id
    merged_overrides = deepcopy(file_overrides) if file_overrides else {}
    if overrides:
        merged_overrides = _deep_merge(merged_overrides, overrides)
    if merged_overrides:
        cfg["overrides"] = merged_overrides
        cfg = _deep_merge(cfg, merged_overrides)
    for spec in dotted_sets or []:
        cfg = apply_dotted_set(cfg, spec)
    return cfg


def migrate_v3_payload_to_v2(raw: dict[str, Any]) -> dict[str, Any]:
    """If ``schema_version`` is 3 with ``scenario``, expand to v2-compatible dict."""
    if str(raw.get("schema_version", "2")) != "3":
        return raw
    scenario = raw.get("scenario")
    if not isinstance(scenario, str) or not scenario.strip():
        raise ValueError("schema_version 3 requires non-empty 'scenario'")
    stub_keys = {"schema_version", "scenario", "overrides"}
    if set(raw.keys()) - stub_keys:
        out = deepcopy(raw)
        out["schema_version"] = "2"
        out.pop("scenario", None)
        out.pop("overrides", None)
        return out
    overrides = raw.get("overrides")
    if overrides is not None and not isinstance(overrides, dict):
        raise ValueError("'overrides' must be a mapping when present")
    compiled = compile_scenario_v3(
        scenario_id=scenario.strip(),
        overrides=overrides,
    )
    compiled["schema_version"] = "2"
    compiled.pop("scenario", None)
    compiled.pop("overrides", None)
    return compiled


# Backward-compatible alias used during migration wiring.
migrate_v2_to_v3 = migrate_v3_payload_to_v2


def _migration_v3_to_v2_class() -> type[ConfigMigration]:
    from qchem_stack.config.migrations import ConfigMigration

    class MigrationV3ToV2(ConfigMigration):
        from_version = "3"
        to_version = "2"
        description = "Expand scenario-first v3 YAML into v2-compatible mapping"

        def migrate(self, config: dict[str, Any]) -> dict[str, Any]:
            return migrate_v3_payload_to_v2(config)

    return MigrationV3ToV2


MigrationV3ToV2 = _migration_v3_to_v2_class()


__all__ = [
    "MigrationV3ToV2",
    "apply_dotted_set",
    "compile_scenario_v3",
    "migrate_v2_to_v3",
    "migrate_v3_payload_to_v2",
]
