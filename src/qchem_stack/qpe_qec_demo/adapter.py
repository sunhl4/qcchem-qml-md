from __future__ import annotations

from dataclasses import dataclass

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.qpe_qec_demo.kitaev import kitaev_qpe_energy_estimate


@dataclass
class FaultTolerantDemoAdapter:
    """Isolated adapter toward ``qec_qpe_chem``-style experiments (no heavy QEC deps here)."""

    def ground_energy_dense(self, h: QubitHamiltonian) -> float:
        return kitaev_qpe_energy_estimate(h)
