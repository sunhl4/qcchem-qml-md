"""Cross-field validation helpers for :mod:`qchem_stack.config.experiment`."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

from qchem_stack.exceptions import ConfigurationError

from ._constants import MD_ML_MAX_EXTRA_GEOMETRIES
from ._driver_helpers import scf_driver_id
from ._embedding_validation import (
    EmbeddingValidationContext,
    validate_embedding,
    validate_embedding_backend_caps,
)
from ._experiment_validation_pbc import (
    validate_pbc_excludes_casscf_hooks,
    validate_pbc_k_mesh_solver_capability,
)
from ._experiment_validation_precomputed import (
    preprocess_precomputed_bundle_path,
    validate_precomputed_driver_excludes_live_hooks,
)
from ._pre_quantum_path import PreQuantumPath, resolve_pre_quantum_path
from .active_space_helpers import resolve_fermion_qubit_mapping

if TYPE_CHECKING:
    from qchem_stack.chem.solvers.base import SolverCapabilities

    from .experiment import ExperimentConfig

_CLUSTER_SQUARE_FERMION_QUBIT_MAPPINGS = frozenset({"jordan_wigner", "bravyi_kitaev", "jkmn"})
_CLUSTER_ANSATZ_IDS = frozenset({"uccsd", "uccgd", "qcc", "upccgsd", "puccd"})


def _raise_missing_backend_capability(
    *,
    enabled: bool,
    message: str,
) -> None:
    if not enabled:
        raise ConfigurationError(message)


def validate_pre_quantum_contract(
    spec: ExperimentConfig,
    *,
    caps: SolverCapabilities | None = None,
) -> None:
    """Run the pre-quantum subset of cross-section validators.

    Includes precomputed driver guards, embedding contract, PBC/CASSCF exclusion,
    and backend capability gates for the default pre-quantum path.

    Does **not** run the full :data:`EXPERIMENT_CROSS_VALIDATORS` registry (e.g.
    MD/ML geometry shape, UCCSD variational constraints, AVAS ao_labels check,
    or ``validate_pbc_k_mesh_solver_capability``).

    *caps* is optional: when provided, capability-dependent checks run
    immediately. When ``None``, those checks are skipped (the pipeline
    layer is responsible for running them separately with real caps).
    """
    validate_precomputed_driver_excludes_live_hooks(spec)
    validate_embedding_contract(spec)
    validate_pbc_excludes_casscf_hooks(spec)
    if caps is not None:
        validate_backend_capabilities_for_pre_quantum_path(spec, caps=caps)


def validate_embedding_contract(spec: ExperimentConfig) -> None:
    ctx = EmbeddingValidationContext(
        n_atom=len(spec.molecule.symbols),
        scf_method=str(spec.scf.method),
        scf_driver=str(spec.scf.driver),
    )
    validate_embedding(spec.embedding, ctx)


def validate_backend_capabilities_for_pre_quantum_path(
    spec: ExperimentConfig,
    *,
    caps: SolverCapabilities,
) -> None:
    """Reject YAML combos that the selected ``scf.driver`` cannot serve at load time.

    *caps* must be supplied by the caller — config never instantiates a solver.
    """
    driver = scf_driver_id(spec.scf.driver)
    path = resolve_pre_quantum_path(spec)
    if path == PreQuantumPath.PRECOMPUTED_BUNDLE:
        return

    validate_embedding_backend_caps(spec.embedding, caps=caps, scf_driver=driver)

    if spec.embedding.mode == "plugin":
        return

    if driver in ("pyscf", "psi4"):
        _raise_missing_backend_capability(
            enabled=caps.supports_restricted_active_space_qubit_hamiltonian,
            message=(
                "Default pre-quantum path builds a restricted active-space qubit Hamiltonian; "
                f"scf.driver={driver!r} does not advertise "
                "supports_restricted_active_space_qubit_hamiltonian=True."
            ),
        )
        return

    _raise_missing_backend_capability(
        enabled=caps.supports_restricted_active_space_qubit_hamiltonian,
        message=(
            "Default pre-quantum path requires supports_restricted_active_space_qubit_hamiltonian "
            f"or embedding.mode='plugin' (scf.driver={driver!r})."
        ),
    )


def preprocess_top_level_yaml_dict(
    data: Mapping[str, Any],
    *,
    known_fields: set[str],
    strict_unknown_top_level: bool = False,
) -> dict[str, Any]:
    """Filter known top-level fields and merge unknown keys into ``extra``."""
    top_level = {key: value for key, value in data.items() if key in known_fields}
    unknown_top_level = {key: data[key] for key in sorted(set(data) - known_fields)}
    if strict_unknown_top_level and unknown_top_level:
        keys = ", ".join(sorted(str(k) for k in unknown_top_level))
        raise ConfigurationError(
            "Unknown top-level config keys are not allowed in strict mode: "
            f"{keys}. Move extension fields under `extra`."
        )

    explicit_extra = top_level.get("extra")
    if explicit_extra is None:
        merged_extra: dict[str, Any] = {}
    elif isinstance(explicit_extra, Mapping):
        merged_extra = dict(explicit_extra)
    else:
        raise TypeError("ExperimentConfig.extra must be a mapping when provided.")

    merged_extra.update(unknown_top_level)
    if merged_extra or "extra" in top_level:
        top_level["extra"] = merged_extra
    return top_level


def validate_md_ml_extra_coordinates_shape(spec: ExperimentConfig) -> None:
    md_ml_spec = spec.md_ml_export
    n_atom = len(spec.molecule.symbols)
    extras = md_ml_spec.trajectory.extra_coordinates_bohr
    if len(extras) > MD_ML_MAX_EXTRA_GEOMETRIES:
        raise ValueError(
            "md_ml_export.trajectory.extra_coordinates_bohr: at most "
            f"{MD_ML_MAX_EXTRA_GEOMETRIES} geometries "
            f"(got {len(extras)})."
        )
    for geometry_index, coordinates in enumerate(extras):
        validate_md_ml_extra_geometry_shape(
            coordinates, geometry_index=geometry_index, n_atom=n_atom
        )


def validate_md_ml_extra_geometry_shape(
    coords: Sequence[Sequence[Any]],
    *,
    geometry_index: int,
    n_atom: int,
) -> None:
    if len(coords) != n_atom:
        raise ValueError(
            f"md_ml_export.trajectory.extra_coordinates_bohr[{geometry_index}]: expected {n_atom} atoms, "
            f"got {len(coords)}."
        )
    for atom_index, row in enumerate(coords):
        if len(row) != 3:
            raise ValueError(
                "md_ml_export.trajectory.extra_coordinates_bohr"
                f"[{geometry_index}][{atom_index}]: expected 3 Cartesian floats."
            )


def validate_md_ml_pauli_energy_requires_pauli_protocol(spec: ExperimentConfig) -> None:
    if (
        not spec.md_ml_export.attach_single_frame_to_repro
        or spec.md_ml_export.energy_reference != "pauli_protocol"
    ):
        return
    if not spec.quantum.pauli.use_protocol:
        raise ValueError(
            "md_ml_export.energy_reference='pauli_protocol' requires quantum.pauli.use_protocol=true."
        )


def validate_avas_strategy_requires_labels_and_capability(
    spec: ExperimentConfig,
    *,
    caps: SolverCapabilities | None = None,
) -> None:
    if spec.active_space.strategy != "avas":
        return
    if caps is not None and not caps.supports_avas_active_space_projection:
        raise ConfigurationError(
            "active_space.strategy='avas' requires SolverCapabilities."
            "supports_avas_active_space_projection=True on the selected backend "
            f"(scf.driver={spec.scf.driver!r})."
        )
    if not spec.chemistry_extended.avas.ao_labels:
        raise ValueError(
            "active_space.strategy='avas' requires non-empty chemistry_extended.avas.ao_labels "
            "(AVAS orbital projection inputs)."
        )


# Drivers known to not support AVAS at config load time (static preset also rejects).
_DRIVERS_WITHOUT_AVAS = frozenset({"precomputed"})


def validate_scf_driver_registered(spec: ExperimentConfig) -> None:
    """Validate that scf.driver is registered in the solver registry."""
    try:
        from qchem_stack.chem.solvers.registry import registered_solver_ids
    except ImportError:
        # Solver registry not available, skip validation
        return

    driver = str(spec.scf.driver).strip().lower()
    if not driver:
        return

    registered_ids = registered_solver_ids()
    if driver not in registered_ids:
        from pydantic_core import PydanticCustomError

        raise PydanticCustomError(
            "unknown_solver",
            "Unknown scf.driver '{driver}'. Registered drivers: {registered}.",
            {"driver": driver, "registered": sorted(registered_ids)},
        )


def validate_avas_strategy_at_config_load(spec: ExperimentConfig) -> None:
    """Reject AVAS for known-bad drivers and validate ao_labels at config load.

    Capability checks use static built-in presets only; plugin drivers defer to
    :data:`EXPERIMENT_CROSS_VALIDATORS_WITH_CAPS` in the pipeline layer.
    """
    if spec.active_space.strategy != "avas":
        return
    driver = str(spec.scf.driver).strip().lower()

    if driver in _DRIVERS_WITHOUT_AVAS:
        raise ConfigurationError(
            "active_space.strategy='avas' requires supports_avas_active_space_projection=True "
            f"on the selected backend (scf.driver={driver!r}). "
            "Driver 'precomputed' does not support AVAS projection."
        )

    caps: SolverCapabilities | None = None
    try:
        from qchem_stack.chem.solvers.registry import static_solver_capabilities_for_driver

        caps = static_solver_capabilities_for_driver(driver)
    except ImportError:
        pass

    validate_avas_strategy_requires_labels_and_capability(spec, caps=caps)


def validate_uccsd_variational_constraints(spec: ExperimentConfig) -> None:
    quantum_spec = spec.quantum
    ansatz = quantum_spec.variational.ansatz
    if ansatz not in _CLUSTER_ANSATZ_IDS:
        return
    if quantum_spec.algorithm != "vqe" and not quantum_spec.algorithm_factory:
        raise ValueError(
            f"quantum.variational.ansatz={ansatz!r} requires quantum.algorithm='vqe' "
            "or an explicit quantum.algorithm_factory (plug-in must honor cluster semantics)."
        )
    mapping = resolve_fermion_qubit_mapping(spec.active_space)
    if mapping == "hard_core_boson":
        raise ValueError(
            f"quantum.variational.ansatz={ansatz!r} is incompatible with "
            "active_space.mapping.fermion_qubit='hard_core_boson' (use hea or a boson-native ansatz)."
        )
    if mapping not in _CLUSTER_SQUARE_FERMION_QUBIT_MAPPINGS:
        raise ValueError(
            f"quantum.variational.ansatz={ansatz!r} requires a square fermion→qubit encoding "
            f"({sorted(_CLUSTER_SQUARE_FERMION_QUBIT_MAPPINGS)}); got {mapping!r}."
        )
    if ansatz != "uccsd":
        return
    if (
        quantum_spec.pauli.use_protocol
        and spec.mitigation.zne.enabled
        and spec.mitigation.zne.mode == "circuit_scale_fold"
    ):
        raise ValueError(
            "quantum.variational.ansatz='uccsd' with quantum.pauli.use_protocol=True "
            "does not support mitigation.zne.mode='circuit_scale_fold' (HEA depth fold only). "
            "Use zne.mode='scalar_stub' or disable ZNE."
        )


EXPERIMENT_CROSS_VALIDATORS = (
    validate_scf_driver_registered,
    validate_embedding_contract,
    validate_md_ml_extra_coordinates_shape,
    validate_md_ml_pauli_energy_requires_pauli_protocol,
    validate_uccsd_variational_constraints,
    validate_precomputed_driver_excludes_live_hooks,
    validate_pbc_excludes_casscf_hooks,
    validate_avas_strategy_at_config_load,
)


EXPERIMENT_CROSS_VALIDATORS_WITH_CAPS = (
    validate_pbc_k_mesh_solver_capability,
    validate_avas_strategy_requires_labels_and_capability,
    validate_backend_capabilities_for_pre_quantum_path,
)


def validate_experiment_for_run(
    spec: ExperimentConfig,
    *,
    caps: SolverCapabilities,
) -> None:
    """Single full-validation entry point for an actual run (pipeline / API / CLI).

    Runs the config-load registry (:data:`EXPERIMENT_CROSS_VALIDATORS`, idempotent
    pure checks) *and* the capability-dependent registry
    (:data:`EXPERIMENT_CROSS_VALIDATORS_WITH_CAPS`) against live
    :class:`SolverCapabilities`.

    Callers that only ``load_experiment_config`` get the base registry via Pydantic
    ``model_validate`` but **skip** the cap-dependent rules (PBC k-mesh, AVAS
    labels + capability, backend capability). Routing every run through this helper
    ensures those rules are never silently skipped.
    """
    for validator in EXPERIMENT_CROSS_VALIDATORS:
        validator(spec)
    for validator in EXPERIMENT_CROSS_VALIDATORS_WITH_CAPS:
        validator(spec, caps=caps)


__all__ = [
    "EXPERIMENT_CROSS_VALIDATORS",
    "EXPERIMENT_CROSS_VALIDATORS_WITH_CAPS",
    "preprocess_precomputed_bundle_path",
    "preprocess_top_level_yaml_dict",
    "validate_experiment_for_run",
    "validate_pre_quantum_contract",
]
