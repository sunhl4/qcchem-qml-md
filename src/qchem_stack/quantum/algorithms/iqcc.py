"""Iterative qubit coupled cluster (iQCC) and optional EN2 (iQCC+PT).

Research-grade open implementation aligned with the QCC → iQCC → iQCC+PT family
(Ryabinkin 2018/2020/2021; Genin et al. arXiv:2512.13657). Not bit-exact vs
closed-source industrial solvers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from typing import TYPE_CHECKING, Any, Literal

import numpy as np
from openfermion.ops import QubitOperator
from scipy.optimize import minimize

from qchem_stack.contracts.schema_ids import ALGORITHM_IQCC_REPORT_V1
from qchem_stack.quantum.algorithms.base import AlgorithmBase
from qchem_stack.quantum.algorithms.iqcc_dressing import (
    dress_product_unitary,
    reference_pauli_expectation,
    truncate_qubit_operator,
)
from qchem_stack.quantum.algorithms.tolerances import NUMERICAL_TOLERANCE
from qchem_stack.quantum.algorithms.uccsd_mapping import reference_state_dense
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import expectation_qubit_operator, qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian

__all__ = [
    "IQCCResult",
    "IQCCVQE",
    "build_genin_style_entanglers",
    "en2_correction",
    "iqcc_algorithm_report_v1",
    "zero_amplitude_gradient",
]

PoolMode = Literal["genin_dis", "iqeb_qubit_excitation"]


@dataclass
class IQCCResult:
    energy: float
    energy_variational: float
    energy_pt: float
    amplitudes_history: list[list[float]]
    selected_generators: list[str]
    nfev: int
    meta: dict[str, Any] = field(default_factory=dict)


def _is_single_pauli(op: QubitOperator) -> bool:
    return len(op.terms) == 1


def _normalize_pauli_generator(op: QubitOperator) -> QubitOperator | None:
    """Return a unit-coefficient single Pauli, or None if unsuitable for dressing."""
    if not _is_single_pauli(op):
        # Collapse anti-Hermitian qubit-excitation pairs into dominant Pauli when possible.
        terms = [
            (t, complex(c)) for t, c in op.terms.items() if abs(complex(c)) > NUMERICAL_TOLERANCE
        ]
        if not terms:
            return None
        # Prefer a term with odd number of Y (QCC-style entangler).
        ranked = sorted(
            terms,
            key=lambda tc: (
                sum(1 for _, p in tc[0] if p == "Y") != 1,
                -abs(tc[1]),
            ),
        )
        term, _ = ranked[0]
        return QubitOperator(term, 1.0)
    term, coeff = next(iter(op.terms.items()))
    if abs(abs(complex(coeff)) - 1.0) > 1.0e-6:
        return QubitOperator(term, 1.0)
    return QubitOperator(term, 1.0)


def build_genin_style_entanglers(n_qubits: int, *, max_weight: int = 4) -> list[QubitOperator]:
    """Genin-style generators: even weight, exactly one Y on the lowest support index, rest X."""
    n = int(n_qubits)
    max_w = max(2, int(max_weight))
    if max_w % 2:
        max_w -= 1
    out: list[QubitOperator] = []
    for weight in range(2, max_w + 1, 2):
        for idxs in combinations(range(n), weight):
            y_idx = min(idxs)
            term = [(y_idx, "Y")]
            for q in idxs:
                if q == y_idx:
                    continue
                term.append((q, "X"))
            term_t = tuple(sorted(term, key=lambda x: x[0]))
            out.append(QubitOperator(term_t, 1.0))
    return out


def zero_amplitude_gradient(
    hamiltonian: QubitOperator,
    generator: QubitOperator,
    reference: np.ndarray,
    n_qubits: int,
) -> float:
    """``g = Im⟨0|H T|0⟩`` (= ``-i/2 ⟨0|[H,T]|0⟩`` for Pauli ``T``)."""
    ht = hamiltonian * generator
    return float(np.imag(expectation_qubit_operator(reference, ht, n_qubits)))


def en2_correction(
    hamiltonian: QubitOperator,
    *,
    generators: list[QubitOperator],
    reference: np.ndarray,
    n_qubits: int,
    denom_cutoff: float,
    e0: float | None = None,
) -> tuple[float, list[dict[str, float]]]:
    """Epstein–Nesbet style second-order correction over unused DIS generators."""
    e_ref = (
        float(e0)
        if e0 is not None
        else reference_pauli_expectation(hamiltonian, reference, n_qubits)
    )
    delta = 0.0
    rows: list[dict[str, float]] = []
    for gen in generators:
        g = zero_amplitude_gradient(hamiltonian, gen, reference, n_qubits)
        php = gen * hamiltonian * gen
        e_flip = reference_pauli_expectation(php, reference, n_qubits)
        denom = e_ref - e_flip
        if abs(denom) < float(denom_cutoff):
            rows.append({"g": g, "D": denom, "contrib": 0.0, "skipped": 1.0})
            continue
        contrib = -(g * g) / denom
        delta += contrib
        rows.append({"g": g, "D": denom, "contrib": contrib, "skipped": 0.0})
    return float(delta), rows


class IQCCVQE(AlgorithmBase):
    """Iterative QCC with Hamiltonian dressing; optional EN2 (iQCC+PT)."""

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        *,
        max_steps: int = 4,
        top_k: int = 2,
        coeff_atol: float = 1.0e-8,
        max_terms: int | None = None,
        enable_pt: bool = False,
        denom_cutoff: float = 1.0e-6,
        pool_mode: PoolMode = "genin_dis",
        pool_id: str = "iqeb_qubit_excitation",
        max_weight: int = 4,
        energy_tolerance: float = 1.0e-8,
        maxiter_inner: int = 200,
        # Compat alias: historical ctor used max_ops for pool truncation width → top_k.
        max_ops: int | None = None,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        super().__init__()
        self._algorithm_name = "iqcc"
        self._report_schema = ALGORITHM_IQCC_REPORT_V1
        self.hamiltonian = hamiltonian
        self.n_qubits = int(hamiltonian.n_qubits)
        self.max_steps = max(1, int(max_steps))
        self.top_k = max(1, int(top_k if max_ops is None else max_ops))
        self.coeff_atol = float(coeff_atol)
        self.max_terms = None if max_terms is None else int(max_terms)
        self.enable_pt = bool(enable_pt)
        self.denom_cutoff = float(denom_cutoff)
        self.pool_mode = pool_mode
        self.pool_id = str(pool_id)
        self.max_weight = int(max_weight)
        self.energy_tolerance = float(energy_tolerance)
        self.maxiter_inner = int(maxiter_inner)
        self._executor = executor
        self._reference = self._build_reference()

    def _build_reference(self) -> np.ndarray:
        fs = self.hamiltonian.fermion_space
        if fs is None:
            # Computational |0…0⟩ fallback for toy Hamiltonians.
            st = np.zeros(2**self.n_qubits, dtype=complex)
            st[0] = 1.0
            return st
        mapping_raw = (self.hamiltonian.meta or {}).get("fermion_to_qubit_map")
        mapping = "jordan_wigner" if mapping_raw is None else str(mapping_raw)
        return reference_state_dense(
            mapping=str(mapping),
            n_spin_orbitals=int(fs.n_spin_orbitals),
            n_electrons=int(fs.n_electrons),
        )

    def _candidate_pool(self, h: QubitOperator) -> list[QubitOperator]:
        if self.pool_mode == "iqeb_qubit_excitation":
            raw = build_registered_operator_pool(self.pool_id, self.hamiltonian)
        else:
            raw = build_genin_style_entanglers(self.n_qubits, max_weight=self.max_weight)
        out: list[QubitOperator] = []
        seen: set[tuple[tuple[int, str], ...]] = set()
        for op in raw:
            gen = _normalize_pauli_generator(op)
            if gen is None:
                continue
            key = next(iter(gen.terms.keys()))
            if key in seen:
                continue
            seen.add(key)
            out.append(gen)
        return out

    def _rank_dis(
        self, h: QubitOperator, *, used: set[tuple[tuple[int, str], ...]]
    ) -> list[tuple[QubitOperator, float]]:
        ranked: list[tuple[QubitOperator, float]] = []
        for gen in self._candidate_pool(h):
            key = next(iter(gen.terms.keys()))
            if key in used:
                continue
            g = zero_amplitude_gradient(h, gen, self._reference, self.n_qubits)
            if abs(g) < NUMERICAL_TOLERANCE:
                continue
            ranked.append((gen, g))
        ranked.sort(key=lambda x: abs(x[1]), reverse=True)
        return ranked

    def _energy_of_amplitudes(
        self, h: QubitOperator, gens: list[QubitOperator], amps: np.ndarray
    ) -> float:
        # Prefer state propagation for objective (numerically stable for small systems).
        st = self._reference.copy()
        for tau, gen in zip(amps, gens, strict=True):
            if abs(float(tau)) < NUMERICAL_TOLERANCE:
                continue
            mat = qubit_operator_to_sparse(gen, self.n_qubits)
            # U = exp(-i τ P / 2)
            from scipy.linalg import expm

            st = expm(-0.5j * float(tau) * mat) @ st
            nrm = float(np.linalg.norm(st))
            if nrm < NUMERICAL_TOLERANCE:
                raise ValueError("iQCC state collapsed during amplitude optimization.")
            st = st / nrm
        return float(np.real(expectation_qubit_operator(st, h, self.n_qubits)))

    def _optimize_amplitudes(
        self, h: QubitOperator, gens: list[QubitOperator], *, seed: int
    ) -> tuple[np.ndarray, int]:
        n = len(gens)
        if n == 0:
            return np.zeros(0, dtype=float), 0
        rng = np.random.default_rng(seed)
        x0 = rng.uniform(-0.1, 0.1, size=n)
        nfev = 0

        def obj(x: np.ndarray) -> float:
            nonlocal nfev
            nfev += 1
            return self._energy_of_amplitudes(h, gens, np.asarray(x, dtype=float))

        res = minimize(obj, x0, method="COBYLA", options={"maxiter": self.maxiter_inner})
        return np.asarray(res.x, dtype=float), int(nfev)

    def run(self, *, maxiter: int | None = None, seed: int = 0) -> IQCCResult:
        if maxiter is not None:
            self.maxiter_inner = int(maxiter)
        h = QubitOperator()
        h += self.hamiltonian.operator
        used: set[tuple[tuple[int, str], ...]] = set()
        amp_hist: list[list[float]] = []
        selected_labels: list[str] = []
        steps_meta: list[dict[str, Any]] = []
        total_nfev = 0
        prev_e: float | None = None
        e_var = reference_pauli_expectation(h, self._reference, self.n_qubits)

        for step in range(self.max_steps):
            ranked = self._rank_dis(h, used=used)
            if not ranked:
                steps_meta.append({"step": step, "status": "empty_dis"})
                break
            chosen = ranked[: self.top_k]
            gens = [g for g, _ in chosen]
            grads = [float(g) for _, g in chosen]
            amps, nfev = self._optimize_amplitudes(h, gens, seed=seed + step)
            total_nfev += nfev
            e_before = reference_pauli_expectation(h, self._reference, self.n_qubits)
            h = dress_product_unitary(h, gens, amps)
            h = truncate_qubit_operator(h, coeff_atol=self.coeff_atol, max_terms=self.max_terms)
            e_var = reference_pauli_expectation(h, self._reference, self.n_qubits)
            amp_hist.append([float(a) for a in amps])
            for gen, amp in zip(gens, amps, strict=True):
                key = next(iter(gen.terms.keys()))
                used.add(key)
                label = " ".join(f"{p}{q}" for q, p in key) if key else "I"
                selected_labels.append(f"step{step}:{label}:tau={float(amp):.6g}")
            steps_meta.append(
                {
                    "step": step,
                    "n_terms": len(h.terms),
                    "energy_before_dress": float(e_before),
                    "energy_after_dress": float(e_var),
                    "gradients": grads,
                    "amplitudes": [float(a) for a in amps],
                    "top_k": len(gens),
                }
            )
            if prev_e is not None and abs(e_var - prev_e) < self.energy_tolerance:
                break
            prev_e = e_var

        e_pt = 0.0
        pt_rows: list[dict[str, float]] = []
        if self.enable_pt:
            unused = [g for g, _ in self._rank_dis(h, used=used)]
            e_pt, pt_rows = en2_correction(
                h,
                generators=unused,
                reference=self._reference,
                n_qubits=self.n_qubits,
                denom_cutoff=self.denom_cutoff,
                e0=e_var,
            )

        energy = float(e_var + e_pt)
        out = IQCCResult(
            energy=energy,
            energy_variational=float(e_var),
            energy_pt=float(e_pt),
            amplitudes_history=amp_hist,
            selected_generators=selected_labels,
            nfev=int(total_nfev),
            meta={
                "variational_ansatz": "iqcc",
                "algorithm": "iqcc_pt" if self.enable_pt else "iqcc",
                "pool_mode": self.pool_mode,
                "pool_id": self.pool_id,
                "max_steps": self.max_steps,
                "top_k": self.top_k,
                "coeff_atol": self.coeff_atol,
                "max_terms": self.max_terms,
                "enable_pt": self.enable_pt,
                "denom_cutoff": self.denom_cutoff,
                "n_terms_final": len(h.terms),
                "iqcc_steps": steps_meta,
                "en2_terms": pt_rows[:32],
                "open_stack_implementation": True,
            },
        )
        self._set_report(
            metrics={
                "energy": out.energy,
                "energy_variational": out.energy_variational,
                "energy_pt": out.energy_pt,
                "steps": len(steps_meta),
                "nfev": out.nfev,
            },
            artifacts={"selected_generators": selected_labels},
            diagnostics={"meta": dict(out.meta)},
        )
        return out


def iqcc_algorithm_report_v1(result: IQCCResult) -> dict[str, Any]:
    return {
        "schema": ALGORITHM_IQCC_REPORT_V1,
        "algorithm": "iqcc_pt" if result.meta.get("enable_pt") else "iqcc",
        "variational_ansatz": "iqcc",
        "final_value": float(result.energy),
        "energy_variational": float(result.energy_variational),
        "energy_pt": float(result.energy_pt),
        "nfev": int(result.nfev),
        "selected_generators": list(result.selected_generators),
        "meta": dict(result.meta),
    }
