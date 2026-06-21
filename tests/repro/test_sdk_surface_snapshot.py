"""SDK ``__all__`` must match the stable surface documented in api_stability_policy."""

from __future__ import annotations

import qchem_stack.sdk as sdk

# Canonical stable SDK exports (docs/engineering/api_stability_policy.md).
_STABLE_SDK_SYMBOLS = frozenset(
    {
        "ExperimentConfig",
        "SCENARIOS",
        "export_parity_table",
        "list_scenarios_text",
        "load_experiment_config",
        "repro_dict_for_strict_json",
        "repro_json_dumps",
        "run_pipeline_from_config",
        "run_pipeline_sync",
        "workflow_preview_payload",
    }
)


def test_sdk_all_matches_stable_policy() -> None:
    assert frozenset(sdk.__all__) == _STABLE_SDK_SYMBOLS


def test_sdk_exports_are_importable() -> None:
    for name in sdk.__all__:
        assert hasattr(sdk, name), name
