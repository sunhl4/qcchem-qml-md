"""Fermion-to-qubit mapping sub-schema for active_space."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from ._base import ForbidExtraBase

FermionQubitMappingName = Literal[
    "jordan_wigner",
    "bravyi_kitaev",
    "symmetry_conserving_bravyi_kitaev",
]


class ActiveSpaceMappingSpec(ForbidExtraBase):
    fermion_qubit: FermionQubitMappingName = Field(
        default="jordan_wigner",
        description="Fermion-to-qubit mapping for the qubit Hamiltonian build path.",
    )
