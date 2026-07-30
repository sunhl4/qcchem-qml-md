"""Optional JAX / optax install probe for native GQE (no network)."""

from __future__ import annotations

from typing import Any

from qchem_stack.contracts.schema_ids import GQE_PROBE_V1


def probe_gqe_jax_installation() -> dict[str, Any]:
    """Return import health for optional ``jax`` / ``optax`` used by native GQE."""
    out: dict[str, Any] = {
        "schema": GQE_PROBE_V1,
        "backend": "jax",
        "available": False,
        "packages": {},
    }
    try:
        import jax  # type: ignore[import-not-found]

        out["packages"]["jax"] = {
            "available": True,
            "version": str(getattr(jax, "__version__", "unknown")),
        }
    except ImportError as e:
        out["packages"]["jax"] = {"available": False, "error": str(e)[:400]}
        return out

    try:
        import optax  # type: ignore[import-not-found]

        out["packages"]["optax"] = {
            "available": True,
            "version": str(getattr(optax, "__version__", "unknown")),
        }
    except ImportError as e:
        out["packages"]["optax"] = {"available": False, "error": str(e)[:400]}
        return out

    out["available"] = True
    return out
