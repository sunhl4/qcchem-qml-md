"""Closed-shell spin-orbital UCCSD variational ansatz.

Pauli averaging protocol prepends HEA circuits; dense UCCSD energy uses ``use_pauli_protocol: false``.

Transforms:
  * ``jordan_wigner``: JW Hartree–Fock reference + JW-mapped fermionic generators; optional
    fixed-particle-sector projection (:func:`jw_number_indices`) after propagation.
  * ``bravyi_kitaev``: BK-mapped fermionic creation-string reference on computational vacuum plus
    BK-matched cluster generators (**no** OpenFermion JW particle projector on BK-encoded states).

``symmetry_conserving_bravyi_kitaev`` is **unsupported** because the truncated qubit Hilbert space
does not match the JW/BK-square layout required here.

Trotterized cluster prep (:class:`UCCSDTrotterVQE`) inherits the same mapping semantics as the dense chain.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
import openfermion as of
from openfermion import bravyi_kitaev, get_sparse_operator, jordan_wigner
from openfermion.linalg.sparse_tools import jw_number_indices
from openfermion.ops import FermionOperator, QubitOperator
from scipy.linalg import expm
from scipy.optimize import minimize

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.integrations.ucc_reference import build_spin_uccsd_fermion_generators

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor


def _occupied_string_creation_op(n_electrons: int) -> FermionOperator:
    op = FermionOperator(())
    for spin_orb_idx in range(int(n_electrons)):
        op *= FermionOperator(((int(spin_orb_idx), 1),), 1.0)
    return op


def _map_fermion_generator(
    ferm_op: FermionOperator,
    mapping: str,
) -> QubitOperator:
    if mapping == "jordan_wigner":
        q = jordan_wigner(ferm_op)
    elif mapping == "bravyi_kitaev":
        q = bravyi_kitaev(ferm_op)
    else:
        raise ValueError(f"Unsupported fermion_to_qubit_map for UCCSDVQE: {mapping!r}")
    if not isinstance(q, QubitOperator):
        raise TypeError(f"Expected QubitOperator from OpenFermion map, got {type(q)}")
    return q


def _reference_state_dense(*, mapping: str, n_spin_orbitals: int, n_electrons: int) -> np.ndarray:
    if mapping == "jordan_wigner":
        v = np.asarray(of.jw_hartree_fock_state(int(n_electrons), int(n_spin_orbitals)), dtype=np.complex128).ravel()
    elif mapping == "bravyi_kitaev":
        fop = _occupied_string_creation_op(int(n_electrons))
        q_op = bravyi_kitaev(fop)
        mat = get_sparse_operator(q_op, n_qubits=int(n_spin_orbitals))
        vac = np.zeros(2 ** int(n_spin_orbitals), dtype=np.complex128)
        vac[0] = 1.0
        v = np.asarray(mat @ vac, dtype=np.complex128).ravel()
    else:
        raise ValueError(mapping)
    nrm = float(np.linalg.norm(v))
    if nrm < 1e-14:
        raise ValueError("UCCSD reference state has zero norm.")
    return v / nrm


@dataclass
class UCCSDVQEResult:
    energy: float
    angles: np.ndarray
    nfev: int
    meta: dict[str, Any] = field(default_factory=dict)


class UCCSDVQE:
    """
    Product ``∏_k exp(θ_k (T_k - T_k†))`` on the fermion-mapped HF reference, with JW or BK coherence.
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

        mapping_raw = (hamiltonian.meta or {}).get("fermion_to_qubit_map")
        mapping = "jordan_wigner" if mapping_raw is None else str(mapping_raw)
        if mapping == "symmetry_conserving_bravyi_kitaev":
            raise ValueError(
                "UCCSD dense cluster ansatz requires a square fermion encoding "
                "(jordan_wigner or bravyi_kitaev with n_spin_orbitals == n_qubits)."
            )

        fs = hamiltonian.fermion_space
        if fs is None:
            raise ValueError("UCCSDVQE requires hamiltonian.fermion_space for electron count.")
        self._fermion_mapping = mapping
        self._n_so = int(fs.n_spin_orbitals)
        self._n_e = int(fs.n_electrons)
        if self._n_so != self.n_qubits:
            raise ValueError(f"JW/BK-square UCCSD expects n_spin_orbitals == n_qubits ({self._n_so} vs {self.n_qubits}).")

        ferm_ops = build_spin_uccsd_fermion_generators(self._n_so, self._n_e)
        self._antiherm_mats: list[np.ndarray] = []
        for fer in ferm_ops:
            qop = _map_fermion_generator(fer, self._fermion_mapping)
            sm = get_sparse_operator(qop, n_qubits=self.n_qubits)
            d = sm.toarray()
            a = d - np.conjugate(d.T)
            self._antiherm_mats.append(np.asarray(a, dtype=np.complex128))
        self.n_params = len(self._antiherm_mats)

    def _reference_state(self) -> np.ndarray:
        return _reference_state_dense(
            mapping=self._fermion_mapping,
            n_spin_orbitals=self._n_so,
            n_electrons=self._n_e,
        )

    def _project_jw_fixed_electron_sector(self, psi: np.ndarray) -> np.ndarray:
        out = np.zeros_like(psi, dtype=np.complex128)
        for i in jw_number_indices(self._n_e, self.n_qubits):
            out[i] = psi[i]
        nrm = float(np.linalg.norm(out))
        if nrm < 1e-14:
            return self._reference_state()
        return out / nrm

    def _post_propagation_state(self, psi: np.ndarray) -> np.ndarray:
        """JW: sector projector; BK: normalization only."""
        if self._fermion_mapping == "jordan_wigner":
            return self._project_jw_fixed_electron_sector(psi)
        nrm = float(np.linalg.norm(psi))
        if nrm < 1e-14:
            raise ValueError("UCCSD state collapsed to zero norm after propagation.")
        return psi / nrm

    def _state_from_angles(self, angles: np.ndarray) -> np.ndarray:
        psi = self._reference_state()
        for th, a in zip(angles, self._antiherm_mats):
            psi = expm(float(th) * a) @ psi
            nrm = float(np.linalg.norm(psi))
            if nrm < 1e-14:
                raise ValueError("UCCSD state collapsed to zero norm.")
            psi = psi / nrm
        return self._post_propagation_state(psi)

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
        proj_meta = True if self._fermion_mapping == "jordan_wigner" else False
        meta: dict[str, Any] = {
            "scipy_message": str(res.message),
            "variational_ansatz": "uccsd",
            "uccsd_n_parameters": self.n_params,
            "fermion_to_qubit_map": self._fermion_mapping,
            "jw_fixed_electron_sector_projection": proj_meta,
            "scipy_method": str(scipy_method),
        }
        if self._fermion_mapping == "bravyi_kitaev":
            meta["mapping_note"] = (
                "BK-encoded reference + BK-matched cluster exponentials on square Hilbert; "
                "no JW particle-sector projector."
            )
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
    """First-order symmetric-product cluster approximations (same fermion mapping chain as dense)."""

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
        return self._post_propagation_state(psi)

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
        proj_meta = True if self._fermion_mapping == "jordan_wigner" else False
        meta: dict[str, Any] = {
            "scipy_message": str(res.message),
            "variational_ansatz": "uccsd",
            "uccsd_n_parameters": self.n_params,
            "uccsd_trotter_steps": self._n_trotter_steps,
            "uccsd_product_formula": "first_order_layer_repeat",
            "fermion_to_qubit_map": self._fermion_mapping,
            "jw_fixed_electron_sector_projection": proj_meta,
            "scipy_method": str(scipy_method),
        }
        if self._fermion_mapping == "bravyi_kitaev":
            meta["mapping_note"] = (
                "BK-encoded reference + BK-matched cluster exponentials on square Hilbert; "
                "no JW particle-sector projector."
            )
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
