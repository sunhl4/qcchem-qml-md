"""Version probe and shared helpers for the Psi4 solver adapter."""

from __future__ import annotations


def psi4_version_or_unknown() -> str:
    from qchem_stack.chem.solvers._common import package_version_or_unknown

    return package_version_or_unknown("psi4")
