"""Optional thin wrapper around ``cudaq_solvers.gqe`` for H₂ PoC contrast.

This is **not** the product path (Plan B). It exists so a machine with CUDA-Q
installed can sanity-check against the native JAX trainer without coupling the
core stack to NVIDIA runtimes.
"""

from __future__ import annotations

from typing import Any

from qchem_stack.integrations.gqe.probe_cudaq import probe_cudaq_solvers_installation


def cudaq_gqe_available() -> bool:
    return bool(probe_cudaq_solvers_installation().get("available"))


def describe_cudaq_gqe_adapter() -> dict[str, Any]:
    """Document how a PoC call would look; does not invoke CUDA-Q."""
    probe = probe_cudaq_solvers_installation()
    return {
        "available": probe.get("available"),
        "probe": probe,
        "note": (
            "Call cudaq_solvers.gqe(...) only in user scripts. "
            "Native GQE must use HamiltonianExpectationExecutor via cost_bridge."
        ),
        "recommended_native_entry": "qchem_stack.integrations.gqe.native.trainer.run_gqe_lm_loop",
    }
