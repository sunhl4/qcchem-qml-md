"""String enums for quantum configuration (YAML-serializable pool ids)."""

from __future__ import annotations

from qchem_stack.config._str_enum import StrEnum


class OperatorPoolId(StrEnum):
    FERMIONIC_UCCSD = "fermionic_uccsd"
    UCCSD_JW = "uccsd_jw"
    UCCSD_SINGLES = "uccsd_singles"
    UCCSD_DOUBLES_ONLY = "uccsd_doubles_only"
    UCCSD_BRAVYI_KITAEV = "uccsd_bravyi_kitaev"
    UCCSD_BK = "uccsd_bk"
    UCCSD_BK_SINGLES = "uccsd_bk_singles"
    UCCSD_BK_DOUBLES_ONLY = "uccsd_bk_doubles_only"
    UCCSD_BK_SINGLES_THEN_DOUBLES = "uccsd_bk_singles_then_doubles"
    FERMIONIC_UCCSD_BRAVYI_KITAEV = "fermionic_uccsd_bravyi_kitaev"
    FERMIONIC_UCCSD_SINGLES = "fermionic_uccsd_singles"
    FERMIONIC_UCCSD_DOUBLES_ONLY = "fermionic_uccsd_doubles_only"
    FERMIONIC_UCCSD_SINGLES_BRAVYI_KITAEV = "fermionic_uccsd_singles_bravyi_kitaev"
    FERMIONIC_UCCSD_DOUBLES_BRAVYI_KITAEV_ONLY = "fermionic_uccsd_doubles_bravyi_kitaev_only"
    FERMIONIC_UCCSD_SINGLES_THEN_DOUBLES_BK_CONCAT = (
        "fermionic_uccsd_singles_then_doubles_bk_concat"
    )
    FERMIONIC_GENERALIZED_DOUBLES = "fermionic_generalized_doubles"
    FERMIONIC_SINGLES_DOUBLES_STAGGERED = "fermionic_singles_doubles_staggered"
    IQEB_QUBIT_EXCITATION = "iqeb_qubit_excitation"
    QUBIT_EXCITATION = "qubit_excitation"
    TOY_PAIR_XX = "toy_pair_xx"
