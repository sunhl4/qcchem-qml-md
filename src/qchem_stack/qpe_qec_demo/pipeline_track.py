"""Pipeline-facing QPE demo track (dense Kitaev emulation + Bayesian toy).

Used by :func:`~qchem_stack.orchestration.pipeline._attach_qpe_demo_track_if_requested` and
``scripts/run_qpe_track_demo.py`` so dual-track YAML and scripts share one implementation.
"""

from __future__ import annotations

from typing import Any

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.qpe_qec_demo import BayesianQPEStub, kitaev_qpe_energy_estimate


def qpe_demo_track_payload(
    qh: QubitHamiltonian,
    *,
    bits: int = 4,
    bayesian_pairs: list[tuple[float, float]] | None = None,
) -> dict[str, Any]:
    pairs = bayesian_pairs if bayesian_pairs is not None else [(0.0, 0.5), (1.0, 1.0)]
    return {
        "schema": "qpe_qec_demo_track_v1",
        "kitaev_ground_energy_dense": float(kitaev_qpe_energy_estimate(qh, bits=bits)),
        "bayesian_phase_map_toy": BayesianQPEStub().estimate(pairs),
    }
