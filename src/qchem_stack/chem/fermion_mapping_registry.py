"""Documented fermion→qubit mappings and Tangelo tutorial alias surface (chem layer)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.contracts.schema_ids import (
    MAPPING_STATUS_ROWS_V1,
    TANGELO_PUBLIC_MAPPING_ALIAS_SURFACE_V1,
)

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian_meta import FermionQubitMappingName

DOCUMENTED_FERMION_QUBIT_MAPPINGS: tuple[FermionQubitMappingName, ...] = (
    "jordan_wigner",
    "bravyi_kitaev",
    "symmetry_conserving_bravyi_kitaev",
)


def list_documented_fermion_qubit_mappings() -> list[str]:
    return list(DOCUMENTED_FERMION_QUBIT_MAPPINGS)


def mapping_status_rows_v1() -> list[dict[str, Any]]:
    """Execution status for YAML literals vs research-stack nicknames."""
    rows: list[dict[str, Any]] = []
    for lit in DOCUMENTED_FERMION_QUBIT_MAPPINGS:
        rows.append(
            {
                "yaml_literal": lit,
                "execution_status": "executable",
                "notes": "Wired in chem.hamiltonian build paths.",
            }
        )
    for nick, note in (
        ("JKMN", "Jordan-Klein-Majorana-Navascués style; not wired in open stack."),
        ("HCB", "Honeycomb Bravyi-style nickname; not wired in open stack."),
    ):
        rows.append(
            {
                "research_stack_nickname": nick,
                "execution_status": "planned_not_wired",
                "executable": False,
                "notes": note,
            }
        )
    return rows


def tangelo_public_mapping_alias_surface_v1() -> dict[str, Any]:
    """L1 parity table: tutorial nicknames vs executable YAML literals."""
    tutorial_rows = [
        {
            "tutorial_alias": "JW",
            "yaml_literal": "jordan_wigner",
            "executable": True,
        },
        {
            "tutorial_alias": "BK",
            "yaml_literal": "bravyi_kitaev",
            "executable": True,
        },
        {
            "tutorial_alias": "SCBK",
            "yaml_literal": "symmetry_conserving_bravyi_kitaev",
            "executable": True,
        },
    ]
    not_executable = [
        {
            "research_stack_nickname": r["research_stack_nickname"],
            "execution_status": r["execution_status"],
            "executable": False,
            "notes": r.get("notes"),
        }
        for r in mapping_status_rows_v1()
        if r.get("execution_status") == "planned_not_wired"
    ]
    return {
        "schema": TANGELO_PUBLIC_MAPPING_ALIAS_SURFACE_V1,
        "qchem_stack_documented_literals": list(DOCUMENTED_FERMION_QUBIT_MAPPINGS),
        "tutorial_alias_rows": tutorial_rows,
        "not_executable_named_in_research_stack": not_executable,
        MAPPING_STATUS_ROWS_V1: mapping_status_rows_v1(),
    }
