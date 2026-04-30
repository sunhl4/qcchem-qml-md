#!/usr/bin/env python3
"""P2: Dual-track hook — NISQ lives in :mod:`orchestration.pipeline`; phase/QPE in ``qpe_qec_demo/``.

This script has **no PySCF** dependency. It prints Kitaev-style ground energy (dense emulate)
and a toy Bayesian phase MAP from :class:`BayesianQPEStub`, matching the public “QPE + NISQ”
product narrative without claiming Nexus or hardware parity.

Usage: ``python scripts/run_qpe_track_demo.py``
"""

from __future__ import annotations

from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.qpe_qec_demo import BayesianQPEStub, kitaev_qpe_energy_estimate


def main() -> None:
    h = QubitOperator(((0, "Z"),), 0.5) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=h, n_qubits=1, meta={"demo": "qpe_track"})
    e0 = kitaev_qpe_energy_estimate(qh, bits=4)
    print("kitaev_qpe_energy_estimate(ground, dense emul)", e0)
    stub = BayesianQPEStub()
    phase_map = stub.estimate([(0.0, 0.5), (1.0, 1.0)])
    print("BayesianQPEStub MAP phase (toy)", phase_map)


if __name__ == "__main__":
    main()
