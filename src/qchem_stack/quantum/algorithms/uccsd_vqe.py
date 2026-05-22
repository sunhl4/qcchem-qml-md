"""Closed-shell spin-orbital UCCSD variational ansatz.

Pauli averaging may use ansatz-native prep (HEA or UCCSD CircuitIR); dense-only UCCSD VQE
still supports ``quantum.pauli.use_protocol: false`` for statevector energy without measurement circuits.

Transforms:
  * ``jordan_wigner``: JW Hartree–Fock reference + JW-mapped fermionic generators; optional
    fixed-particle-sector projection (:func:`jw_number_indices`) after propagation.
  * ``bravyi_kitaev``: BK-mapped fermionic creation-string reference on computational vacuum plus
    BK-matched cluster generators (**no** OpenFermion JW particle projector on BK-encoded states).

``symmetry_conserving_bravyi_kitaev`` is **unsupported** because the truncated qubit Hilbert space
does not match the JW/BK-square layout required here.

Trotterized cluster prep (:class:`UCCSDTrotterVQE`) inherits the same mapping semantics as the dense chain.

Mapping helpers live in :mod:`~qchem_stack.quantum.algorithms.uccsd_mapping`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
from openfermion.linalg.sparse_tools import jw_number_indices
from scipy.linalg import expm
from scipy.optimize import minimize

from qchem_stack.chem.kernels.spin_ucc import build_spin_uccsd_fermion_generators
from qchem_stack.contracts.schema_ids import (
    ALGORITHM_UCCSD_REPORT_V1,
    UCCSD_MAPPING_SUPPORT_MATRIX_V1,
)
from qchem_stack.quantum.algorithms.uccsd_mapping import (
    antihermitian_cluster_matrices,
    reference_state_dense,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


@dataclass
class UCCSDVQEResult:
    energy: float
    angles: np.ndarray
    nfev: int
    meta: dict[str, Any] = field(default_factory=dict)


def uccsd_algorithm_report_v1(result: UCCSDVQEResult) -> dict[str, Any]:
    """Standardized variational report for UCCSD VQE runs."""
    return {
        "schema": ALGORITHM_UCCSD_REPORT_V1,
        "algorithm": "vqe",
        "final_value": float(result.energy),
        "nfev": int(result.nfev),
        "final_parameters": np.asarray(result.angles, dtype=float).tolist(),
        "meta": dict(result.meta),
    }


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
            raise ValueError(
                f"JW/BK-square UCCSD expects n_spin_orbitals == n_qubits ({self._n_so} vs {self.n_qubits})."
            )

        ferm_ops = build_spin_uccsd_fermion_generators(self._n_so, self._n_e)
        self._antiherm_mats = antihermitian_cluster_matrices(
            ferm_ops,
            mapping=self._fermion_mapping,
            n_qubits=self.n_qubits,
        )
        self.n_params = len(self._antiherm_mats)

    def _reference_state(self) -> np.ndarray:
        return reference_state_dense(
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
        for th, a in zip(angles, self._antiherm_mats, strict=False):
            psi = expm(float(th) * a) @ psi
            nrm = float(np.linalg.norm(psi))
            if nrm < 1e-14:
                raise ValueError("UCCSD state collapsed to zero norm.")
            psi = psi / nrm
        return self._post_propagation_state(psi)

    def prepare_state(self, angles: np.ndarray) -> np.ndarray:
        """Dense statevector for variational parameters (e.g. VQD deflation on the UCCSD ansatz)."""
        return self._state_from_angles(np.asarray(angles, dtype=float))

    def _run_meta_base(self) -> dict[str, Any]:
        proj_meta = self._fermion_mapping == "jordan_wigner"
        meta: dict[str, Any] = {
            "variational_ansatz": "uccsd",
            "uccsd_n_parameters": self.n_params,
            "fermion_to_qubit_map": self._fermion_mapping,
            "jw_fixed_electron_sector_projection": proj_meta,
        }
        if self._fermion_mapping == "bravyi_kitaev":
            meta["mapping_note"] = (
                "BK-encoded reference + BK-matched cluster exponentials on square Hilbert; "
                "no JW particle-sector projector."
            )
        return meta

    def _run_variational_optimize(
        self,
        *,
        maxiter: int,
        seed: int,
        executor: HamiltonianExpectationExecutor | None,
        record_energy_trace: bool,
        scipy_method: str,
        bounds: Sequence[tuple[float, float]] | None,
        initial_parameters: np.ndarray | None,
        scipy_options: dict[str, Any] | None,
        extra_meta: dict[str, Any] | None = None,
    ) -> UCCSDVQEResult:
        exe = executor or self._executor
        rng = np.random.default_rng(seed)
        if initial_parameters is not None:
            x0 = np.asarray(initial_parameters, dtype=float).ravel()
            if x0.shape != (self.n_params,):
                raise ValueError(
                    f"initial_parameters must have shape ({self.n_params},), got {x0.shape}"
                )
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
        meta = self._run_meta_base()
        if extra_meta:
            meta.update(extra_meta)
        meta["scipy_message"] = str(res.message)
        meta["scipy_method"] = str(scipy_method)
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
        return self._run_variational_optimize(
            maxiter=maxiter,
            seed=seed,
            executor=executor,
            record_energy_trace=record_energy_trace,
            scipy_method=scipy_method,
            bounds=bounds,
            initial_parameters=initial_parameters,
            scipy_options=scipy_options,
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
        return self._run_variational_optimize(
            maxiter=maxiter,
            seed=seed,
            executor=executor,
            record_energy_trace=record_energy_trace,
            scipy_method=scipy_method,
            bounds=bounds,
            initial_parameters=initial_parameters,
            scipy_options=scipy_options,
            extra_meta={
                "uccsd_trotter_steps": self._n_trotter_steps,
                "uccsd_product_formula": "first_order_layer_repeat",
            },
        )


def uccsd_mapping_support_matrix_v1() -> dict[str, Any]:
    """Machine-readable boundary for UCCSD ansatz mapping support."""
    return {
        "schema": UCCSD_MAPPING_SUPPORT_MATRIX_V1,
        "yaml_fields": {
            "variational_ansatz": "quantum.variational.ansatz",
            "fermion_qubit_mapping": "active_space.mapping.fermion_qubit",
        },
        "rows": [
            {
                "fermion_qubit_mapping": "jordan_wigner",
                "support_status": "supported",
                "mode": "dense_and_trotter",
                "note": "Uses JW reference and optional fixed-electron-sector projection.",
            },
            {
                "fermion_qubit_mapping": "bravyi_kitaev",
                "support_status": "supported",
                "mode": "dense_and_trotter",
                "note": "Uses BK reference and BK-matched cluster generators.",
            },
            {
                "fermion_qubit_mapping": "symmetry_conserving_bravyi_kitaev",
                "support_status": "not_supported",
                "mode": "n_a",
                "note": (
                    "Truncated qubit-space mapping; current UCCSD implementation requires square "
                    "fermion encoding (n_spin_orbitals == n_qubits)."
                ),
            },
        ],
    }
