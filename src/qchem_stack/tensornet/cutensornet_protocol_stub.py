"""
CuTensorNet *protocol* stand-in: optional ``opt_einsum`` / NumPy / CuPy demos without vendor binaries.

A future optional backend can replace the contraction body with :mod:`cuquantum.cutensornet`.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from qchem_stack.contracts.schema_ids import CUTENSORTNET_PROTOCOL_STUB_V1


def _demo_triangle_closed_path() -> tuple[str, list[np.ndarray], int]:
    """Build a 3-tensor network that contracts to a scalar (parity-sized demo)."""
    rng = np.random.default_rng(0)
    a = rng.standard_normal((2, 2))
    b = rng.standard_normal((2, 2))
    c = rng.standard_normal((2, 2))
    return "ij,jk,ki->", [a, b, c], 2


def run_cutensornet_expectation_stub(
    n_qubits: int,
    *,
    requested_backend: str = "stub",
) -> dict[str, Any]:
    """
    Vendor ``CuTensorNetProtocol``-style **machine-readable** row (open stack).

    Parameters
    ----------
    n_qubits
        Qubit count (propagated to metadata only here).
    requested_backend
        ``stub`` | ``opt_einsum`` | ``cupy_if_available`` — no Quantinuum GPU requirement.
    """
    be = (requested_backend or "stub").lower()
    if be in ("cupy", "cupy_if_available", "cupyifavailable"):
        be = "cupy_if_available"
    if be in ("cuquantum", "cuquantum_if_available", "cuquantumifavailable"):
        be = "cuquantum_if_available"

    base: dict[str, Any] = {
        "schema": CUTENSORTNET_PROTOCOL_STUB_V1,
        "n_qubits": int(n_qubits),
        "requested_backend": requested_backend,
    }

    if be == "stub":
        return {
            **base,
            "status": "stub_no_contraction",
            "note": "Open-stack placeholder; set tensornet_contraction_engine=opt_einsum in YAML for a demo path.",
        }

    subscripts, ops, _chi = _demo_triangle_closed_path()
    if be == "opt_einsum":
        import opt_einsum as oe

        _path, path_info = oe.contract_path(subscripts, *ops, optimize="optimal")
        val = float(oe.contract(subscripts, *ops, optimize="optimal"))
        out: dict[str, Any] = {
            **base,
            "status": "opt_einsum_demo_ok",
            "engine_resolved": "opt_einsum",
            "contraction_value": val,
            "einsum_subscripts": subscripts,
        }
        if hasattr(path_info, "largest_intermediate"):
            out["largest_intermediate"] = getattr(path_info, "largest_intermediate", None)
        return out

    if be == "cupy_if_available":
        try:
            import cupy as cp  # type: ignore[import-not-found]
        except Exception:  # noqa: BLE001
            import opt_einsum as oe

            val = float(oe.contract(subscripts, *ops, optimize="optimal"))
            return {
                **base,
                "status": "cupy_unavailable_fell_back_numpy_opt_einsum",
                "engine_resolved": "opt_einsum_fallback",
                "contraction_value": val,
                "einsum_subscripts": subscripts,
            }
        c_ops = [cp.asarray(x) for x in ops]
        expr = "ij,jk,ki->"
        # einsum on GPU arrays
        val = float(cp.einsum(expr, c_ops[0], c_ops[1], c_ops[2]))
        return {
            **base,
            "status": "cupy_einsum_demo_ok",
            "engine_resolved": "cupy",
            "contraction_value": val,
        }

    if be == "cuquantum_if_available":
        try:
            import cuquantum  # type: ignore[import-not-found]  # noqa: F401
        except Exception:
            subscripts, ops, _chi = _demo_triangle_closed_path()
            import opt_einsum as oe

            val = float(oe.contract(subscripts, *ops, optimize="optimal"))
            return {
                **base,
                "status": "cuquantum_not_installed_fell_back_opt_einsum",
                "engine_resolved": "opt_einsum_fallback",
                "contraction_value": val,
                "note": "Install NVIDIA cuQuantum (cuTensorNet) for GPU contraction; see NVIDIA docs.",
            }
        return {
            **base,
            "status": "cuquantum_import_ok",
            "engine_resolved": "cuquantum",
            "note": "cuQuantum is importable; wire a real tensor network + cutensornet handle in a plugin for production.",
        }

    return {
        **base,
        "status": "unknown_backend",
        "note": f"unhandled requested_backend={requested_backend!r}",
    }
