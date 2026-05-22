"""Registry for excited-state sidecar plug-ins (VQD / QSE / SCEOM)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Final

from qchem_stack.config.quantum_helpers import (
    excited_qse_after_variational,
    excited_sceom_after_variational,
    excited_vqd_after_variational,
)
from qchem_stack.quantum.excited_plugins.builtins import BUILTIN_EXCITED_RUNNERS
from qchem_stack.quantum.excited_plugins.spec import ExcitedRunContext, ExcitedStageOutcome

ExcitedRunner = Callable[[ExcitedRunContext], ExcitedStageOutcome]

BUILTIN_EXCITED_PLUGIN_IDS: Final[frozenset[str]] = frozenset(BUILTIN_EXCITED_RUNNERS.keys())

_PLUGIN_REGISTRY: dict[str, ExcitedRunner] = dict(BUILTIN_EXCITED_RUNNERS)  # type: ignore[arg-type]


def list_registered_excited_ids() -> tuple[str, ...]:
    return tuple(sorted(_PLUGIN_REGISTRY.keys()))


def register_excited_plugin(
    plugin_id: str,
    *,
    runner: ExcitedRunner,
    overwrite: bool = False,
) -> None:
    """Register or replace an excited-state sidecar runner."""
    key = plugin_id.strip()
    if not key:
        raise ValueError("plugin_id must be non-empty")
    if key in BUILTIN_EXCITED_PLUGIN_IDS and not overwrite:
        raise ValueError(f"cannot overwrite built-in excited plugin {key!r}")
    if key in _PLUGIN_REGISTRY and not overwrite:
        raise ValueError(f"excited plugin {key!r} already registered (pass overwrite=True)")
    _PLUGIN_REGISTRY[key] = runner


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
        runner = _PLUGIN_REGISTRY[plugin_id]
    except KeyError as exc:
        raise ValueError(f"Unknown excited plugin id: {plugin_id!r}") from exc
    return runner(ctx)


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
