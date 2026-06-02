"""Registry for plug-in variational algorithms (engineering entry point).

Add third-party identifiers at runtime with :func:`register_variational_plugin`.

YAML:

* ``quantum.algorithm``: built-in key (see :func:`list_registered_variational_ids`) **or**
  any string when ``quantum.algorithm_factory`` is set (reporting / reproducibility label).
* ``quantum.algorithm_factory``: optional ``module.submod:callable`` (see :mod:`~qchem_stack.quantum.variational_plugins.loader`).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Final

from qchem_stack.config.quantum_helpers import (
    resolve_quantum_algorithm_factory,
    resolve_variational_algorithm,
)
from qchem_stack.exceptions import PipelineError
from qchem_stack.quantum.variational_plugins.builtins import BUILTIN_RUNNERS
from qchem_stack.quantum.variational_plugins.loader import load_variational_runner_from_factory
from qchem_stack.quantum.variational_plugins.spec import (
    VariationalRunContext,
    VariationalStageOutcome,
)

VariationalRunner = Callable[[VariationalRunContext], VariationalStageOutcome]


@dataclass(frozen=True)
class VariationalPluginRecord:
    """Metadata + runner for parity export and diagnostics."""

    plugin_id: str
    summary: str
    implementation: str
    """Where the pipeline runner lives (often a ``builtins`` function)."""
    runner: VariationalRunner
    capabilities: dict[str, bool] = field(default_factory=dict)
    result_schema: str = "variational_stage_outcome_v1"
    optional_model_factory: Callable[..., Any] | None = None
    """If set, :func:`~qchem_stack.quantum.algorithm_registry.build_registered_algorithm` may materialize legacy objects."""
    materialization_implementation: str | None = None
    """Public class path surfaced in Methods / ``ALGORITHM_REGISTRY`` (defaults to algorithm class, not runner)."""
    materialization_result_schema: str = "algorithm_report_v1"
    """Export schema id for :class:`~qchem_stack.quantum.algorithm_registry.AlgorithmRegistryEntry`."""


_BUILTIN_METADATA: Final[dict[str, dict[str, Any]]] = {
    "vqe": {
        "summary": "Standard HEA / UCC-style VQE loop (see ``quantum.vqe.depth`` / ``quantum.vqe.maxiter``).",
        "implementation": "qchem_stack.quantum.variational_plugins.builtins.run_vqe_branch",
        "materialization_implementation": "qchem_stack.quantum.algorithms.vqe.VQE",
        "materialization_result_schema": "algorithm_vqe_report_v1",
        "capabilities": {
            "supports_auxiliary_expression": True,
            "supports_gradient_expression": True,
            "supports_uccsd_pauli_protocol": True,
        },
    },
    "adapt": {
        "summary": "Fermionic-pool ADAPT-VQE (commutator-gradient selection).",
        "implementation": "qchem_stack.quantum.variational_plugins.builtins.run_adapt_family",
        "materialization_implementation": "qchem_stack.quantum.algorithms.adapt.FermionicAdaptVQE",
        "materialization_result_schema": "algorithm_report_v1",
        "capabilities": {
            "supports_operator_pool": True,
            "supports_commutator_gradient": True,
        },
    },
    "tetris_adapt": {
        "summary": "TETRIS-style multi-operator rounds on disjoint qubit sets.",
        "implementation": "qchem_stack.quantum.variational_plugins.builtins.run_adapt_family",
        "materialization_implementation": "qchem_stack.quantum.algorithms.adapt.FermionicAdaptVQE",
        "materialization_result_schema": "algorithm_report_v1",
        "capabilities": {
            "supports_operator_pool": True,
            "supports_commutator_gradient": True,
            "supports_tetris_round": True,
        },
    },
    "iqeb": {
        "summary": "IQEB outer Pauli-selection loop with inner VQE.",
        "implementation": "qchem_stack.quantum.variational_plugins.builtins.run_iqeb",
        "materialization_implementation": "qchem_stack.quantum.algorithms.iqeb.IQEBVQE",
        "materialization_result_schema": "algorithm_report_v1",
        "capabilities": {"supports_operator_pool": True, "supports_outer_rounds": True},
    },
    "sa_vqe": {
        "summary": "Minimal state-averaged VQE with overlap penalty (SA-VQE).",
        "implementation": "qchem_stack.quantum.variational_plugins.builtins.run_sa_vqe_branch",
        "materialization_implementation": "qchem_stack.quantum.algorithms.sa_vqe.SAVQE",
        "materialization_result_schema": "algorithm_sa_vqe_report_v1",
        "capabilities": {"supports_state_averaging_penalty": True},
    },
    "qpe_kitaev": {
        "summary": "Kitaev-style dense-spectrum QPE on the active-space Hamiltonian (main config tree).",
        "implementation": "qchem_stack.quantum.variational_plugins.builtins.run_qpe_kitaev",
        "materialization_implementation": "qchem_stack.quantum.algorithms.qpe.AlgorithmKitaevQPE",
        "materialization_result_schema": "algorithm_kitaev_qpe_report_v1",
        "capabilities": {"supports_phase_estimation": True},
    },
    "qpe_deterministic": {
        "summary": "Deterministic dense-spectrum QPE estimator (main config tree).",
        "implementation": "qchem_stack.quantum.variational_plugins.builtins.run_qpe_deterministic",
        "materialization_implementation": "qchem_stack.quantum.algorithms.qpe.AlgorithmDeterministicQPE",
        "materialization_result_schema": "algorithm_deterministic_qpe_report_v1",
        "capabilities": {"supports_phase_estimation": True},
    },
    "qpe_info_theory": {
        "summary": "Information-theory QPE wrapper with Gaussian posterior summary (main config tree).",
        "implementation": "qchem_stack.quantum.variational_plugins.builtins.run_qpe_info_theory",
        "materialization_implementation": "qchem_stack.quantum.algorithms.qpe.AlgorithmInfoTheoryQPE",
        "materialization_result_schema": "algorithm_info_theory_qpe_report_v1",
        "capabilities": {"supports_phase_estimation": True},
    },
}


_MODEL_FACTORY_MAP: Final[dict[str, tuple[str, str, dict[str, Any]]]] = {
    "vqe": ("qchem_stack.quantum.algorithms.vqe", "VQE", {}),
    "adapt": ("qchem_stack.quantum.algorithms.adapt", "FermionicAdaptVQE", {}),
    "tetris_adapt": (
        "qchem_stack.quantum.algorithms.adapt",
        "FermionicAdaptVQE",
        {"tetris_style": True},
    ),
    "iqeb": ("qchem_stack.quantum.algorithms.iqeb", "IQEBVQE", {}),
    "sa_vqe": ("qchem_stack.quantum.algorithms.sa_vqe", "SAVQE", {}),
    "qpe_kitaev": ("qchem_stack.quantum.algorithms.qpe", "AlgorithmKitaevQPE", {}),
    "qpe_deterministic": ("qchem_stack.quantum.algorithms.qpe", "AlgorithmDeterministicQPE", {}),
    "qpe_info_theory": ("qchem_stack.quantum.algorithms.qpe", "AlgorithmInfoTheoryQPE", {}),
}


def _model_factory_from_plugin_id(pid: str) -> Callable[..., Any] | None:
    """Get a model factory callable for a given plugin ID.

    Returns a callable that instantiates the algorithm class, or None if the plugin ID
    is not recognized. Uses lazy imports to avoid circular dependencies.
    """
    if pid not in _MODEL_FACTORY_MAP:
        return None

    module_name, class_name, default_kwargs = _MODEL_FACTORY_MAP[pid]

    def factory(hamiltonian: Any, **kwargs: Any) -> Any:
        import importlib

        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        merged_kwargs = {**default_kwargs, **kwargs}
        return cls(hamiltonian, **merged_kwargs)

    return factory


def _initial_registry() -> dict[str, VariationalPluginRecord]:
    out: dict[str, VariationalPluginRecord] = {}
    for pid, runner in BUILTIN_RUNNERS.items():
        meta = _BUILTIN_METADATA[pid]
        mat_impl = meta.get("materialization_implementation")
        mat_rs = str(meta.get("materialization_result_schema", "algorithm_report_v1"))
        out[pid] = VariationalPluginRecord(
            plugin_id=pid,
            summary=str(meta["summary"]),
            implementation=str(meta["implementation"]),
            runner=runner,  # type: ignore[arg-type]
            capabilities=dict(meta.get("capabilities", {})),
            optional_model_factory=_model_factory_from_plugin_id(pid),
            materialization_implementation=str(mat_impl) if mat_impl else None,
            materialization_result_schema=mat_rs,
        )
    return out


_PLUGIN_REGISTRY: dict[str, VariationalPluginRecord] = _initial_registry()

BUILTIN_VARIATIONAL_PLUGIN_IDS: frozenset[str] = frozenset(BUILTIN_RUNNERS.keys())


def list_registered_variational_ids() -> tuple[str, ...]:
    return tuple(sorted(_PLUGIN_REGISTRY.keys()))


def get_variational_plugin_record(plugin_id: str) -> VariationalPluginRecord | None:
    return _PLUGIN_REGISTRY.get(plugin_id)


def is_registered_variational_id(plugin_id: str) -> bool:
    return plugin_id in _PLUGIN_REGISTRY


def unregister_variational_plugin(plugin_id: str) -> None:
    """Remove a dynamically registered plug-in (built-ins are immutable)."""

    key = plugin_id.strip()
    if key in BUILTIN_VARIATIONAL_PLUGIN_IDS:
        raise ValueError(f"cannot unregister built-in variational plugin {key!r}")
    if key not in _PLUGIN_REGISTRY:
        raise KeyError(key)
    del _PLUGIN_REGISTRY[key]
    from qchem_stack.quantum.algorithm_registry import sync_algorithm_registry_from_variational

    sync_algorithm_registry_from_variational()


def register_variational_plugin(
    plugin_id: str,
    *,
    runner: VariationalRunner,
    summary: str,
    implementation: str,
    capabilities: dict[str, bool] | None = None,
    result_schema: str = "variational_stage_outcome_v1",
    optional_model_factory: Callable[..., Any] | None = None,
    materialization_implementation: str | None = None,
    materialization_result_schema: str = "algorithm_report_v1",
    overwrite: bool = False,
) -> None:
    """Register or replace a variational plug-in (thread-safe enough for startup wiring)."""

    if not plugin_id or not plugin_id.strip():
        raise ValueError("plugin_id must be non-empty")
    key = plugin_id.strip()
    if key in _PLUGIN_REGISTRY and not overwrite:
        raise ValueError(f"variational plugin {key!r} already registered (pass overwrite=True)")
    _PLUGIN_REGISTRY[key] = VariationalPluginRecord(
        plugin_id=key,
        summary=summary,
        implementation=implementation,
        runner=runner,
        capabilities=dict(capabilities or {}),
        result_schema=result_schema,
        optional_model_factory=optional_model_factory,
        materialization_implementation=materialization_implementation,
        materialization_result_schema=materialization_result_schema,
    )
    from qchem_stack.quantum.algorithm_registry import sync_algorithm_registry_from_variational

    sync_algorithm_registry_from_variational()


def variational_registry_export() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for k, rec in sorted(_PLUGIN_REGISTRY.items()):
        out[k] = {
            "summary": rec.summary,
            "implementation": rec.implementation,
            "capabilities": dict(rec.capabilities),
            "result_schema": rec.result_schema,
            "has_materialization": rec.optional_model_factory is not None,
            "materialization_implementation": rec.materialization_implementation,
            "materialization_result_schema": rec.materialization_result_schema,
        }
    return out


def resolve_variational_runner(
    *, algorithm: str, algorithm_factory: str | None
) -> VariationalRunner:
    if algorithm_factory:
        return load_variational_runner_from_factory(algorithm_factory)
    try:
        return _PLUGIN_REGISTRY[algorithm].runner
    except KeyError as exc:
        raise PipelineError(
            f"Unknown quantum.algorithm={algorithm!r}. Registered: {list_registered_variational_ids()}. "
            "Use quantum.algorithm_factory to load external plugins."
        ) from exc


def run_variational_stage(ctx: VariationalRunContext) -> VariationalStageOutcome:
    runner = resolve_variational_runner(
        algorithm=resolve_variational_algorithm(ctx.cfg),
        algorithm_factory=resolve_quantum_algorithm_factory(ctx.cfg),
    )
    return runner(ctx)
