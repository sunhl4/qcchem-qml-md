"""Variational Scheduled Quantum Simulation (VSQS) VQE (arXiv:2003.09913)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from openfermion.ops import FermionOperator, QubitOperator
from scipy.linalg import expm
from scipy.optimize import minimize

from qchem_stack.chem.hamiltonian_mapping import _fermion_operator_to_qubits
from qchem_stack.quantum.statevector import expectation_qubit_operator, qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.chem.hamiltonian_meta import FermionQubitMappingName


@dataclass
class VSQSVQEResult:
    energy: float
    angles: np.ndarray
    nfev: int
    meta: dict[str, Any] = field(default_factory=dict)


def _strip_constant(qop: QubitOperator) -> list[tuple[tuple[tuple[int, str], ...], complex]]:
    return [(term, complex(coeff)) for term, coeff in qop.terms.items() if term]


def _build_hf_init_fermion(
    *,
    constant: float,
    h1: np.ndarray,
    h2: np.ndarray,
    n_active_mos: int,
    n_active_occupied: int,
) -> FermionOperator:
    diag_fock = np.diag(np.asarray(h1, dtype=float)).copy()
    tei = np.asarray(h2, dtype=float)
    for j in range(n_active_mos):
        for i in range(n_active_occupied):
            diag_fock[j] += 2.0 * tei[i, j, j, i] - tei[i, j, i, j]
    hf = FermionOperator((), float(constant))
    for i in range(n_active_mos):
        for j in range(n_active_mos):
            if i != j:
                hf += FermionOperator(((i * 2, 1), (j * 2, 0)), float(h1[i, j]))
                hf += FermionOperator(((i * 2 + 1, 1), (j * 2 + 1, 0)), float(h1[i, j]))
            else:
                hf += FermionOperator(((i * 2, 1), (j * 2, 0)), float(diag_fock[i]))
                hf += FermionOperator(((i * 2 + 1, 1), (j * 2 + 1, 0)), float(diag_fock[i]))
    return hf


def build_vsqs_h_init(
    hamiltonian: QubitHamiltonian,
    *,
    mapping: FermionQubitMappingName | None = None,
) -> QubitOperator:
    meta = hamiltonian.meta or {}
    h1 = meta.get("spatial_mo_h1")
    h2 = meta.get("spatial_mo_h2")
    if h1 is None or h2 is None:
        raise ValueError(
            "VSQS h_init requires spatial_mo_h1/spatial_mo_h2 in hamiltonian.meta "
            "(use the spatial CAS integral build path)."
        )
    h1a = np.asarray(h1, dtype=float)
    h2a = np.asarray(h2, dtype=float)
    n_mos = int(h1a.shape[0])
    if hamiltonian.fermion_space is not None:
        n_electrons = int(hamiltonian.fermion_space.n_electrons)
    else:
        n_electrons = int(meta.get("n_active_electrons") or 0)
    map_name = str(mapping or meta.get("fermion_to_qubit_map") or "jordan_wigner")
    if map_name == "hard_core_boson":
        raise ValueError("VSQS with hard_core_boson mapping is not supported.")
    n_spin = 2 * n_mos
    hf = _build_hf_init_fermion(
        constant=float(meta.get("spatial_mo_constant") or 0.0),
        h1=h1a,
        h2=h2a,
        n_active_mos=n_mos,
        n_active_occupied=n_electrons // 2,
    )
    return _fermion_operator_to_qubits(
        hf,
        map_name,  # type: ignore[arg-type]
        n_spin_orbitals=n_spin,
        n_active_fermions=n_electrons,
    )


def _apply_trotterized_pauli_sum(
    state: np.ndarray,
    terms: list[tuple[tuple[tuple[int, str], ...], complex]],
    angle: float,
    *,
    n_qubits: int,
    trotter_order: int,
) -> np.ndarray:
    if abs(float(angle)) < 1e-15 or not terms:
        return state
    order = terms if int(trotter_order) == 1 else terms + list(reversed(terms))
    psi = state
    pref = -1.0j * float(angle)
    for term, coeff in order:
        if abs(coeff) < 1e-15:
            continue
        mat = qubit_operator_to_sparse(QubitOperator(term, 1.0), n_qubits) * complex(coeff)
        psi = expm(pref * mat) @ psi
        nrm = float(np.linalg.norm(psi))
        if nrm < 1e-14:
            raise ValueError("VSQS Trotter layer collapsed state to zero norm.")
        psi = psi / nrm
    return psi


def _reference_state(hamiltonian: QubitHamiltonian) -> np.ndarray:
    from qchem_stack.quantum.algorithms.uccsd_mapping import reference_state_dense

    fs = hamiltonian.fermion_space
    if fs is None:
        raise ValueError("VSQSVQE requires fermion_space for HF reference.")
    mapping_raw = (hamiltonian.meta or {}).get("fermion_to_qubit_map")
    mapping = "jordan_wigner" if mapping_raw is None else str(mapping_raw)
    return reference_state_dense(
        mapping=mapping,
        n_spin_orbitals=int(fs.n_spin_orbitals),
        n_electrons=int(fs.n_electrons),
    )


def vsqs_prepare_statevector(
    hamiltonian: QubitHamiltonian,
    angles: np.ndarray,
    *,
    h_init: QubitOperator,
    intervals: int,
    dt: float,
    trotter_order: int,
) -> np.ndarray:
    h_final_terms = _strip_constant(hamiltonian.operator)
    h_init_terms = _strip_constant(h_init)
    n_q = int(hamiltonian.n_qubits)
    psi = _reference_state(hamiltonian)
    psi = _apply_trotterized_pauli_sum(
        psi, h_init_terms, dt, n_qubits=n_q, trotter_order=trotter_order
    )
    ang = np.asarray(angles, dtype=float).ravel()
    stride = 2
    expected = (int(intervals) - 1) * stride
    if ang.size != expected:
        raise ValueError(f"VSQS expects {expected} schedule angles, got {ang.size}")
    for step in range(int(intervals) - 1):
        a = float(ang[stride * step])
        b = float(ang[stride * step + 1])
        psi = _apply_trotterized_pauli_sum(
            psi, h_init_terms, a * dt, n_qubits=n_q, trotter_order=trotter_order
        )
        psi = _apply_trotterized_pauli_sum(
            psi, h_final_terms, b * dt, n_qubits=n_q, trotter_order=trotter_order
        )
    psi = _apply_trotterized_pauli_sum(
        psi, h_final_terms, dt, n_qubits=n_q, trotter_order=trotter_order
    )
    return psi


def vsqs_initial_angles(intervals: int, *, stride: int = 2) -> np.ndarray:
    n = int(intervals)
    if n <= 1:
        raise ValueError("VSQS intervals must be > 1")
    a = np.zeros(n + 1)
    b = np.zeros(n + 1)
    a[0] = 1.0
    b[n] = 1.0
    step = 1.0 / n
    for i in range(1, n):
        a[i] = 1.0 - i * step
        b[i] = i * step
    stacked = np.dstack((a, b)).reshape(-1)
    return np.asarray(stacked[stride : stride + (n - 1) * stride], dtype=float)


class VSQSVQE:
    """VSQS adiabatic-style state preparation with variational schedule (``h_init`` → ``h_final``)."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        *,
        intervals: int = 2,
        time: float = 1.0,
        trotter_order: int = 1,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        self.hamiltonian = hamiltonian
        self.h_op = hamiltonian.operator
        self.n_qubits = hamiltonian.n_qubits
        self.intervals = int(intervals)
        self.time = float(time)
        self.dt = self.time / self.intervals
        self.trotter_order = int(trotter_order)
        self._executor = executor or StatevectorHeaExecutor()
        self.h_init = build_vsqs_h_init(hamiltonian)
        self.n_params = (self.intervals - 1) * 2

    def _state_from_angles(self, angles: np.ndarray) -> np.ndarray:
        return vsqs_prepare_statevector(
            self.hamiltonian,
            angles,
            h_init=self.h_init,
            intervals=self.intervals,
            dt=self.dt,
            trotter_order=self.trotter_order,
        )

    def run(
        self,
        maxiter: int = 200,
        *,
        seed: int = 0,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> VSQSVQEResult:
        exe = executor or self._executor
        rng = np.random.default_rng(seed)
        x0 = vsqs_initial_angles(self.intervals) + rng.normal(scale=0.02, size=self.n_params)
        nfev = 0

        def objective(x: np.ndarray) -> float:
            nonlocal nfev
            nfev += 1
            st = self._state_from_angles(x)
            if hasattr(exe, "expectation_state"):
                return float(exe.expectation_state(st, self.h_op, self.n_qubits))  # type: ignore[attr-defined]
            return float(np.real(expectation_qubit_operator(st, self.h_op, self.n_qubits)))

        res = minimize(objective, x0, method="COBYLA", options={"maxiter": int(maxiter)})
        return VSQSVQEResult(
            energy=float(res.fun),
            angles=np.asarray(res.x, dtype=float),
            nfev=nfev,
            meta={
                "variational_ansatz": "vsqs",
                "vsqs_intervals": self.intervals,
                "vsqs_time": self.time,
                "vsqs_trotter_order": self.trotter_order,
                "vsqs_n_parameters": self.n_params,
            },
        )


def vsqs_algorithm_report_v1(result: VSQSVQEResult) -> dict[str, Any]:
    return {
        "schema": "algorithm_vsqs_report_v1",
        "algorithm": "vqe",
        "variational_ansatz": "vsqs",
        "final_value": float(result.energy),
        "nfev": int(result.nfev),
        "final_parameters": result.angles.tolist(),
        "meta": dict(result.meta),
    }
