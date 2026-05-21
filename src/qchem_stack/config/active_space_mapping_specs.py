"""Fermion-to-qubit mapping sub-schema for active_space."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

_FORBID = ConfigDict(extra="forbid")

FermionQubitMappingName = Literal[
    "jordan_wigner",
    "bravyi_kitaev",
    "symmetry_conserving_bravyi_kitaev",
]


class ActiveSpaceMappingSpec(BaseModel):
    model_config = _FORBID

    fermion_qubit: FermionQubitMappingName = Field(
        default="jordan_wigner",
        description="Fermion-to-qubit mapping for the qubit Hamiltonian build path.",
    )
