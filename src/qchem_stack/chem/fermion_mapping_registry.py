"""Documented fermion→qubit mappings and public tutorial alias surface (chem layer)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import (
    MAPPING_STATUS_ROWS_V1,
    PUBLIC_MAPPING_ALIAS_SURFACE_V1,
)

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian_meta import FermionQubitMappingName

DOCUMENTED_FERMION_QUBIT_MAPPINGS: tuple[FermionQubitMappingName, ...] = (
    "jordan_wigner",
    "bravyi_kitaev",
    "symmetry_conserving_bravyi_kitaev",
    "jkmn",
    "hard_core_boson",
)


def list_documented_fermion_qubit_mappings() -> list[str]:
    return list(DOCUMENTED_FERMION_QUBIT_MAPPINGS)


def mapping_status_rows_v1() -> list[dict[str, Any]]:
    """Execution status for YAML literals vs research-stack nicknames."""
    notes = {
        "jordan_wigner": "Wired in chem.hamiltonian build paths.",
        "bravyi_kitaev": "Wired in chem.hamiltonian build paths.",
        "symmetry_conserving_bravyi_kitaev": "Wired in chem.hamiltonian build paths.",
        "jkmn": "Ternary-tree JKMN mapping (arXiv:1910.10746); spatial CAS build path.",
        "hard_core_boson": "Hard-core boson paired-electron mapping; spatial CAS build path.",
    }
    return [
        {
            "yaml_literal": lit,
            "execution_status": "executable",
            "executable": True,
            "notes": notes.get(lit, "Wired in chem.hamiltonian build paths."),
        }
        for lit in DOCUMENTED_FERMION_QUBIT_MAPPINGS
    ]


def public_mapping_alias_surface_v1() -> dict[str, Any]:
    """L1 table: tutorial nicknames vs executable YAML literals."""
    tutorial_rows = [
        {"tutorial_alias": "JW", "yaml_literal": "jordan_wigner", "executable": True},
        {"tutorial_alias": "BK", "yaml_literal": "bravyi_kitaev", "executable": True},
        {
            "tutorial_alias": "SCBK",
            "yaml_literal": "symmetry_conserving_bravyi_kitaev",
            "executable": True,
        },
        {"tutorial_alias": "JKMN", "yaml_literal": "jkmn", "executable": True},
        {"tutorial_alias": "HCB", "yaml_literal": "hard_core_boson", "executable": True},
    ]
    return {
        "schema": PUBLIC_MAPPING_ALIAS_SURFACE_V1,
        "qchem_stack_documented_literals": list(DOCUMENTED_FERMION_QUBIT_MAPPINGS),
        "tutorial_alias_rows": tutorial_rows,
        "not_executable_named_in_research_stack": [],
        MAPPING_STATUS_ROWS_V1: mapping_status_rows_v1(),
    }


def tangelo_public_mapping_alias_surface_v1() -> dict[str, Any]:
    """Deprecated export alias; prefer :func:`public_mapping_alias_surface_v1`."""
    return public_mapping_alias_surface_v1()
