"""Cross-field validation helpers for :mod:`qchem_stack.config.experiment`."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .experiment import ExperimentConfig


_UCCSD_ALLOWED_FERMION_QUBIT_MAPPINGS = frozenset({"jordan_wigner", "bravyi_kitaev"})


def preprocess_top_level_yaml_dict(
    data: Mapping[str, Any],
    *,
    known_fields: set[str],
) -> dict[str, Any]:
    """Filter known top-level fields and merge unknown keys into ``extra``."""
    top_level = {key: value for key, value in data.items() if key in known_fields}
    unknown_top_level = {key: data[key] for key in sorted(set(data) - known_fields)}

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
