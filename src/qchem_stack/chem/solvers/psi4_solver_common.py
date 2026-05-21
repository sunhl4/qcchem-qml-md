"""Version probe and shared helpers for the Psi4 solver adapter."""

from __future__ import annotations


def psi4_version_or_unknown() -> str:
    try:
        import psi4

        v = getattr(psi4, "__version__", "")
        if isinstance(v, str) and v.strip():
            return v.strip()
    except Exception:  # pragma: no cover
        pass
    return "unknown"
