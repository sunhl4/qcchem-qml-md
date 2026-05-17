"""Cross-field validation helpers for :mod:`qchem_stack.config.experiment`."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from qchem_stack.exceptions import ConfigurationError

if TYPE_CHECKING:
    from .experiment import ExperimentConfig


_UCCSD_ALLOWED_FERMION_QUBIT_MAPPINGS = frozenset({"jordan_wigner", "bravyi_kitaev"})

SCHMIDT_DMET_MAX_CYCLES_LIMIT = 50


def _driver_id(spec: ExperimentConfig) -> str:
    return str(spec.scf.driver).strip().lower()


def _raise_missing_backend_capability(
    *,
    enabled: bool,
    message: str,
) -> None:
    if not enabled:
        raise ConfigurationError(message)


def validate_pre_quantum_contract(spec: ExperimentConfig) -> None:
    """Run all pre-quantum YAML validators (same gates as :class:`ExperimentConfig` load)."""
    validate_precomputed_driver_excludes_live_hooks(spec)
    validate_schmidt_requires_rhf(spec)
    validate_schmidt_cycle_bounds(spec)
    validate_pbc_excludes_casscf_hooks(spec)
    validate_backend_capabilities_for_pre_quantum_path(spec)


def validate_precomputed_driver_excludes_live_hooks(spec: ExperimentConfig) -> None:
    if _driver_id(spec) != "precomputed":
        return
    if spec.chemistry_extended.classical_benchmark_enabled:
        raise ConfigurationError(
            "chemistry_extended.classical_benchmark_enabled is unsupported with "
            "scf.driver='precomputed' (no live post-HF backend)."
        )
    if str(spec.chemistry_extended.rdm_correction_method).strip().lower() != "none":
        raise ConfigurationError(
            "chemistry_extended.rdm_correction_method requires live backend hooks and is "
            "unsupported with scf.driver='precomputed'."
        )


def validate_schmidt_requires_rhf(spec: ExperimentConfig) -> None:
    emb = spec.embedding
    if emb.dmet_hamiltonian_source != "schmidt_atomic_production":
        return
    if str(spec.scf.method).strip().upper() != "RHF":
        raise ConfigurationError(
            "embedding.dmet_hamiltonian_source='schmidt_atomic_production' requires "
            "scf.method='RHF' (closed-shell single density matrix)."
        )


def validate_schmidt_cycle_bounds(spec: ExperimentConfig) -> None:
    emb = spec.embedding
    if emb.dmet_hamiltonian_source != "schmidt_atomic_production":
        return
    cycles = int(emb.schmidt_dmet_max_cycles)
    if cycles < 1:
        raise ConfigurationError("embedding.schmidt_dmet_max_cycles must be at least 1.")
    if cycles > SCHMIDT_DMET_MAX_CYCLES_LIMIT:
        raise ConfigurationError(
            "embedding.schmidt_dmet_max_cycles exceeds limit "
            f"{SCHMIDT_DMET_MAX_CYCLES_LIMIT} (got {cycles})."
        )


def validate_pbc_excludes_casscf_hooks(spec: ExperimentConfig) -> None:
    ce = spec.chemistry_extended
    mesh = list(ce.pbc_kpoint_mesh or [1, 1, 1])
    pbc_on = bool(ce.pbc_cell_vectors_bohr) or mesh != [1, 1, 1]
    if not pbc_on:
        return
    if spec.active_space.strategy == "avas":
        raise ConfigurationError(
            "active_space.strategy='avas' is unsupported with periodic boundary conditions."
        )
    if ce.casscf_orbital_optimization_audit:
        raise ConfigurationError(
            "chemistry_extended.casscf_orbital_optimization_audit is unsupported with PBC in this milestone."
        )
    if ce.casscf_orbital_optimization_for_integrals:
        raise ConfigurationError(
            "chemistry_extended.casscf_orbital_optimization_for_integrals is unsupported with PBC "
            "in this milestone."
        )


def validate_backend_capabilities_for_pre_quantum_path(spec: ExperimentConfig) -> None:
    """Reject YAML combos that the selected ``scf.driver`` cannot serve at load time."""
    from qchem_stack.chem.pre_quantum_path import PreQuantumPath, resolve_pre_quantum_path
    from qchem_stack.chem.solvers.registry import create_solver

    driver = _driver_id(spec)
    path = resolve_pre_quantum_path(spec)
    if path == PreQuantumPath.PRECOMPUTED_BUNDLE:
        return
    caps = create_solver(spec).capabilities

    if path == PreQuantumPath.SCHMIDT_ATOMIC_PRODUCTION:
        _raise_missing_backend_capability(
            enabled=caps.supports_schmidt_atomic_hamiltonian,
            message=(
                "embedding.dmet_hamiltonian_source='schmidt_atomic_production' requires "
                f"backend Schmidt support (scf.driver={driver!r})."
            ),
        )
    elif path == PreQuantumPath.PROJECTION_FRAGMENT_MULLIKEN_MO:
        _raise_missing_backend_capability(
            enabled=caps.supports_projection_fragment_mulliken_hamiltonian,
            message=(
                "embedding.projection_quantum_hamiltonian='fragment_mulliken_mo' requires "
                f"backend projection support (scf.driver={driver!r})."
            ),
        )

    if spec.active_space.strategy == "avas":
        _raise_missing_backend_capability(
            enabled=caps.supports_avas_active_space_projection,
            message=(
                "active_space.strategy='avas' requires backend AVAS support "
                f"(scf.driver={driver!r})."
            ),
        )
    if path == PreQuantumPath.EMBEDDING_PLUGIN:
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


def preprocess_precomputed_bundle_path(
    data: dict[str, Any],
    *,
    base_dir: Path,
) -> None:
    """Resolve ``scf.precomputed_bundle_path`` relative to YAML location when present."""
    scf = data.get("scf")
    if not isinstance(scf, dict):
        return
    if str(scf.get("driver", "")).strip().lower() != "precomputed":
        return
    raw = scf.get("precomputed_bundle_path")
    if raw is None:
        return
    if not isinstance(raw, str) or not raw.strip():
        raise ConfigurationError(
            "scf.precomputed_bundle_path must be a non-empty string when scf.driver='precomputed'."
        )
    p = Path(raw.strip())
    resolved = p if p.is_absolute() else (base_dir / p).resolve()
    scf["precomputed_bundle_path"] = str(resolved)


def validate_embedding_atom_indices_within_molecule(spec: ExperimentConfig) -> None:
    n_atom = len(spec.molecule.symbols)
    for atom_index in spec.embedding.projection_fragment_atom_indices:
        if atom_index < 0 or atom_index >= n_atom:
            raise ValueError(
                "embedding.projection_fragment_atom_indices: atom index "
                f"{atom_index} out of range (n_atom={n_atom})."
            )


def validate_md_ml_extra_coordinates_shape(spec: ExperimentConfig) -> None:
    from qchem_stack.md_bridge.from_pipeline import MD_ML_MAX_EXTRA_GEOMETRIES

    md_ml_spec = spec.md_ml_export
    n_atom = len(spec.molecule.symbols)
    if len(md_ml_spec.extra_coordinates_bohr) > MD_ML_MAX_EXTRA_GEOMETRIES:
        raise ValueError(
            "md_ml_export.extra_coordinates_bohr: at most "
            f"{MD_ML_MAX_EXTRA_GEOMETRIES} geometries "
            f"(got {len(md_ml_spec.extra_coordinates_bohr)})."
        )
    for geometry_index, coordinates in enumerate(md_ml_spec.extra_coordinates_bohr):
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
            f"md_ml_export.extra_coordinates_bohr[{geometry_index}]: expected {n_atom} atoms, "
            f"got {len(coords)}."
        )
    for atom_index, row in enumerate(coords):
        if len(row) != 3:
            raise ValueError(
                "md_ml_export.extra_coordinates_bohr"
                f"[{geometry_index}][{atom_index}]: expected 3 Cartesian floats."
            )


def validate_md_ml_pauli_energy_requires_pauli_protocol(spec: ExperimentConfig) -> None:
    if (
        not spec.md_ml_export.attach_single_frame_to_repro
        or spec.md_ml_export.energy_reference != "pauli_protocol"
    ):
        return
    if not spec.quantum.use_pauli_protocol:
        raise ValueError(
            "md_ml_export.energy_reference='pauli_protocol' requires quantum.use_pauli_protocol=true."
        )


def validate_avas_strategy_requires_pyscf_labels(spec: ExperimentConfig) -> None:
    if spec.active_space.strategy != "avas":
        return
    if str(spec.scf.driver).strip().lower() != "pyscf":
        raise ValueError(
            "active_space.strategy='avas' requires a backend that implements PySCF-style AVAS "
            "in this milestone: set scf.driver='pyscf' (or register another adapter whose "
            "SolverCapabilities.supports_avas_active_space_projection is True and wires the same hook). "
            f"Got scf.driver={spec.scf.driver!r}."
        )
    if not spec.chemistry_extended.avas_ao_labels:
        raise ValueError(
            "active_space.strategy='avas' requires non-empty chemistry_extended.avas_ao_labels "
            "(PySCF AVAS orbital projection inputs)."
        )


def validate_uccsd_variational_constraints(spec: ExperimentConfig) -> None:
    quantum_spec = spec.quantum
    if quantum_spec.variational_ansatz != "uccsd":
        return
    if quantum_spec.algorithm != "vqe" and not quantum_spec.algorithm_factory:
        raise ValueError(
            "quantum.variational_ansatz='uccsd' requires quantum.algorithm='vqe' "
            "or an explicit quantum.algorithm_factory (plug-in must honor UCCSD semantics)."
        )
    if spec.active_space.fermion_qubit_mapping not in _UCCSD_ALLOWED_FERMION_QUBIT_MAPPINGS:
        raise ValueError(
            "quantum.variational_ansatz='uccsd' requires active_space.fermion_qubit_mapping in "
            "{'jordan_wigner', 'bravyi_kitaev'} (square encodings; symmetry_conserving_bravyi_kitaev is unsupported)."
        )
    if quantum_spec.use_pauli_protocol:
        raise ValueError(
            "quantum.variational_ansatz='uccsd' is incompatible with use_pauli_protocol=True "
            "(Pauli measurement circuits use HEA). Set use_pauli_protocol: false."
        )
    if quantum_spec.qse_after_variational or quantum_spec.sceom_after_variational:
        raise ValueError(
            "quantum.variational_ansatz='uccsd' cannot combine with QSE/SCEOM "
            "(those stages expect HEA angle packing)."
        )
