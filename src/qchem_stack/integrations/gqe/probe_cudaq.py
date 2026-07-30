"""Optional cudaq-solvers install probe (Plan A PoC only; not the product path)."""

from __future__ import annotations

from typing import Any

from qchem_stack.contracts.schema_ids import GQE_PROBE_V1


def probe_cudaq_solvers_installation() -> dict[str, Any]:
    """Return import health for optional ``cudaq_solvers`` / ``cudaq``.

    Never raises: failures are encoded in ``available=False``.
    """
    out: dict[str, Any] = {
        "schema": GQE_PROBE_V1,
        "backend": "cudaq_solvers",
        "available": False,
        "packages": {},
        "role": "optional_poc_reference_only",
    }
    try:
        import cudaq  # type: ignore[import-not-found]

        out["packages"]["cudaq"] = {
            "available": True,
            "version": str(getattr(cudaq, "__version__", "unknown")),
        }
    except ImportError as e:
        out["packages"]["cudaq"] = {"available": False, "error": str(e)[:400]}

    try:
        import cudaq_solvers as solvers  # type: ignore[import-not-found]

        out["packages"]["cudaq_solvers"] = {
            "available": True,
            "version": str(getattr(solvers, "__version__", "unknown")),
            "has_gqe": hasattr(solvers, "gqe"),
        }
    except ImportError as e:
        out["packages"]["cudaq_solvers"] = {"available": False, "error": str(e)[:400]}
        return out

    cudaq_ok = bool(out["packages"].get("cudaq", {}).get("available"))
    solvers_ok = bool(out["packages"].get("cudaq_solvers", {}).get("available"))
    out["available"] = cudaq_ok and solvers_ok
    return out
