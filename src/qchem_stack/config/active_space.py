"""Active-space sizing and fermion-to-qubit mapping configuration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from ._active_space_validation import (
    normalize_active_space_entry,
    validate_frozen_orbitals,
    validate_jw_optimizer_flags,
)


class ActiveSpaceSpec(BaseModel):
    """Active-space sizing, strategy, and fermion-to-qubit mapping.

    **strategy** selects how active orbitals and electrons are specified:

    - ``cas``: canonical CAS notation via ``ncas``/``nelecas`` (or legacy ``n_active_*`` aliases).
    - ``manual``: explicit active-space sizes plus optional ``frozen_orbitals`` bookkeeping.
    - ``avas_stub``: **hook-only** — same **CAS** sizing as ``cas`` (``ncas`` / ``nelecas``); no AO
      threshold projection. Honesty metadata is written by
      :func:`~qchem_stack.chem.active_space.mean_field_meta.apply_active_space_strategy_to_mean_field_meta`
      (e.g. ``avas_partial_stub``, ``avas_atomic_projection_executed``, ``avas_stub_semantics``).
      Does **not** build vendor/PySCF-style ``frozen=avas.frozenf`` from atomic valence weights.
    - ``avas``: **PySCF path** — run :class:`pyscf.mcscf.avas.AVAS` threshold projection using
      ``chemistry_extended.avas_ao_labels`` and related AVAS knobs, rotate ``mf.mo_coeff``, then
      patch YAML-sized ``ncas`` / ``nelecas`` via ``driver_meta.qchem_active_space_resolution_v1``
      inside the pipeline (repro parity with AVAS-derived active dimensions).
    """

    strategy: Literal["manual", "cas", "avas_stub", "avas"] = "cas"
    n_active_orbitals: int | None = None
    n_active_electrons: int | None = None
    ncas: int | None = None
    nelecas: int | None = None
    frozen_orbitals: list[int] = Field(default_factory=list)
    fermion_qubit_mapping: Literal[
        "jordan_wigner",
        "bravyi_kitaev",
        "symmetry_conserving_bravyi_kitaev",
    ] = Field(
        default="jordan_wigner",
        description=(
            "OpenFermion transform from :class:`openfermion.InteractionOperator` "
            "to :class:`openfermion.QubitOperator`."
        ),
    )
    prefer_restricted_spatial_fermion_for_jordan_wigner: bool = Field(
        default=False,
        description=(
            "Jordan–Wigner only: build :class:`openfermion.FermionOperator` from spatial MO integrals then JW, "
            "avoiding a dense (2×ncas)⁴ spin ERI tensor for that mapping step (see "
            ":func:`~qchem_stack.chem.hamiltonian.molecular_hamiltonian_from_classical_reference`)."
        ),
    )
    jordan_wigner_coeff_atol: float | None = Field(
        default=None,
        description=(
            "Optional positive cutoff on the InteractionOperator JW path (skip negligible coefficient shells). "
            "Must be omitted when prefer_restricted_spatial_fermion_for_jordan_wigner is True."
        ),
    )

    @field_validator("frozen_orbitals")
    @classmethod
    def _validate_frozen_orbitals(cls, v: list[int]) -> list[int]:
        return validate_frozen_orbitals(v)

    @model_validator(mode="after")
    def _normalize_active_space_entry(self) -> ActiveSpaceSpec:
        normalize_active_space_entry(self)
        return self

    @model_validator(mode="after")
    def _jw_optimizer_flags_consistent(self) -> ActiveSpaceSpec:
        validate_jw_optimizer_flags(self)
        return self
