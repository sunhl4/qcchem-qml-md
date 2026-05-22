"""Registry for excited-state sidecar plug-ins (VQD / QSE / SCEOM)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Final

from qchem_stack.config.quantum_helpers import (
    excited_qse_after_variational,
    excited_sceom_after_variational,
    excited_vqd_after_variational,
)
from qchem_stack.contracts.schema_ids import (
    EXCITED_QSE_BUNDLE_V1,
    EXCITED_SCEOM_BUNDLE_V1,
    EXCITED_VQD_BUNDLE_V1,
)
from qchem_stack.exceptions import PipelineError
from qchem_stack.quantum.excited_plugins.builtins import BUILTIN_EXCITED_RUNNERS
from qchem_stack.quantum.excited_plugins.spec import ExcitedRunContext, ExcitedStageOutcome

ExcitedRunner = Callable[[ExcitedRunContext], ExcitedStageOutcome]


@dataclass(frozen=True)
class ExcitedPluginRecord:
    """Metadata + runner for parity export and diagnostics."""

    plugin_id: str
    summary: str
    implementation: str
    runner: ExcitedRunner
    bundle_schema: str
    capabilities: dict[str, bool] = field(default_factory=dict)
    result_schema: str = "excited_stage_outcome_v1"


_BUILTIN_METADATA: Final[dict[str, dict[str, Any]]] = {
    "vqd": {
        "summary": "Deflation VQD sidecar; supports UCCSD prepare_state via variational_branch.",
        "implementation": "qchem_stack.quantum.excited_plugins.builtins.run_vqd_excited",
        "bundle_schema": EXCITED_VQD_BUNDLE_V1,
        "capabilities": {"supports_uccsd_prepare_state": True, "requires_executor": True},
    },
    "qse": {
        "summary": "QSE sidecar (HEA Pauli-X or UCCSD fermionic-singles basis; exact / gaussian_h / pauli_transitions).",
        "implementation": "qchem_stack.quantum.excited_plugins.builtins.run_qse_excited",
        "bundle_schema": EXCITED_QSE_BUNDLE_V1,
        "capabilities": {
            "supports_uccsd_prepare_state": True,
            "hea_pauli_transitions_only": True,
        },
    },
    "sceom": {
        "summary": "Nested-commutator SCEOM sidecar (HEA or UCCSD reference state).",
        "implementation": "qchem_stack.quantum.excited_plugins.builtins.run_sceom_excited",
        "bundle_schema": EXCITED_SCEOM_BUNDLE_V1,
        "capabilities": {"supports_uccsd_prepare_state": True},
    },
}


def _initial_registry() -> dict[str, ExcitedPluginRecord]:
    out: dict[str, ExcitedPluginRecord] = {}
    for pid, runner in BUILTIN_EXCITED_RUNNERS.items():
        meta = _BUILTIN_METADATA[pid]
        out[pid] = ExcitedPluginRecord(
            plugin_id=pid,
            summary=str(meta["summary"]),
            implementation=str(meta["implementation"]),
            runner=runner,  # type: ignore[arg-type]
            bundle_schema=str(meta["bundle_schema"]),
            capabilities=dict(meta.get("capabilities", {})),
        )
    return out


_PLUGIN_REGISTRY: dict[str, ExcitedPluginRecord] = _initial_registry()

BUILTIN_EXCITED_PLUGIN_IDS: Final[frozenset[str]] = frozenset(BUILTIN_EXCITED_RUNNERS.keys())


def list_registered_excited_ids() -> tuple[str, ...]:
    return tuple(sorted(_PLUGIN_REGISTRY.keys()))


def get_excited_plugin_record(plugin_id: str) -> ExcitedPluginRecord | None:
    return _PLUGIN_REGISTRY.get(plugin_id)


def unregister_excited_plugin(plugin_id: str) -> None:
    """Remove a dynamically registered plug-in (built-ins are immutable)."""
    key = plugin_id.strip()
    if key in BUILTIN_EXCITED_PLUGIN_IDS:
        raise ValueError(f"cannot unregister built-in excited plugin {key!r}")
    if key not in _PLUGIN_REGISTRY:
        raise KeyError(key)
    del _PLUGIN_REGISTRY[key]


def register_excited_plugin(
    plugin_id: str,
    *,
    runner: ExcitedRunner,
    summary: str = "Custom excited-state sidecar plugin.",
    implementation: str = "custom",
    bundle_schema: str = "excited_custom_bundle_v1",
    capabilities: dict[str, bool] | None = None,
    result_schema: str = "excited_stage_outcome_v1",
    overwrite: bool = False,
) -> None:
    """Register or replace an excited-state sidecar runner."""
    key = plugin_id.strip()
    if not key:
        raise ValueError("plugin_id must be non-empty")
    if key in BUILTIN_EXCITED_PLUGIN_IDS and not overwrite:
        raise PipelineError(f"cannot overwrite built-in excited plugin {key!r}")
    if key in _PLUGIN_REGISTRY and not overwrite:
        raise PipelineError(f"excited plugin {key!r} already registered (pass overwrite=True)")
    _PLUGIN_REGISTRY[key] = ExcitedPluginRecord(
        plugin_id=key,
        summary=summary,
        implementation=implementation,
        runner=runner,
        bundle_schema=bundle_schema,
        capabilities=dict(capabilities or {}),
        result_schema=result_schema,
    )


def excited_registry_export() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for k, rec in sorted(_PLUGIN_REGISTRY.items()):
        out[k] = {
            "summary": rec.summary,
            "implementation": rec.implementation,
            "capabilities": dict(rec.capabilities),
            "result_schema": rec.result_schema,
            "bundle_schema": rec.bundle_schema,
        }
    return out


def resolve_excited_plugin_ids(cfg: object) -> tuple[str, ...]:
    """Return sidecar plugin ids enabled by ``quantum.excited.*`` flags."""
    from qchem_stack.config import ExperimentConfig

    if not isinstance(cfg, ExperimentConfig):
        raise TypeError("cfg must be ExperimentConfig")
    ids: list[str] = []
    if excited_vqd_after_variational(cfg):
        ids.append("vqd")
    if excited_qse_after_variational(cfg):
        ids.append("qse")
    if excited_sceom_after_variational(cfg):
        ids.append("sceom")
    return tuple(ids)


def run_excited_plugin(plugin_id: str, ctx: ExcitedRunContext) -> ExcitedStageOutcome:
    try:
        record = _PLUGIN_REGISTRY[plugin_id]
    except KeyError as exc:
        raise PipelineError(
            f"Unknown excited plugin id: {plugin_id!r}. Registered: {list_registered_excited_ids()}."
        ) from exc
    return record.runner(ctx)


def run_excited_stages_from_context(
    ctx: ExcitedRunContext,
    out: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run all enabled excited plugins and merge bundles into ``out``."""
    merged = out if out is not None else {}
    for plugin_id in resolve_excited_plugin_ids(ctx.cfg):
        outcome = run_excited_plugin(plugin_id, ctx)
        merged[outcome.bundle_key] = outcome.bundle
    return merged
