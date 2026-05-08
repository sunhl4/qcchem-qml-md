from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from scipy.linalg import eigvalsh

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.base import AlgorithmBase
from qchem_stack.quantum.statevector import qubit_operator_to_sparse


@dataclass
class QPEResult:
    phase_mu: float
    phase_sigma: float
    energy_estimate: float
    meta: dict[str, Any] = field(default_factory=dict)


class AlgorithmDeterministicQPE(AlgorithmBase):
    """Canonical QPE-style dense estimator (algorithm surface compatible)."""

    def __init__(self, hamiltonian: QubitHamiltonian, time: float = 1.0, n_rounds: int = 4) -> None:
        super().__init__()
        self._algorithm_name = "deterministic_qpe"
        self._report_schema = "algorithm_deterministic_qpe_report_v1"
        self.hamiltonian = hamiltonian
        self.time = float(time)
        self.n_rounds = int(n_rounds)
        self._last: QPEResult | None = None

    def run(self, **kwargs: Any) -> QPEResult:
        self._ensure_built()
        mat = qubit_operator_to_sparse(self.hamiltonian.operator, self.hamiltonian.n_qubits)
        w = np.sort(np.real(eigvalsh(mat)))
        e0 = float(w[0])
        phi = float((-e0 * self.time) / (2.0 * np.pi))
        phi_mod = float(phi % 1.0)
        bit_precision = 2.0 ** (-max(1, self.n_rounds))
        out = QPEResult(
            phase_mu=phi_mod,
            phase_sigma=bit_precision,
            energy_estimate=e0,
            meta={"n_rounds": self.n_rounds, "time": self.time},
        )
        self._last = out
        self._set_report(
            metrics={"energy_estimate": out.energy_estimate},
            artifacts={"phase_mu": out.phase_mu, "phase_sigma": out.phase_sigma},
            diagnostics={"meta": dict(out.meta)},
        )
        return out


class AlgorithmKitaevQPE(AlgorithmBase):
    """Iterative-Kitaev style estimator over dense eigen spectrum."""

    def __init__(self, hamiltonian: QubitHamiltonian, time: float = 1.0, n_bits: int = 6) -> None:
        super().__init__()
        self._algorithm_name = "kitaev_qpe"
        self._report_schema = "algorithm_kitaev_qpe_report_v1"
        self.hamiltonian = hamiltonian
        self.time = float(time)
        self.n_bits = int(n_bits)
        self._last: QPEResult | None = None

    def run(self, **kwargs: Any) -> QPEResult:
        self._ensure_built()
        mat = qubit_operator_to_sparse(self.hamiltonian.operator, self.hamiltonian.n_qubits)
        w = np.sort(np.real(eigvalsh(mat)))
        e0 = float(w[0])
        phi = float((-e0 * self.time) / (2.0 * np.pi))
        phi_mod = float(phi % 1.0)
        precision = float(2.0 ** (-max(1, self.n_bits)))
        out = QPEResult(
            phase_mu=phi_mod,
            phase_sigma=precision,
            energy_estimate=float(e0),
            meta={
                "n_bits": self.n_bits,
                "time": self.time,
                "ground_energy_dense": float(e0),
                "phase_to_energy_bridge": "-phi_mu * (2*pi)/time is ambiguous without phase unwrap; report spectrum e0.",
            },
        )
        self._last = out
        self._set_report(
            metrics={"energy_estimate": out.energy_estimate},
            artifacts={"phase_mu": out.phase_mu, "phase_sigma": out.phase_sigma},
            diagnostics={"meta": dict(out.meta)},
        )
        return out


class AlgorithmInfoTheoryQPE(AlgorithmBase):
    """Information-theory style QPE wrapper with Gaussian posterior summary."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        time: float = 1.0,
        resolution: int = 2**10,
        n_samples: int = 64,
    ) -> None:
        super().__init__()
        self._algorithm_name = "info_theory_qpe"
        self._report_schema = "algorithm_info_theory_qpe_report_v1"
        self.hamiltonian = hamiltonian
        self.time = float(time)
        self.resolution = int(resolution)
        self.n_samples = int(n_samples)
        self._last: QPEResult | None = None

    def run(self, seed: int = 0, **kwargs: Any) -> QPEResult:
        self._ensure_built()
        rng = np.random.default_rng(seed)
        mat = qubit_operator_to_sparse(self.hamiltonian.operator, self.hamiltonian.n_qubits)
        w = np.sort(np.real(eigvalsh(mat)))
        e0 = float(w[0])
        phi = float(((-e0 * self.time) / (2.0 * np.pi)) % 1.0)
        sigma = float(max(1e-6, 1.0 / np.sqrt(max(1, self.n_samples))))
        phi_s = (phi + sigma * rng.normal(size=max(1, self.n_samples))) % 1.0
        mu = float(np.mean(phi_s))
        sd = float(np.std(phi_s))
        out = QPEResult(
            phase_mu=mu,
            phase_sigma=sd,
            energy_estimate=float(e0),
            meta={
                "resolution": self.resolution,
                "n_samples": self.n_samples,
                "time": self.time,
                "ground_energy_dense": float(e0),
                "note": "phase_mu aggregates noisy phase samples; energy_estimate anchored to dense e0.",
            },
        )
        self._last = out
        self._set_report(
            metrics={"energy_estimate": out.energy_estimate},
            artifacts={"phase_mu": out.phase_mu, "phase_sigma": out.phase_sigma},
            diagnostics={"meta": dict(out.meta)},
        )
        return out
