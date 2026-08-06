"""SQD-family algorithm classes (peer level to VQE).

Implements dense / lite prototypes of algorithms from
``docs/基于采样的量子化学计算报告.pdf``:

CBS (dense truncated support), QSCI, SQD (+ S-CORE-lite), QSE+QSCI-lite
(subspace spectrum), ADAPT-QSCI, SKQD, SqDRIFT, HI-VQE-lite, EWF-TrimSQD-lite,
QBE-SQD-lite, SQD+ph-AFQMC-lite.

Epistemic bounds: dense statevector sampling / exact subspace diagonalization
for small qubit counts; not a drop-in for qiskit-addon-sqd at 50+ qubits.
See ``docs/quantum_模块风格约定.md`` §8.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any, cast

import numpy as np
from scipy.linalg import expm

from qchem_stack.contracts.schema_ids import ALGORITHM_SQD_REPORT_V1
from qchem_stack.quantum.algorithms.base import AlgorithmBase
from qchem_stack.quantum.algorithms.sqd.evolution import (
    krylov_states,
    qdrift_channel_state,
)
from qchem_stack.exceptions import QuantumAlgorithmError
from qchem_stack.quantum.algorithms.sqd.sampling import (
    default_hea_angles,
    ensure_nonempty_basis,
    filter_particle_number,
    fragment_qubit_ranges,
    hf_bitstring,
    hf_state,
    overlapping_fragment_ranges,
    particle_number_preserving_singles,
    popcount,
    prepare_hea_sampling_state,
    resolve_n_electrons,
    sample_bitstrings_from_state,
    select_sampled_basis,
    top_k_unique,
)
from qchem_stack.quantum.algorithms.sqd.subspace import (
    cbs_energy_estimate,
    diagonalize_subspace,
    recover_configurations,
    subspace_hamiltonian_matrix,
)
from qchem_stack.quantum.algorithms.sqd.types import (
    MAX_SQD_QUBITS,
    SqdConfig,
    SqdResult,
    sqd_customer_tier,
)
from qchem_stack.quantum.algorithms.tolerances import STATE_NORMALIZATION_FLOOR
from qchem_stack.quantum.operator_pool_registry import build_registered_operator_pool
from qchem_stack.quantum.statevector import expectation_qubit_operator, qubit_operator_to_sparse

if TYPE_CHECKING:
    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


def _unitary_pool_rotation(p_mat: np.ndarray, theta: float) -> np.ndarray:
    """Build a unitary from a pool generator matrix.

    Prefer the anti-Hermitian part ``A=(P-P†)/2`` with ``expm(θ A)``. If that
    vanishes (Hermitian toy Paulis), fall back to ``expm(-i θ H)`` on the
    Hermitian part.
    """
    ah = 0.5 * (p_mat - p_mat.conj().T)
    herm = 0.5 * (p_mat + p_mat.conj().T)
    if float(np.linalg.norm(ah)) > 1e-14:
        return np.asarray(expm(float(theta) * ah), dtype=np.complex128)
    return np.asarray(expm(-1j * float(theta) * herm), dtype=np.complex128)


class _SqdFamilyBase(AlgorithmBase):
    """Shared build/run/report plumbing for sample-based algorithms."""

    _algorithm_name: str = "sqd"
    _report_schema: str = ALGORITHM_SQD_REPORT_V1

    def __init__(
        self,
        hamiltonian: QubitHamiltonian,
        config: SqdConfig | None = None,
        *,
        executor: HamiltonianExpectationExecutor | None = None,
        **overrides: Any,
    ) -> None:
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        super().__init__()
        self.hamiltonian = hamiltonian
        self.h_op = hamiltonian.operator
        self.n_qubits = int(hamiltonian.n_qubits)
        if self.n_qubits > MAX_SQD_QUBITS:
            raise QuantumAlgorithmError(
                f"SQD-family dense prototype supports at most {MAX_SQD_QUBITS} qubits "
                f"(got n_qubits={self.n_qubits}). Reduce the active space, or use a "
                "hardware-capable algorithm such as VQE."
            )
        self._executor = executor or StatevectorHeaExecutor()
        cfg = config or SqdConfig()
        for key, value in overrides.items():
            if hasattr(cfg, key):
                cfg = replace(cfg, **{key: value})
        self.config = cfg
        self._last_result: SqdResult | None = None

    def build(self, **kwargs: Any) -> _SqdFamilyBase:
        return cast("_SqdFamilyBase", super().build(**kwargs))

    def _n_electrons(self) -> int | None:
        return resolve_n_electrons(self.hamiltonian, self.config.n_electrons)

    def _epistemic_base(self) -> dict[str, Any]:
        return {
            "dense_prototype": True,
            "execution_mode": "dense_statevector",
            "backend_executor_used": False,
            "literature_parity": False,
            "max_qubits_supported": MAX_SQD_QUBITS,
            "customer_tier": sqd_customer_tier(self._algorithm_name),
            "n_shots_total": None,
        }

    def _finalize(self, result: SqdResult) -> SqdResult:
        # Epistemic base wins over nested callee meta (e.g. QSCI inside QSE-lite).
        meta = {**dict(result.meta), **self._epistemic_base()}
        if meta.get("n_shots_total") is None:
            meta["n_shots_total"] = int(result.nfev)
        result.meta = meta
        self._last_result = result
        self._set_report(
            metrics={
                "energy": result.energy,
                "nfev": result.nfev,
                "subspace_size": len(result.selected_bitstrings),
            },
            artifacts={
                "selected_bitstrings": list(result.selected_bitstrings),
                "ci_coefficients": [complex(z) for z in result.ci_coefficients],
                "energy_trace": list(result.energy_trace),
                "final_parameters": result.angles.tolist(),
            },
            diagnostics={"meta": dict(result.meta)},
        )
        return result

    def generate_report(self) -> dict[str, Any]:
        if self._last_result is None:
            return super().generate_report()
        r = self._last_result
        return {
            "schema": ALGORITHM_SQD_REPORT_V1,
            "algorithm": self._algorithm_name,
            "final_value": float(r.energy),
            "nfev": int(r.nfev),
            "selected_bitstrings": list(r.selected_bitstrings),
            "energy_trace": list(r.energy_trace),
            "final_parameters": r.angles.tolist(),
            "meta": dict(r.meta),
        }

    def run(self, *, seed: int | None = None) -> SqdResult:  # pragma: no cover - override
        raise NotImplementedError


class CBS(_SqdFamilyBase):
    """Dense truncated computational-basis energy (CBS-inspired; not Kohda shot CBS).

    Epistemic bound: uses exact amplitudes on the top-R support. Literature CBS
    reconstructs off-diagonal interference via auxiliary circuits.
    """

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "cbs"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        rng = np.random.default_rng(self.config.seed if seed is None else seed)
        ne = self._n_electrons()
        angles = default_hea_angles(self.n_qubits, self.config.hea_depth, rng)
        psi = prepare_hea_sampling_state(
            self.n_qubits, angles, self.config.hea_depth, n_electrons=ne
        )
        if ne is not None:
            # Restrict support to the requested particle-number sector before truncation
            mask = np.array([popcount(i) == ne for i in range(2**self.n_qubits)], dtype=bool)
            psi = psi.copy()
            psi[~mask] = 0.0
            nrm = float(np.linalg.norm(psi))
            if nrm < STATE_NORMALIZATION_FLOOR:
                psi = hf_state(self.n_qubits, ne)
            else:
                psi = psi / nrm
        e, support = cbs_energy_estimate(
            psi, self.h_op, self.n_qubits, top_r=self.config.subspace_size
        )
        return self._finalize(
            SqdResult(
                energy=e,
                angles=angles,
                nfev=1,
                selected_bitstrings=support,
                energy_trace=[e],
                meta={
                    "method": "cbs",
                    "variant": "dense_truncated_support",
                    "kohda_interference_circuits": False,
                },
            )
        )


class QSCI(_SqdFamilyBase):
    """Quantum-Selected Configuration Interaction (Kanno et al. 2023) — dense lite."""

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "qsci"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        rng = np.random.default_rng(self.config.seed if seed is None else seed)
        ne = self._n_electrons()
        angles = default_hea_angles(self.n_qubits, self.config.hea_depth, rng)
        psi = prepare_hea_sampling_state(
            self.n_qubits, angles, self.config.hea_depth, n_electrons=ne
        )
        samples = sample_bitstrings_from_state(psi, n_shots=self.config.n_shots, rng=rng)
        basis, sample_meta = select_sampled_basis(
            samples,
            subspace_size=self.config.subspace_size,
            n_qubits=self.n_qubits,
            n_electrons=ne,
        )
        e, c, _occ = diagonalize_subspace(self.h_op, self.n_qubits, basis)
        return self._finalize(
            SqdResult(
                energy=e,
                angles=angles,
                nfev=int(self.config.n_shots),
                selected_bitstrings=basis,
                ci_coefficients=list(c),
                energy_trace=[e],
                meta={"method": "qsci", **sample_meta},
            )
        )


class SQD(_SqdFamilyBase):
    """Sample-based Quantum Diagonalization with S-CORE-lite + iterative expansion."""

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "sqd"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        rng = np.random.default_rng(self.config.seed if seed is None else seed)
        angles = default_hea_angles(self.n_qubits, self.config.hea_depth, rng)
        ne = self._n_electrons()
        occ = None
        pooled: list[int] = []
        energy_trace: list[float] = []
        best_e = float("inf")
        best_c: list[complex] = []
        best_basis: list[int] = []
        nfev = 0
        any_fallback_hf = False
        n_raw_total = 0
        for it in range(self.config.max_iters):
            psi = prepare_hea_sampling_state(
                self.n_qubits, angles, self.config.hea_depth, n_electrons=ne
            )
            samples = sample_bitstrings_from_state(psi, n_shots=self.config.n_shots, rng=rng)
            nfev += int(self.config.n_shots)
            n_raw_total += int(np.asarray(samples).size)
            recovered = recover_configurations(
                samples, n_qubits=self.n_qubits, n_electrons=ne, occupancy=occ
            )
            for _ in range(max(0, self.config.recovery_iters - 1)):
                recovered = recover_configurations(
                    recovered, n_qubits=self.n_qubits, n_electrons=ne, occupancy=occ
                )
            pooled.extend(int(x) for x in recovered)
            if best_basis and self.config.carryover > 0:
                order = np.argsort(np.abs(np.asarray(best_c)))[::-1]
                for j in order[: self.config.carryover]:
                    pooled.append(int(best_basis[int(j)]))
            basis, fallback_hf = ensure_nonempty_basis(
                top_k_unique(np.asarray(pooled, dtype=int), self.config.subspace_size),
                n_qubits=self.n_qubits,
                n_electrons=ne,
            )
            any_fallback_hf = any_fallback_hf or bool(fallback_hf)
            e, c, occ = diagonalize_subspace(self.h_op, self.n_qubits, basis)
            energy_trace.append(e)
            if e < best_e - self.config.energy_tol or it == 0:
                best_e, best_c, best_basis = e, list(c), list(basis)
            angles = angles + rng.normal(0.0, 0.05, size=angles.shape)
            if it >= 2 and abs(energy_trace[-1] - energy_trace[-2]) < self.config.energy_tol:
                break
        return self._finalize(
            SqdResult(
                energy=float(best_e),
                angles=angles,
                nfev=nfev,
                selected_bitstrings=best_basis,
                ci_coefficients=best_c,
                energy_trace=energy_trace,
                meta={
                    "method": "sqd",
                    "recovery": "s_core_lite",
                    "lucj_ansatz": False,
                    "batched_sci": False,
                    "parameter_update": "heuristic_gaussian",
                    "fallback_hf": any_fallback_hf,
                    "n_raw_samples": n_raw_total,
                },
            )
        )


class QSEQSCI(_SqdFamilyBase):
    """QSE+QSCI-lite: QSCI subspace spectrum / gaps (not full QSE transition operators).

    Epistemic bound: Ohgoe-style QSE+QSCI for quasiparticle bands needs excitation
    operators and QSE matrices; this reports eigengaps of the sampled CI subspace.
    """

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "qse_qsci_lite"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        base = QSCI(self.hamiltonian, self.config, executor=self._executor).build().run(seed=seed)
        h_sub = subspace_hamiltonian_matrix(self.h_op, self.n_qubits, base.selected_bitstrings)
        evals = np.sort(np.real(np.linalg.eigvalsh(h_sub)))
        gaps = [float(evals[i] - evals[0]) for i in range(1, min(4, len(evals)))]
        meta = dict(base.meta)
        meta.update(
            {
                "method": "qse_qsci_lite",
                "subspace_gaps": gaps,
                "qse_transition_operators": False,
            }
        )
        return self._finalize(
            SqdResult(
                energy=float(evals[0]),
                angles=base.angles,
                nfev=base.nfev,
                selected_bitstrings=base.selected_bitstrings,
                ci_coefficients=base.ci_coefficients,
                energy_trace=base.energy_trace,
                meta=meta,
            )
        )


class AdaptQSCI(_SqdFamilyBase):
    """ADAPT-QSCI: grow sampling state with pool rotations selected on classical CI."""

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "adapt_qsci"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        rng = np.random.default_rng(self.config.seed if seed is None else seed)
        ne = self._n_electrons()
        psi = hf_state(self.n_qubits, ne)
        pool = build_registered_operator_pool("fermionic_uccsd", self.hamiltonian)
        if not pool:
            pool = build_registered_operator_pool("toy_pair_xx", self.hamiltonian)
        energy_trace: list[float] = []
        basis: list[int] = []
        c: list[complex] = []
        nfev = 0
        selected_ops: list[int] = []
        selected_thetas: list[float] = []
        theta_grid = np.asarray([-0.5, -0.3, -0.15, -0.05, 0.05, 0.15, 0.3, 0.5], dtype=float)
        last_sample_meta: dict[str, object] = {}
        for _round in range(self.config.max_iters):
            samples = sample_bitstrings_from_state(psi, n_shots=self.config.n_shots, rng=rng)
            nfev += int(self.config.n_shots)
            basis, last_sample_meta = select_sampled_basis(
                samples,
                subspace_size=self.config.subspace_size,
                n_qubits=self.n_qubits,
                n_electrons=ne,
            )
            e, c_arr, _ = diagonalize_subspace(self.h_op, self.n_qubits, basis)
            c = list(c_arr)
            energy_trace.append(e)
            recon = np.zeros(2**self.n_qubits, dtype=np.complex128)
            for amp, idx in zip(c_arr, basis, strict=True):
                recon[int(idx)] = amp
            best_j = 0
            best_g = 0.0
            h_mat = qubit_operator_to_sparse(self.h_op, self.n_qubits)
            for j, pop in enumerate(pool[: min(16, len(pool))]):
                p_mat = qubit_operator_to_sparse(pop, self.n_qubits)
                gen = 0.5 * (p_mat - p_mat.conj().T)
                if float(np.linalg.norm(gen)) < 1e-14:
                    gen = 0.5 * (p_mat + p_mat.conj().T)
                comm = h_mat @ gen - gen @ h_mat
                g = float(np.imag(np.vdot(recon, comm @ recon)))
                if abs(g) > abs(best_g):
                    best_g, best_j = g, j
            selected_ops.append(best_j)
            p_mat = qubit_operator_to_sparse(pool[best_j], self.n_qubits)
            best_theta = 0.1 * float(np.sign(best_g) if best_g != 0.0 else 1.0)
            best_e_rot = float("inf")
            for th in theta_grid:
                u = _unitary_pool_rotation(p_mat, float(th))
                psi_try = u @ psi
                nrm = float(np.linalg.norm(psi_try))
                if nrm < STATE_NORMALIZATION_FLOOR:
                    continue
                psi_try = psi_try / nrm
                e_try = float(np.real(expectation_qubit_operator(psi_try, self.h_op, self.n_qubits)))
                if e_try < best_e_rot:
                    best_e_rot, best_theta = e_try, float(th)
            selected_thetas.append(best_theta)
            psi = _unitary_pool_rotation(p_mat, best_theta) @ psi
            psi = psi / max(float(np.linalg.norm(psi)), STATE_NORMALIZATION_FLOOR)
        return self._finalize(
            SqdResult(
                energy=float(energy_trace[-1] if energy_trace else 0.0),
                angles=np.asarray(selected_thetas, dtype=float),
                nfev=nfev,
                selected_bitstrings=basis,
                ci_coefficients=c,
                energy_trace=energy_trace,
                meta={
                    "method": "adapt_qsci",
                    "selected_pool_indices": selected_ops,
                    "selected_thetas": selected_thetas,
                    "pool_rotation": "unitary_antihermitian_or_hermitian",
                    **last_sample_meta,
                },
            )
        )


class SKQD(_SqdFamilyBase):
    """Sample-based Krylov Quantum Diagonalization (dense exact Krylov powers)."""

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "skqd"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        rng = np.random.default_rng(self.config.seed if seed is None else seed)
        ne = self._n_electrons()
        ref = hf_state(self.n_qubits, ne)
        states = krylov_states(
            ref,
            self.h_op,
            self.n_qubits,
            krylov_dim=self.config.krylov_dim,
            dt=self.config.krylov_dt,
        )
        pooled: list[int] = []
        nfev = 0
        for st in states:
            samples = sample_bitstrings_from_state(st, n_shots=self.config.n_shots, rng=rng)
            nfev += int(self.config.n_shots)
            pooled.extend(int(x) for x in samples)
        basis, sample_meta = select_sampled_basis(
            np.asarray(pooled, dtype=int),
            subspace_size=self.config.subspace_size,
            n_qubits=self.n_qubits,
            n_electrons=ne,
        )
        e, c, _ = diagonalize_subspace(self.h_op, self.n_qubits, basis)
        return self._finalize(
            SqdResult(
                energy=e,
                angles=np.zeros(2 * self.n_qubits * self.config.hea_depth, dtype=float),
                nfev=nfev,
                selected_bitstrings=basis,
                ci_coefficients=list(c),
                energy_trace=[e],
                meta={
                    "method": "skqd",
                    "krylov_dim": self.config.krylov_dim,
                    "dt": self.config.krylov_dt,
                    "evolution": "dense_expm",
                    **sample_meta,
                },
            )
        )


class SqDRIFT(_SqdFamilyBase):
    """SKQD with qDRIFT randomized Hamiltonian simulation (dense lite)."""

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "sqdrift"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        rng = np.random.default_rng(self.config.seed if seed is None else seed)
        ne = self._n_electrons()
        ref = hf_state(self.n_qubits, ne)
        pooled: list[int] = []
        nfev = 0
        for k in range(self.config.krylov_dim):
            t = float(k) * float(self.config.krylov_dt)
            for _ in range(self.config.qdrift_replicas):
                if k == 0:
                    st = ref
                else:
                    st = qdrift_channel_state(
                        ref,
                        self.h_op,
                        self.n_qubits,
                        time=t,
                        n_steps=self.config.qdrift_steps,
                        rng=rng,
                    )
                samples = sample_bitstrings_from_state(st, n_shots=self.config.n_shots, rng=rng)
                nfev += int(self.config.n_shots)
                pooled.extend(int(x) for x in samples)
        basis, sample_meta = select_sampled_basis(
            np.asarray(pooled, dtype=int),
            subspace_size=self.config.subspace_size,
            n_qubits=self.n_qubits,
            n_electrons=ne,
        )
        e, c, _ = diagonalize_subspace(self.h_op, self.n_qubits, basis)
        return self._finalize(
            SqdResult(
                energy=e,
                angles=np.zeros(2 * self.n_qubits * self.config.hea_depth, dtype=float),
                nfev=nfev,
                selected_bitstrings=basis,
                ci_coefficients=list(c),
                energy_trace=[e],
                meta={
                    "method": "sqdrift",
                    "qdrift_steps": self.config.qdrift_steps,
                    "qdrift_replicas": self.config.qdrift_replicas,
                    **sample_meta,
                },
            )
        )


class HIVQE(_SqdFamilyBase):
    """HI-VQE-lite: dual subspace energies + Ne-preserving classical singles.

    Epistemic bound: not full Qunova/IBM handover (no LUCJ / Ext-CI by H-coupling
    ranking / variational update from round-only energy). Angle refresh is a
    heuristic Gaussian step keyed by round vs cumulative energy.
    """

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "hi_vqe_lite"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        rng = np.random.default_rng(self.config.seed if seed is None else seed)
        angles = default_hea_angles(self.n_qubits, self.config.hea_depth, rng)
        ne = self._n_electrons()
        cumulative: list[int] = []
        energy_trace: list[float] = []
        best_e = float("inf")
        best_basis: list[int] = []
        best_c: list[complex] = []
        occ = None
        nfev = 0
        for it in range(self.config.max_iters):
            psi = prepare_hea_sampling_state(
                self.n_qubits, angles, self.config.hea_depth, n_electrons=ne
            )
            samples = sample_bitstrings_from_state(psi, n_shots=self.config.n_shots, rng=rng)
            nfev += int(self.config.n_shots)
            recovered = recover_configurations(
                samples, n_qubits=self.n_qubits, n_electrons=ne, occupancy=occ
            )
            round_basis, _fallback_hf = ensure_nonempty_basis(
                top_k_unique(recovered, self.config.subspace_size),
                n_qubits=self.n_qubits,
                n_electrons=ne,

            )
            expanded = list(round_basis)
            for seed_bs in round_basis[: min(3, len(round_basis))]:
                expanded.extend(particle_number_preserving_singles(int(seed_bs), self.n_qubits))
            if ne is not None:
                expanded = [b for b in expanded if popcount(b) == ne]
            round_basis, _fallback_hf = ensure_nonempty_basis(
                top_k_unique(np.asarray(expanded, dtype=int), self.config.subspace_size),
                n_qubits=self.n_qubits,
                n_electrons=ne,

            )
            e_round, _, occ_round = diagonalize_subspace(
                self.h_op, self.n_qubits, round_basis
            )
            occ = occ_round
            cumulative.extend(round_basis)
            cum_basis, _fallback_hf = ensure_nonempty_basis(
                top_k_unique(np.asarray(cumulative, dtype=int), self.config.subspace_size * 2),
                n_qubits=self.n_qubits,
                n_electrons=ne,

            )
            e_cum, c_cum, _ = diagonalize_subspace(self.h_op, self.n_qubits, cum_basis)
            energy_trace.append(float(e_cum))
            if e_cum < best_e:
                best_e, best_basis, best_c = float(e_cum), list(cum_basis), list(c_cum)
            # Heuristic param refresh keyed by round-only vs cumulative (handover-lite)
            step = 0.08 if e_round > e_cum else 0.03
            angles = angles + rng.normal(0.0, step, size=angles.shape)
            if it >= 2 and abs(energy_trace[-1] - energy_trace[-2]) < self.config.energy_tol:
                break
        return self._finalize(
            SqdResult(
                energy=float(best_e),
                angles=angles,
                nfev=nfev,
                selected_bitstrings=best_basis,
                ci_coefficients=best_c,
                energy_trace=energy_trace,
                meta={
                    "method": "hi_vqe_lite",
                    "handover": "gaussian_step_heuristic",
                    "ext_ci": "ne_preserving_singles",
                },
            )
        )


class EWFTrimSQD(_SqdFamilyBase):
    """EWF-TrimSQD-lite: fragment-local Ne-preserving expansion then global diag.

    Epistemic bound: no MP2 bath / η-trim / per-fragment FCI / embedding reassembly.
    """

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "ewf_trim_sqd_lite"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        rng = np.random.default_rng(self.config.seed if seed is None else seed)
        ne = self._n_electrons()
        ranges = fragment_qubit_ranges(self.n_qubits, self.config.n_fragments)
        angles = default_hea_angles(self.n_qubits, self.config.hea_depth, rng)
        psi = prepare_hea_sampling_state(
            self.n_qubits, angles, self.config.hea_depth, n_electrons=ne
        )
        samples = sample_bitstrings_from_state(psi, n_shots=self.config.n_shots, rng=rng)
        samples = recover_configurations(
            samples, n_qubits=self.n_qubits, n_electrons=ne
        )
        hf = hf_bitstring(self.n_qubits, ne)
        pooled: list[int] = []
        for lo, hi in ranges:
            local_pool = [int(x) for x in samples]
            # Prefer configs that only differ from HF inside this fragment
            for b in samples:
                bb = int(b)
                outside_ok = True
                for q in list(range(0, lo)) + list(range(hi, self.n_qubits)):
                    bit_b = (bb >> (self.n_qubits - 1 - q)) & 1
                    bit_h = (hf >> (self.n_qubits - 1 - q)) & 1
                    if bit_b != bit_h:
                        outside_ok = False
                        break
                if outside_ok:
                    local_pool.append(bb)
            # Fragment-local singles from HF (only i,a in [lo,hi))
            occ = [q for q in range(lo, hi) if (hf >> (self.n_qubits - 1 - q)) & 1]
            virt = [q for q in range(lo, hi) if not ((hf >> (self.n_qubits - 1 - q)) & 1)]
            for i in occ:
                for a in virt:
                    local_pool.append(hf ^ (1 << (self.n_qubits - 1 - i)) ^ (1 << (self.n_qubits - 1 - a)))
            if ne is not None:
                local_pool = [b for b in local_pool if popcount(b) == ne]
            pooled.extend(
                top_k_unique(np.asarray(local_pool, dtype=int), max(2, self.config.subspace_size // max(1, len(ranges))))
            )
        basis, _fallback_hf = ensure_nonempty_basis(
            top_k_unique(np.asarray(pooled, dtype=int), self.config.subspace_size),
            n_qubits=self.n_qubits,
            n_electrons=ne,

        )
        e, c, _ = diagonalize_subspace(self.h_op, self.n_qubits, basis)
        return self._finalize(
            SqdResult(
                energy=e,
                angles=angles,
                nfev=int(self.config.n_shots),
                selected_bitstrings=basis,
                ci_coefficients=list(c),
                energy_trace=[e],
                meta={
                    "method": "ewf_trim_sqd_lite",
                    "n_fragments": len(ranges),
                    "fragment_ranges": ranges,
                    "mp2_bath": False,
                    "eta_trim": False,
                },
            )
        )


class QBESQD(_SqdFamilyBase):
    """QBE-SQD-lite: overlapping fragments + iterative occupancy matching.

    Epistemic bound: no Schmidt bath / BE potential / true bootstrap embedding.
    """

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "qbe_sqd_lite"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        rng = np.random.default_rng(self.config.seed if seed is None else seed)
        ne = self._n_electrons()
        ranges = overlapping_fragment_ranges(self.n_qubits, self.config.n_fragments)
        angles = default_hea_angles(self.n_qubits, self.config.hea_depth, rng)
        occ = None
        energy_trace: list[float] = []
        best_e = float("inf")
        best_basis: list[int] = []
        best_c: list[complex] = []
        nfev = 0
        for _it in range(max(2, self.config.max_iters)):
            psi = prepare_hea_sampling_state(
                self.n_qubits, angles, self.config.hea_depth, n_electrons=ne
            )
            samples = sample_bitstrings_from_state(psi, n_shots=self.config.n_shots, rng=rng)
            nfev += int(self.config.n_shots)
            pooled: list[int] = []
            for lo, hi in ranges:
                frag_samples = np.asarray(samples, dtype=int)
                recovered = recover_configurations(
                    frag_samples, n_qubits=self.n_qubits, n_electrons=ne, occupancy=occ
                )
                local = [int(x) for x in recovered]
                # Expand with Ne-preserving singles that touch the fragment
                for seed_bs in top_k_unique(recovered, min(3, self.config.subspace_size)):
                    for exc in particle_number_preserving_singles(int(seed_bs), self.n_qubits):
                        # keep if excitation involves at least one fragment qubit
                        diff = int(seed_bs) ^ int(exc)
                        touches = False
                        for q in range(lo, hi):
                            if (diff >> (self.n_qubits - 1 - q)) & 1:
                                touches = True
                                break
                        if touches:
                            local.append(int(exc))
                if ne is not None:
                    local = [b for b in local if popcount(b) == ne]
                pooled.extend(
                    top_k_unique(
                        np.asarray(local, dtype=int),
                        max(2, self.config.subspace_size // max(1, len(ranges))),
                    )
                )
            basis, _fallback_hf = ensure_nonempty_basis(
                top_k_unique(np.asarray(pooled, dtype=int), self.config.subspace_size),
                n_qubits=self.n_qubits,
                n_electrons=ne,

            )
            e, c, occ = diagonalize_subspace(self.h_op, self.n_qubits, basis)
            energy_trace.append(e)
            if e < best_e:
                best_e, best_basis, best_c = e, list(basis), list(c)
            angles = angles + rng.normal(0.0, 0.04, size=angles.shape)
        return self._finalize(
            SqdResult(
                energy=float(best_e),
                angles=angles,
                nfev=nfev,
                selected_bitstrings=best_basis,
                ci_coefficients=best_c,
                energy_trace=energy_trace,
                meta={
                    "method": "qbe_sqd_lite",
                    "embedding": "occupancy_match_overlapping_fragments",
                    "fragment_ranges": ranges,
                    "schmidt_bath": False,
                    "be_potential": False,
                },
            )
        )


class SQDAFQMC(_SqdFamilyBase):
    """SQD + ph-AFQMC-lite: refine SQD trial with subspace walker local energies.

    Epistemic bound: not production ph-AFQMC (no auxiliary-field / phaseless AF
    dynamics). Walkers live in the selected CI subspace only.
    """

    def __init__(self, hamiltonian: QubitHamiltonian, config: SqdConfig | None = None, **kw: Any):
        super().__init__(hamiltonian, config, **kw)
        self._algorithm_name = "sqd_afqmc_lite"

    def run(self, *, seed: int | None = None) -> SqdResult:
        self._ensure_built()
        sqd = SQD(self.hamiltonian, self.config, executor=self._executor).build().run(seed=seed)
        basis = sqd.selected_bitstrings
        if len(basis) < 2:
            meta = dict(sqd.meta)
            meta.update({"method": "sqd_afqmc_lite", "afqmc_lite": True, "skipped": "tiny_subspace"})
            return self._finalize(
                SqdResult(
                    energy=sqd.energy,
                    angles=sqd.angles,
                    nfev=sqd.nfev,
                    selected_bitstrings=basis,
                    ci_coefficients=sqd.ci_coefficients,
                    energy_trace=sqd.energy_trace,
                    meta=meta,
                )
            )
        h_sub = np.asarray(
            subspace_hamiltonian_matrix(self.h_op, self.n_qubits, basis),
            dtype=np.complex128,
        )
        trial = np.asarray(sqd.ci_coefficients, dtype=np.complex128)
        trial = trial / max(float(np.linalg.norm(trial)), 1e-15)
        walkers = np.tile(np.abs(trial) ** 2, (self.config.afqmc_walkers, 1))
        walkers = walkers / walkers.sum(axis=1, keepdims=True)
        energies: list[float] = []
        for _ in range(self.config.afqmc_steps):
            local = []
            for w in walkers:
                amp = np.sqrt(np.maximum(w, 0.0)) * np.exp(1j * np.angle(trial))
                denom = complex(np.vdot(trial, amp))
                if abs(denom) < 1e-12:
                    continue
                num = complex(np.vdot(trial, h_sub @ amp))
                el = float(np.real(num / denom))
                local.append(el)
                w[:] = 0.85 * w + 0.15 * (np.abs(trial) ** 2)
                w[:] = w / w.sum()
            if local:
                energies.append(float(np.mean(local)))
        e_af = float(energies[-1]) if energies else float(sqd.energy)
        meta = dict(sqd.meta)
        meta.update(
            {
                "method": "sqd_afqmc_lite",
                "sqd_energy": float(sqd.energy),
                "afqmc_lite": True,
                "phaseless_afqmc": False,
                "afqmc_trace": energies,
            }
        )
        return self._finalize(
            SqdResult(
                energy=e_af,
                angles=sqd.angles,
                nfev=sqd.nfev + self.config.afqmc_walkers * self.config.afqmc_steps,
                selected_bitstrings=basis,
                ci_coefficients=sqd.ci_coefficients,
                energy_trace=list(sqd.energy_trace) + energies,
                meta=meta,
            )
        )


VARIANT_TO_CLASS: dict[str, type[_SqdFamilyBase]] = {
    "cbs": CBS,
    "qsci": QSCI,
    "sqd": SQD,
    "qse_qsci_lite": QSEQSCI,
    "adapt_qsci": AdaptQSCI,
    "skqd": SKQD,
    "sqdrift": SqDRIFT,
    "hi_vqe_lite": HIVQE,
    "ewf_trim_sqd_lite": EWFTrimSQD,
    "qbe_sqd_lite": QBESQD,
    "sqd_afqmc_lite": SQDAFQMC,
}


def sqd_algorithm_report_v1(result: SqdResult, *, algorithm: str) -> dict[str, Any]:
    meta = dict(result.meta)
    return {
        "schema": ALGORITHM_SQD_REPORT_V1,
        "algorithm": algorithm,
        "final_value": float(result.energy),
        "nfev": int(result.nfev),
        "n_shots_total": int(meta.get("n_shots_total", result.nfev)),
        "selected_bitstrings": list(result.selected_bitstrings),
        "energy_trace": list(result.energy_trace),
        "final_parameters": result.angles.tolist(),
        "dense_prototype": bool(meta.get("dense_prototype", True)),
        "execution_mode": str(meta.get("execution_mode", "dense_statevector")),
        "backend_executor_used": bool(meta.get("backend_executor_used", False)),
        "literature_parity": bool(meta.get("literature_parity", False)),
        "customer_tier": str(meta.get("customer_tier", sqd_customer_tier(algorithm))),
        "fallback_hf": bool(meta.get("fallback_hf", False)),
        "postselect_kept_fraction": meta.get("postselect_kept_fraction"),
        "max_qubits_supported": int(meta.get("max_qubits_supported", MAX_SQD_QUBITS)),
        "meta": meta,
    }
