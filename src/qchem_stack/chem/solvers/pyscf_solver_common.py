"""PySCF import helpers shared by solver submodules."""

from __future__ import annotations

from typing import Any


def require_pyscf() -> tuple[Any, Any]:
    try:
        from pyscf import gto, scf
    except ImportError as e:  # pragma: no cover
        raise ImportError("PySCF is required. Install with: pip install qchem-stack[chem]") from e
    return gto, scf


def pyscf_version_or_unknown() -> str:
    from qchem_stack.chem.solvers._common import package_version_or_unknown

    return package_version_or_unknown("pyscf")
