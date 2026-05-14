"""Closed-shell UCCSD-style variational state (Jordan–Wigner only).

Pauli averaging protocol in this stack prepends **HEA** on measurement circuits; UCCSD variational
energy is therefore combined with ``use_pauli_protocol: false`` (validated on :class:`~qchem_stack.config.ExperimentConfig`).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
import openfermion as of
from openfermion import get_sparse_operator, jordan_wigner
from scipy.linalg import expm
from scipy.optimize import minimize

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.integrations.ucc_reference import build_spin_uccsd_fermion_generators

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor


@dataclass
class UCCSDVQEResult:
    energy: float
    angles: np.ndarray
    nfev: int
    meta: dict[str, Any] = field(default_factory=dict)


class UCCSDVQE:
    """
    Product of cluster exponentials ``∏_k exp(θ_k (T_k - T_k†))`` on JW Hartree–Fock,
    with ``T_k`` single-reference UCCSD excitations (spin-orbital generators).
    """

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        *,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        self.hamiltonian = hamiltonian
        self.h_op = hamiltonian.operator
        self.n_qubits = hamiltonian.n_qubits
        self._executor = executor or StatevectorHeaExecutor()

        mapping = (hamiltonian.meta or {}).get("fermion_to_qubit_map")
        if mapping != "jordan_wigner":
            raise ValueError(
                "UCCSDVQE currently requires fermion_to_qubit_map='jordan_wigner' "
                f"(got {mapping!r}). Bravyi–Kitaev / SCBK reference-state bookkeeping differs."
            )
        fs = hamiltonian.fermion_space
        if fs is None:
            raise ValueError("UCCSDVQE requires hamiltonian.fermion_space for electron count.")
        self._n_so = int(fs.n_spin_orbitals)
        self._n_e = int(fs.n_electrons)
        if self._n_so != self.n_qubits:
            raise ValueError(
                f"JW UCCSD expects n_spin_orbitals == n_qubits ({self._n_so} vs {self.n_qubits})."
            )

        ferm_ops = build_spin_uccsd_fermion_generators(self._n_so, self._n_e)
        self._antiherm_mats: list[np.ndarray] = []
        for fo in ferm_ops:
            qop = jordan_wigner(fo)
            sm = get_sparse_operator(qop, n_qubits=self.n_qubits)
            d = sm.toarray()
            a = d - np.conjugate(d.T)
            self._antiherm_mats.append(np.asarray(a, dtype=np.complex128))
        self.n_params = len(self._antiherm_mats)

    def _reference_state(self) -> np.ndarray:
        v = np.asarray(of.jw_hartree_fock_state(self._n_e, self._n_so), dtype=np.complex128).ravel()
        nrm = float(np.linalg.norm(v))
        if nrm < 1e-14:
            raise ValueError("JW Hartree–Fock state has zero norm.")
        return v / nrm

    def _state_from_angles(self, angles: np.ndarray) -> np.ndarray:
        psi = self._reference_state()
        for th, a in zip(angles, self._antiherm_mats):
            psi = expm(float(th) * a) @ psi
        nrm = float(np.linalg.norm(psi))
        if nrm < 1e-14:
            raise ValueError("UCCSD state collapsed to zero norm.")
        return psi / nrm

    def run(
        self,
        maxiter: int = 200,
        *,
        seed: int = 0,
        executor: HamiltonianExpectationExecutor | None = None,
        record_energy_trace: bool = False,
        scipy_method: str = "COBYLA",
        bounds: Sequence[tuple[float, float]] | None = None,
        initial_parameters: np.ndarray | None = None,
        scipy_options: dict[str, Any] | None = None,
    ) -> UCCSDVQEResult:
        exe = executor or self._executor
        rng = np.random.default_rng(seed)
        if initial_parameters is not None:
            x0 = np.asarray(initial_parameters, dtype=float).ravel()
            if x0.shape != (self.n_params,):
                raise ValueError(f"initial_parameters must have shape ({self.n_params},), got {x0.shape}")
        else:
            x0 = rng.uniform(-np.pi, np.pi, size=self.n_params)
        nfev = 0
        trace: list[float] = []

        def objective(x: np.ndarray) -> float:
            nonlocal nfev
            nfev += 1
            st = self._state_from_angles(x)
            val = float(exe.expectation_state(st, self.h_op, self.n_qubits))
            if record_energy_trace:
                trace.append(val)
            return val

        opts: dict[str, Any] = {"maxiter": int(maxiter)}
        if scipy_options:
            opts.update(scipy_options)
        kwargs: dict[str, Any] = {
            "fun": objective,
            "x0": x0,
            "method": str(scipy_method),
            "options": opts,
        }
        if bounds is not None:
            kwargs["bounds"] = list(bounds)
        res = minimize(**kwargs)
        meta: dict[str, Any] = {
            "scipy_message": str(res.message),
            "variational_ansatz": "uccsd",
            "uccsd_n_parameters": self.n_params,
            "fermion_to_qubit_map": "jordan_wigner",
            "scipy_method": str(scipy_method),
        }
        if bounds is not None:
            meta["uccsd_parameter_bounds"] = [list(b) for b in bounds]
        if record_energy_trace:
            meta["energy_trace"] = list(trace)
        return UCCSDVQEResult(
            energy=float(res.fun),
            angles=np.asarray(res.x, dtype=float),
            nfev=nfev,
            meta=meta,
        )


class UCCSDTrotterVQE(UCCSDVQE):
    """Same cluster generators as :class:`UCCSDVQE`, but state prep uses a first-order product formula.

    Each optimization angle vector applies ``n_trotter_steps`` layers: for each layer, every generator
    is stepped with angle ``theta_k / n_trotter_steps`` (non-commuting fragments — differs from a single
    exact ``expm(theta_k A_k)`` chain when ``n_trotter_steps > 1``).
    """

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        *,
        executor: HamiltonianExpectationExecutor | None = None,
        n_trotter_steps: int = 1,
    ) -> None:
        super().__init__(hamiltonian, executor=executor)
        if n_trotter_steps < 1:
            raise ValueError("n_trotter_steps must be >= 1")
        self._n_trotter_steps = int(n_trotter_steps)

    def _state_from_angles(self, angles: np.ndarray) -> np.ndarray:
        psi = self._reference_state()
        inv = 1.0 / float(self._n_trotter_steps)
        for _ in range(self._n_trotter_steps):
            for th, a in zip(angles, self._antiherm_mats, strict=True):
                psi = expm(float(th * inv) * a) @ psi
                nrm = float(np.linalg.norm(psi))
                if nrm < 1e-14:
                    raise ValueError("UCCSD Trotter state collapsed to zero norm.")
                psi = psi / nrm
        return psi

    def run(
        self,
        maxiter: int = 200,
        *,
        seed: int = 0,
        executor: HamiltonianExpectationExecutor | None = None,
        record_energy_trace: bool = False,
        scipy_method: str = "COBYLA",
        bounds: Sequence[tuple[float, float]] | None = None,
        initial_parameters: np.ndarray | None = None,
        scipy_options: dict[str, Any] | None = None,
    ) -> UCCSDVQEResult:
        exe = executor or self._executor
        rng = np.random.default_rng(seed)
        if initial_parameters is not None:
            x0 = np.asarray(initial_parameters, dtype=float).ravel()
            if x0.shape != (self.n_params,):
                raise ValueError(f"initial_parameters must have shape ({self.n_params},), got {x0.shape}")
        else:
            x0 = rng.uniform(-np.pi, np.pi, size=self.n_params)
        nfev = 0
        trace: list[float] = []

        def objective(x: np.ndarray) -> float:
            nonlocal nfev
            nfev += 1
            st = self._state_from_angles(x)
            val = float(exe.expectation_state(st, self.h_op, self.n_qubits))
            if record_energy_trace:
                trace.append(val)
            return val

        opts: dict[str, Any] = {"maxiter": int(maxiter)}
        if scipy_options:
            opts.update(scipy_options)
        kwargs: dict[str, Any] = {
            "fun": objective,
            "x0": x0,
            "method": str(scipy_method),
            "options": opts,
        }
        if bounds is not None:
            kwargs["bounds"] = list(bounds)
        res = minimize(**kwargs)
        meta: dict[str, Any] = {
            "scipy_message": str(res.message),
            "variational_ansatz": "uccsd",
            "uccsd_n_parameters": self.n_params,
            "uccsd_trotter_steps": self._n_trotter_steps,
            "uccsd_product_formula": "first_order_layer_repeat",
            "fermion_to_qubit_map": "jordan_wigner",
            "scipy_method": str(scipy_method),
        }
        if bounds is not None:
            meta["uccsd_parameter_bounds"] = [list(b) for b in bounds]
        if record_energy_trace:
            meta["energy_trace"] = list(trace)
        return UCCSDVQEResult(
            energy=float(res.fun),
            angles=np.asarray(res.x, dtype=float),
            nfev=nfev,
            meta=meta,
        )
