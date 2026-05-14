"""Documented fermion→qubit transforms (config + OpenFermion wiring).

See :attr:`qchem_stack.config.ActiveSpaceSpec.fermion_qubit_mapping` and :mod:`qchem_stack.chem.hamiltonian`.

Research distributions such as **Tangelo** additionally advertise JKMN / generalized mappings in tutorials.
Those identifiers remain **out-of-scope** for execution until each mapping gets explicit OpenFermion plumbing,
parity fixtures, and documentation parity rows (:data:`DOCUMENTED_FERMION_QUBIT_MAPPINGS` is the whitelist).
"""

from __future__ import annotations

from typing import Any, Final

DOCUMENTED_FERMION_QUBIT_MAPPINGS: Final[tuple[str, ...]] = (
    "jordan_wigner",
    "bravyi_kitaev",
    "symmetry_conserving_bravyi_kitaev",
)


def list_documented_fermion_qubit_mappings() -> tuple[str, ...]:
    return DOCUMENTED_FERMION_QUBIT_MAPPINGS


def tangelo_public_mapping_alias_surface_v1() -> dict[str, Any]:
    """
    L1 nickname alignment vs **Tangelo** / tutorial literature (JW, BK, SCBK, …).

    Executability is pinned to :data:`DOCUMENTED_FERMION_QUBIT_MAPPINGS` only — JKMN / HCB and
    other research mappings stay **explicitly undisclosed-as-executable** until OpenFermion plumbing
    + parity fixtures land (same epistemic bound as this module docstring).

    Surfaced from ``GET /v1/meta/capability-surface`` for dashboards / Methods appendix tables — **not**
    a claim of full Tangelo toolbox parity.
    """
    executable_rows = [
        {
            "public_aliases": [
                "JW",
                "Jordan-Wigner",
                "jordan-wigner",
                "Jordan-Wigner transformation",
            ],
            "qchem_stack": "jordan_wigner",
            "executable": True,
        },
        {
            "public_aliases": ["BK", "Bravyi-Kitaev", "bravyi-kitaev"],
            "qchem_stack": "bravyi_kitaev",
            "executable": True,
        },
        {
            "public_aliases": ["SCBK", "BKSC", "symmetry-conserving-Bravyi-Kitaev"],
            "qchem_stack": "symmetry_conserving_bravyi_kitaev",
            "executable": True,
        },
    ]
    non_exec_rows = [
        {
            "public_aliases": ["JKMN", "HCB"],
            "executable": False,
            "qchem_stack_status": "planned_not_wired",
            "note": (
                "Not wired in qchem-stack; keep parity matrix partial + whitelist "
                "DOCUMENTED_FERMION_QUBIT_MAPPINGS authoritative."
            ),
        },
    ]
    return {
        "schema": "tangelo_public_mapping_alias_surface_v1",
        "public_tool_references": [
            {"label": "tangelo_docs", "url": "https://sandbox-quantum.github.io/Tangelo/"},
            {"label": "tangelo_github", "url": "https://github.com/sandbox-quantum/Tangelo"},
        ],
        "epistemic_bound": (
            "Alias vocabulary for reproducibility narratives — executable mappings are YAML "
            "`active_space.fermion_qubit_mapping` literals in qchem-documented-whitelist form only."
        ),
        "yaml_config_field": "active_space.fermion_qubit_mapping",
        "qchem_stack_documented_literals": list(DOCUMENTED_FERMION_QUBIT_MAPPINGS),
        "tutorial_alias_rows": executable_rows,
        "not_executable_named_in_research_stack": non_exec_rows,
        "mapping_status_rows_v1": [
            *[
                {
                    "canonical_mapping": r["qchem_stack"],
                    "aliases": list(r["public_aliases"]),
                    "execution_status": "executable",
                }
                for r in executable_rows
            ],
            *[
                {
                    "canonical_mapping": "unknown_or_future",
                    "aliases": list(r["public_aliases"]),
                    "execution_status": str(r["qchem_stack_status"]),
                }
                for r in non_exec_rows
            ],
        ],
    }
