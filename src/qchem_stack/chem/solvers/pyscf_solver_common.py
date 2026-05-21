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
    try:
        import pyscf

        v = getattr(pyscf, "__version__", "")
        if isinstance(v, str) and v.strip():
            return v.strip()
    except Exception:  # pragma: no cover
        pass
    return "unknown"
