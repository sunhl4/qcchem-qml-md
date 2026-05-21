"""Pipeline-facing QPE demo track (dense Kitaev emulation + Bayesian toy).

Used by :func:`~qchem_stack.orchestration.pipeline._attach_qpe_demo_track_if_requested` and
``scripts/run_qpe_track_demo.py`` so dual-track YAML and scripts share one implementation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast

from qchem_stack.contracts.schema_ids import PHASE_ESTIMATION_CONTRACT_V1, QPE_QEC_DEMO_TRACK_V1
from qchem_stack.qpe_qec_demo import BayesianQPEStub, kitaev_qpe_energy_estimate
from qchem_stack.quantum.algorithms.qpe import (
    AlgorithmInfoTheoryQPE,
    AlgorithmKitaevQPE,
)

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


def qpe_demo_track_payload(
    qh: QubitHamiltonian,
    *,
    bits: int = 4,
    bayesian_pairs: list[tuple[float, float]] | None = None,
) -> dict[str, Any]:
    pairs = bayesian_pairs if bayesian_pairs is not None else [(0.0, 0.5), (1.0, 1.0)]
    kitaev_alg = cast("AlgorithmKitaevQPE", AlgorithmKitaevQPE(qh, n_bits=max(2, bits)).build())
    info_alg = cast("AlgorithmInfoTheoryQPE", AlgorithmInfoTheoryQPE(qh, n_samples=32).build())
    kitaev = kitaev_alg.run()
    info = info_alg.run(seed=17)
    return {
        "schema": QPE_QEC_DEMO_TRACK_V1,
        "phase_estimation_contract_v1": {
            "schema": PHASE_ESTIMATION_CONTRACT_V1,
            "implementations_surfaces": (
                "AlgorithmKitaevQPE + AlgorithmInfoTheoryQPE in qchem_stack.quantum.algorithms.qpe; "
                "dense emulation only (Methods sidecar)."
            ),
            "kitaev_register_bits_requested": max(2, bits),
            "info_theory_n_samples_fixed": 32,
            "bayesian_stub_symbol": "BayesianQPEStub",
            "bayesian_stub_module": "qchem_stack.qpe_qec_demo.bayesian_stub",
        },
        "kitaev_ground_energy_dense": float(kitaev_qpe_energy_estimate(qh, bits=bits)),
        "kitaev_phase_mu": float(kitaev.phase_mu),
        "kitaev_phase_precision": float(kitaev.phase_sigma),
        "info_theory_energy_mu": float(info.energy_estimate),
        "info_theory_phase_sigma": float(info.phase_sigma),
        "bayesian_phase_map_toy": BayesianQPEStub().estimate(pairs),
    }
