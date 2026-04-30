"""
Strategy map for **tensor-network expectation** vs statevector — open “closure” around the stub.

InQuanto ``inquanto-cutensornet`` binds vendor GPU paths; we keep **contract-level** switches
that point to :mod:`qchem_stack.tensornet.cutensornet_protocol_stub` and future engines.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class TensorNetClosureStrategy(str, Enum):
    """How to attempt TN / einsum closure for auditing (not a single best default)."""

    SV_ONLY = "sv_only"
    """No TN path; classical or Qiskit statevector only."""
    STUB_METADATA = "stub_metadata"
    """`run_cutensornet_expectation_stub` with ``requested_backend=stub`` — parity metadata row."""
    OPT_EINSUM_DEMO = "opt_einsum_demo"
    """Toy closed network via ``opt_einsum`` (proves contraction stack wiring)."""
    CUPY_IF_AVAILABLE = "cupy_if_available"
    CUQUANTUM_IF_AVAILABLE = "cuquantum_if_available"


def tensornet_closure_strategy() -> dict[str, Any]:
    """JSON-serializable map for docs / export sidecars."""
    return {
        "schema": "tensornet_closure_reference_v1",
        "strategies": [s.value for s in TensorNetClosureStrategy],
        "stub_entrypoint": "qchem_stack.tensornet.cutensornet_protocol_stub.run_cutensornet_expectation_stub",
        "cross_check_note": (
            "Small systems: compare SV energy to stub/opt_einsum demo; "
            "full chemistry hypergraph → TN is user-defined (no InQuanto graph clone)."
        ),
    }
