"""Shared helpers for chemistry solver adapters."""

from __future__ import annotations


def package_version_or_unknown(module_name: str) -> str:
    """Import *module_name* and return its ``__version__`` or ``"unknown"``."""
    try:
        import importlib

        mod = importlib.import_module(module_name)
        v = getattr(mod, "__version__", "")
        if isinstance(v, str) and v.strip():
            return v.strip()
    except Exception:  # pragma: no cover
        pass
    return "unknown"
