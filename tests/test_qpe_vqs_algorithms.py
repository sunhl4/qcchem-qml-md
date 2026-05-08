from __future__ import annotations

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.qpe import (
    AlgorithmDeterministicQPE,
    AlgorithmInfoTheoryQPE,
    AlgorithmKitaevQPE,
)
from qchem_stack.quantum.algorithms.vqs import (
    AlgorithmMcLachlanImagTime,
    AlgorithmMcLachlanRealTime,
)
from qchem_stack.quantum.algorithms.vqs_pipeline_track import vqs_track_payload


def _toy_hamiltonian() -> QubitHamiltonian:
    h = (
        QubitOperator(((0, "Z"),), -0.3)
        + QubitOperator(((1, "Z"),), -0.2)
        + QubitOperator(((0, "X"), (1, "X")), 0.1)
    )
    return QubitHamiltonian(operator=h, n_qubits=2)


def test_qpe_algorithms_smoke() -> None:
    qh = _toy_hamiltonian()
    d = AlgorithmDeterministicQPE(qh, time=0.7, n_rounds=5).build().run()
    k = AlgorithmKitaevQPE(qh, time=0.7, n_bits=6).build().run()
    i = AlgorithmInfoTheoryQPE(qh, time=0.7, n_samples=20).build().run(seed=0)
    assert np.isfinite(d.energy_estimate)
    assert 0.0 <= k.phase_mu < 1.0
    assert i.phase_sigma >= 0.0


def test_vqs_track_payload_smoke() -> None:
    qh = _toy_hamiltonian()
    n_params = 2 * qh.n_qubits * 1
    init = np.zeros(n_params, dtype=float)
    p = vqs_track_payload(
        qh, init, mode="mclachlan_real_time", n_times=5, dt=0.02
    )
    assert p["schema"] == "vqs_track_v1"
    assert len(p["times"]) == 5
    assert p["algorithm_report"].get("algorithm") == "mclachlan_real_time"


def test_vqs_algorithms_smoke() -> None:
    qh = _toy_hamiltonian()
    n_params = 2 * qh.n_qubits * 1
    init = np.zeros(n_params, dtype=float)
    times = np.linspace(0.0, 0.2, 6)
    r = AlgorithmMcLachlanRealTime(qh, init, times).build().run()
    im = AlgorithmMcLachlanImagTime(qh, init, times).build().run()
    assert len(r.trajectory) == len(times)
    assert len(im.trajectory) == len(times)
