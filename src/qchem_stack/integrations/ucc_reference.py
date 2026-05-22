"""
UCC / **chemically aware** reference layer (compat re-export).

Implementation moved to :mod:`qchem_stack.chem.kernels.spin_ucc`.
"""

from __future__ import annotations

import warnings

from qchem_stack.chem.kernels import spin_ucc as _spin_ucc

_DEPRECATION = (
    "qchem_stack.integrations.ucc_reference is deprecated; "
    "import from qchem_stack.chem.kernels.spin_ucc instead"
)


def _warn_deprecated() -> None:
    warnings.warn(_DEPRECATION, DeprecationWarning, stacklevel=3)


ChemicallyAwareUCCPolicy = _spin_ucc.ChemicallyAwareUCCPolicy
IdentityRegrouping = _spin_ucc.IdentityRegrouping
SinglesBeforeDoublesLexicographic = _spin_ucc.SinglesBeforeDoublesLexicographic
GreedyCommutingFermionicLayers = _spin_ucc.GreedyCommutingFermionicLayers


def count_uccsd_excitations(n_spin_orbitals: int, n_electrons: int) -> dict[str, int]:
    _warn_deprecated()
    return _spin_ucc.count_uccsd_excitations(n_spin_orbitals, n_electrons)


def build_spin_ucc_doubles_only_fermion_generators(*args: object, **kwargs: object):
    _warn_deprecated()
    return _spin_ucc.build_spin_ucc_doubles_only_fermion_generators(*args, **kwargs)  # type: ignore[arg-type]


def build_spin_ucc_singles_only_fermion_generators(*args: object, **kwargs: object):
    _warn_deprecated()
    return _spin_ucc.build_spin_ucc_singles_only_fermion_generators(*args, **kwargs)  # type: ignore[arg-type]


def build_spin_uccsd_fermion_generators(*args: object, **kwargs: object):
    _warn_deprecated()
    return _spin_ucc.build_spin_uccsd_fermion_generators(*args, **kwargs)  # type: ignore[arg-type]


__all__ = [
    "ChemicallyAwareUCCPolicy",
    "GreedyCommutingFermionicLayers",
    "IdentityRegrouping",
    "SinglesBeforeDoublesLexicographic",
    "build_spin_ucc_doubles_only_fermion_generators",
    "build_spin_ucc_singles_only_fermion_generators",
    "build_spin_uccsd_fermion_generators",
    "count_uccsd_excitations",
]
