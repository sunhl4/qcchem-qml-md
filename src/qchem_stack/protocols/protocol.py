from __future__ import annotations

import hashlib
import math
import pickle
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, cast

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.compile_passes import apply_pass_bundle
from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.backends.pauli_grouping import PauliMeasurementPlan, build_measurement_plan
from qchem_stack.backends.pauli_measure_expand import (
    build_synthesized_pauli_shot_circuit,
    deserialize_basis_key,
    hea_operations,
)
from qchem_stack.backends.shot_budget import (
    energy_estimate_with_uncertainty,
    recommended_shots_per_circuit,
)
from qchem_stack.backends.spec import (
    BackendSpec,
    CircuitIR,
    CompilerPassBundle,
    circuit_resource_row,
)
from qchem_stack.config import NexusAnalogSpec
from qchem_stack.jobs.nexus_analog import nexus_analog_billing_for_job_result
from qchem_stack.jobs.store import JobHandle, SqliteJobStore
from qchem_stack.mitigation.pmsv import PMSVConfig, filter_shots_pmsv, finalize_pmsv_report
from qchem_stack.mitigation.zne import zne_scale_energy
from qchem_stack.protocols.pauli_support import hamiltonian_pauli_term_records
from qchem_stack.quantum.statevector import hea_state


def _hea_angles_for_depth(
    angles: np.ndarray, *, n_qubits: int, base_depth: int, eff_depth: int
) -> np.ndarray:
    """Pad or truncate variational angles for ``hea_state`` when ZNE uses a larger effective HEA depth."""
    n_base = int(2 * n_qubits * base_depth)
    n_eff = int(2 * n_qubits * eff_depth)
    a = np.asarray(angles, dtype=float).reshape(-1)
    if a.size == n_eff:
        return a
    if a.size != n_base:
        raise ValueError(
            f"HEA angles length mismatch: got {a.size}, expected {n_base} for depth={base_depth} "
            f"or {n_eff} for effective depth={eff_depth}"
        )
    if eff_depth <= base_depth:
        return a[:n_eff]
    return np.concatenate([a, np.zeros(n_eff - n_base, dtype=float)])


# Pauli ``run``/``evaluate`` expectation paths (P0): exact executor vs grouped statevector MC vs Qiskit
# ``get_counts`` — see ``docs/技术文档_设备比特串与Qiskit采样路径.md`` §2 and
# ``protocols.inquanto_contract.protocol_expectation_semantics_public``.


class ProtocolPhase(str, Enum):
    INSTANTIATE = "instantiate"
    BUILD = "build"
    COMPILE = "compile"
    RUN = "run"
    EVALUATE = "evaluate"


@dataclass
class PauliAveragingProtocol:
    """Five-stage protocol with **commuting Pauli groups** (fewer measurement circuits) and shot stderr bounds.

    **Evaluate / expectation (P0)**: when Pauli averaging runs, ``protocol_counts`` records
    ``expectation_source`` and ``energy_stderr_model`` — either the default exact executor path,
    ``run_sampled`` statevector grouped MC, or ``run_qiskit_shots`` device/Aer histograms
    (mutually exclusive shot modes; see module comment above).
    """

    hamiltonian: QubitOperator
    n_qubits: int
    backend: BackendSpec
    pass_bundle: CompilerPassBundle = field(default_factory=CompilerPassBundle)
    pmsv: PMSVConfig | None = None
    zne_scales: list[float] | None = None
    zne_mode: Literal["scalar_stub", "circuit_scale_fold"] = "scalar_stub"
    hea_depth: int = 1
    angles: np.ndarray = field(default_factory=lambda: np.zeros(1, dtype=float))
    measurement_grouping: Literal["tensor_product", "greedy_commuting"] = "tensor_product"
    run_sampled: bool = False
    """If True, energy is a Monte Carlo estimate from grouped Pauli readouts (statevector sampling)."""
    run_qiskit_shots: bool = False
    """If True, use Qiskit ``get_counts`` (Aer or hardware) per group; see :mod:`qchem_stack.backends.qiskit_pauli_shots`."""
    record_histograms: bool = False
    """With ``run_sampled`` or ``run_qiskit_shots``, attach ``measurement_histogram_rows`` (histogram schema below)."""
    executor: HamiltonianExpectationExecutor | None = None
    nexus_analog: NexusAnalogSpec | None = None
    """If set, async :meth:`process_job` HQC row uses these weights; else cost defaults (see :mod:`qchem_stack.jobs.nexus_analog`)."""
    pauli_support_max_terms: int | None = None
    """Cap exported Pauli list / records in ``protocol_counts`` (full count in ``n_hamiltonian_pauli_terms_full`` when truncated)."""
    _phase: ProtocolPhase = field(default=ProtocolPhase.INSTANTIATE, init=False)
    _measurement_plan: PauliMeasurementPlan | None = field(default=None, init=False)
    _logical_circuits: list[CircuitIR] = field(default_factory=list, init=False)
    _compiled: list[CircuitIR] = field(default_factory=list, init=False)
    _counts: dict[str, Any] = field(default_factory=dict, init=False)

    def __getstate__(self) -> dict[str, Any]:
        d = self.__dict__.copy()
        d.pop("executor", None)
        return d

    def __setstate__(self, state: dict[str, Any]) -> None:
        self.__dict__.update(state)
        self.executor = None

    def instantiate(self) -> None:
        self._phase = ProtocolPhase.INSTANTIATE

    def build(self, angles: np.ndarray, hea_depth: int = 1) -> None:
        """Build one circuit per measurement group: HEA + single-qubit basis change + measure when synthesizable."""
        self._phase = ProtocolPhase.BUILD
        self.angles = np.asarray(angles, dtype=float)
        self.hea_depth = hea_depth
        self._measurement_plan = build_measurement_plan(
            self.hamiltonian, self.n_qubits, grouping=self.measurement_grouping
        )
        circuits: list[CircuitIR] = []
        for meta in self._measurement_plan.to_circuit_metas():
            n_terms = int(meta.get("n_terms", 0))
            qs = list(meta.get("support_qubits", []))
            bk = deserialize_basis_key(meta.get("basis_key"))
            if n_terms == 0:
                circuits.append(
                    CircuitIR(
                        n_qubits=self.n_qubits,
                        operations=hea_operations(self.n_qubits, hea_depth, self.angles),
                        boxes=["HEA"],
                    )
                )
            elif bk is not None:
                circuits.append(
                    build_synthesized_pauli_shot_circuit(
                        self.n_qubits,
                        hea_depth,
                        self.angles,
                        basis_key=bk,
                        support_qubits=qs,
                    )
                )
            else:
                ops = hea_operations(self.n_qubits, hea_depth, self.angles)
                ops.append({"name": "JOINT_PAULI_MEASURE", "qubits": qs, "params": dict(meta)})
                circuits.append(
                    CircuitIR(
                        n_qubits=self.n_qubits, operations=ops, boxes=["HEA", "JointPauliMeasure"]
                    )
                )
        self._logical_circuits = circuits

    def compile(self) -> None:
        self._phase = ProtocolPhase.COMPILE
        pre = self.pass_bundle.preoptimize_passes + self.pass_bundle.compiler_passes
        self._compiled = [apply_pass_bundle(c, pre) for c in self._logical_circuits]

    def run(
        self,
        noise_rng: np.random.Generator | None = None,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        """Evaluate energy; stderr is either a conservative bound or shot-simulation stderr."""
        self._phase = ProtocolPhase.RUN
        noise_rng = noise_rng or np.random.default_rng(0)
        exe = executor or self.executor or executor_from_spec(self.backend)
        plan = self._measurement_plan or build_measurement_plan(
            self.hamiltonian, self.n_qubits, grouping=self.measurement_grouping
        )
        self._measurement_plan = plan
        terms_dict = dict(self.hamiltonian.terms)
        tgt = self.backend.target_energy_stderr
        shots = int(self.backend.shots_per_circuit)
        if tgt is not None and float(tgt) > 0:
            shots = recommended_shots_per_circuit(plan, terms_dict, float(tgt))
        n_groups = len(plan.groups)
        pmsv_stderr_scale = 1.0
        if self.pmsv is not None and 0.0 < float(self.pmsv.retention_rate) < 1.0:
            pmsv_stderr_scale = 1.0 / math.sqrt(float(self.pmsv.retention_rate))

        if self.run_sampled and self.run_qiskit_shots:
            raise ValueError(
                "run_sampled and run_qiskit_shots are mutually exclusive in PauliAveragingProtocol"
            )
        if self.run_sampled:
            from qchem_stack.backends.pauli_shot_sim import energy_estimate_grouped_shot_simulation

            psi = hea_state(self.angles, self.n_qubits, self.hea_depth)
            e_sim, se_sim, sim_meta = energy_estimate_grouped_shot_simulation(
                psi,
                self.hamiltonian,
                plan,
                self.n_qubits,
                shots,
                noise_rng,
                return_histograms=self.record_histograms,
            )
            stderr = float(se_sim) * pmsv_stderr_scale
            self._counts = {
                "expectation": float(e_sim),
                "expectation_source": "grouped_shot_simulation_statevector",
                "energy_stderr_model": "sample_stderr_independent_groups_approx",
                "raw_shots": self.backend.shots_per_circuit,
                "shots_per_circuit_effective": shots,
                "energy_stderr": stderr,
                "n_measurement_circuits": plan.n_circuits,
                "total_shots_budget": int(
                    sim_meta.get("total_shots_used", shots * max(1, n_groups))
                ),
                "n_pauli_terms": len(terms_dict),
                "n_pauli_groups": n_groups,
                "pmsv_stderr_scale": pmsv_stderr_scale,
                "shot_sim_meta": sim_meta,
            }
            if self.record_histograms and "measurement_histogram_rows" in sim_meta:
                self._counts["measurement_histogram_rows"] = sim_meta["measurement_histogram_rows"]
        elif self.run_qiskit_shots:
            from qchem_stack.backends.qiskit_pauli_shots import energy_estimate_grouped_qiskit_shots

            e_q, se_q, q_meta = energy_estimate_grouped_qiskit_shots(
                self.hamiltonian,
                plan,
                self.n_qubits,
                self.hea_depth,
                self.angles,
                shots,
                self.backend,
                noise_rng,
                return_histograms=self.record_histograms,
            )
            stderr = float(se_q) * pmsv_stderr_scale
            self._counts = {
                "expectation": float(e_q),
                "expectation_source": "qiskit_shot_counts_get_counts",
                "energy_stderr_model": "empirical_shot_variance_independent_groups_approx",
                "raw_shots": self.backend.shots_per_circuit,
                "shots_per_circuit_effective": shots,
                "energy_stderr": stderr,
                "n_measurement_circuits": plan.n_circuits,
                "total_shots_budget": int(q_meta.get("total_shots_used", shots * max(1, n_groups))),
                "n_pauli_terms": len(terms_dict),
                "n_pauli_groups": n_groups,
                "pmsv_stderr_scale": pmsv_stderr_scale,
                "qiskit_pauli_shot_meta": q_meta,
            }
            if self.record_histograms and "measurement_histogram_rows" in q_meta:
                self._counts["measurement_histogram_rows"] = q_meta["measurement_histogram_rows"]
        else:
            e = exe.expectation_hea(
                self.hamiltonian,
                self.n_qubits,
                _hea_angles_for_depth(
                    self.angles,
                    n_qubits=self.n_qubits,
                    base_depth=int(self.hea_depth),
                    eff_depth=int(self.hea_depth),
                ),
                self.hea_depth,
            )
            est = energy_estimate_with_uncertainty(e, plan, terms_dict, shots)
            stderr = float(est.stderr) * pmsv_stderr_scale
            self._counts = {
                "expectation": e,
                "expectation_source": "executor_exact_or_device_mean",
                "energy_stderr_model": "conservative_sum_bound_equal_shots",
                "raw_shots": self.backend.shots_per_circuit,
                "shots_per_circuit_effective": shots,
                "energy_stderr": stderr,
                "n_measurement_circuits": est.n_circuits,
                "total_shots_budget": est.total_shots,
                "n_pauli_terms": len(terms_dict),
                "n_pauli_groups": n_groups,
                "pmsv_stderr_scale": pmsv_stderr_scale,
            }

        records = hamiltonian_pauli_term_records(self.hamiltonian)
        n_full = len(records)
        ps = [r["pauli_string"] for r in records]
        truncated = False
        cap = self.pauli_support_max_terms
        if cap is not None and cap >= 0 and n_full > cap:
            truncated = True
            records = records[:cap]
            ps = ps[:cap]
        self._counts["hamiltonian_pauli_term_records"] = records
        self._counts["hamiltonian_pauli_strings"] = ps
        self._counts["n_hamiltonian_pauli_terms"] = len(ps)
        self._counts["pauli_support_truncated"] = truncated
        if truncated:
            self._counts["n_hamiltonian_pauli_terms_full"] = n_full
        metas_post = plan.to_circuit_metas()
        self._counts["pauli_group_ids"] = [int(m.get("group_id", 0)) for m in metas_post]

        e_val = float(self._counts["expectation"])
        if self.pmsv and (self.pmsv.stabilizers or 0.0 < float(self.pmsv.retention_rate) < 1.0):
            raw_shots = shots
            kept = filter_shots_pmsv(raw_shots, self.pmsv.retention_rate, noise_rng)
            self._counts["kept_shots"] = kept
        if self.zne_scales:
            scales_f = [float(s) for s in self.zne_scales]
            fold_requested = self.zne_mode == "circuit_scale_fold"
            unsupported_fold = fold_requested and (self.run_sampled or self.run_qiskit_shots)
            if fold_requested and not unsupported_fold:
                base_depth = int(self.hea_depth)
                curve: list[float] = []
                for s in scales_f:
                    eff_depth = max(1, base_depth + int(max(0.0, round(s - 1.0))))
                    ang = _hea_angles_for_depth(
                        self.angles,
                        n_qubits=self.n_qubits,
                        base_depth=base_depth,
                        eff_depth=eff_depth,
                    )
                    curve.append(
                        float(
                            exe.expectation_hea(
                                self.hamiltonian,
                                self.n_qubits,
                                ang,
                                eff_depth,
                            )
                        )
                    )
                self._counts["zne_curve"] = curve
                self._counts["zne_energies"] = curve
                self._counts["zne_mode"] = "circuit_scale_fold"
                arr_s = np.asarray(scales_f, dtype=float)
                arr_e = np.asarray(curve, dtype=float)
                if arr_e.size >= 2:
                    coef = np.polyfit(arr_s, arr_e, 1)
                    self._counts["zne_extrapolated_energy"] = float(np.polyval(coef, 1.0))
                else:
                    self._counts["zne_extrapolated_energy"] = float(curve[0])
                base_budget = int(self._counts.get("total_shots_budget", shots * max(1, n_groups)))
                shot_mult = sum(max(1, int(round(s))) for s in scales_f)
                self._counts["total_shots_budget"] = base_budget * shot_mult
            else:
                scaled = [zne_scale_energy(e_val, s) for s in scales_f]
                self._counts["zne_energies"] = scaled
                self._counts["zne_mode"] = "scalar_stub"
                if unsupported_fold:
                    self._counts["zne_circuit_fold_fallback_reason"] = (
                        "circuit_scale_fold requires exact executor path (disable run_sampled / run_qiskit_shots)"
                    )
        if self.pmsv is not None:
            rr = float(self.pmsv.retention_rate)
            discard = max(0.0, min(1.0, 1.0 - rr))
            pr = {
                "stabilizers": list(self.pmsv.stabilizers),
                "stabilizer_count": len(self.pmsv.stabilizers),
                "retention_rate": rr,
                "discard_fraction": discard,
                "effective_kept_shots_fraction": rr,
                "stderr_inflation_from_postselection": float(
                    self._counts.get("pmsv_stderr_scale", 1.0)
                ),
                "pmsv_stderr_scale": float(self._counts.get("pmsv_stderr_scale", 1.0)),
                "kept_shots_simulated": self._counts.get("kept_shots"),
            }
            self._counts["pmsv_report"] = finalize_pmsv_report(pr, self.pmsv)

    def evaluate(self) -> float:
        self._phase = ProtocolPhase.EVALUATE
        return float(self._counts.get("expectation", 0.0))

    def dataframe_circuit_shot_rows(self) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        plan = self._measurement_plan or build_measurement_plan(
            self.hamiltonian, self.n_qubits, grouping=self.measurement_grouping
        )
        metas = plan.to_circuit_metas()
        eff = int(self._counts.get("shots_per_circuit_effective", self.backend.shots_per_circuit))
        zne_scales = self.zne_scales or []
        if self._counts.get("zne_mode") == "circuit_scale_fold" and zne_scales:
            for si, sf in enumerate(float(s) for s in zne_scales):
                shot_m = max(1, int(round(sf)))
                for i, c in enumerate(self._compiled):
                    extra: dict[str, Any] = {"zne_scale": sf, "zne_scale_index": si}
                    if i < len(metas):
                        extra["pauli_group_id"] = metas[i].get("group_id")
                        extra["n_pauli_terms"] = metas[i].get("n_terms")
                        extra["synthesized"] = metas[i].get("synthesized")
                    rows.append(
                        circuit_resource_row(
                            f"zne{si}_circ_{i}",
                            c,
                            shots=eff * shot_m,
                            backend=self.backend,
                            extra=extra,
                        )
                    )
            return rows
        for i, c in enumerate(self._compiled):
            extra = {}
            if i < len(metas):
                extra["pauli_group_id"] = metas[i].get("group_id")
                extra["n_pauli_terms"] = metas[i].get("n_terms")
                extra["synthesized"] = metas[i].get("synthesized")
            rows.append(
                circuit_resource_row(
                    f"circ_{i}",
                    c,
                    shots=eff,
                    backend=self.backend,
                    extra=cast(dict[str, Any] | None, extra or None),
                )
            )
        return rows

    def launch(self, store: SqliteJobStore) -> JobHandle:
        blob = pickle.dumps(self)
        jid = str(uuid.uuid4())
        ph = hashlib.sha256(blob).hexdigest()[:32]
        return store.enqueue(jid, blob, protocol_hash=ph)

    @staticmethod
    def process_job(store: SqliteJobStore, job_id: str) -> None:
        import sqlite3

        con = sqlite3.connect(store.path)
        row = con.execute("SELECT payload FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        con.close()
        if row is None:
            raise KeyError(job_id)
        proto: PauliAveragingProtocol = pickle.loads(row[0])
        proto.compile()
        proto.run()
        val = proto.evaluate()
        rows = proto.dataframe_circuit_shot_rows()
        stderr = proto._counts.get("energy_stderr")
        res: dict[str, Any] = {
            "expectation": val,
            "rows": rows,
            "energy_stderr": stderr,
            "total_shots_budget": proto._counts.get("total_shots_budget"),
            "n_measurement_circuits": proto._counts.get("n_measurement_circuits"),
            "shots_per_circuit_effective": proto._counts.get("shots_per_circuit_effective"),
            "nexus_analog_billing": nexus_analog_billing_for_job_result(rows, proto.nexus_analog),
        }
        store.complete(job_id, res)

    def retrieve(self, store: SqliteJobStore, handle: JobHandle) -> dict[str, Any]:
        """Fetch job result dict; same keys as :meth:`SqliteJobStore.result`.

        This is the local analogue of Nexus **retrieve** (async pull). When the job is
        still ``QUEUED``/``RUNNING``/``FAILED``, the return value includes ``status`` (and
        ``error`` if failed) and does **not** fabricate ``expectation``—callers must check
        ``status == "DONE"`` before using energy fields (see ``docs/launch_retrieve_nexus_analog.md``).
        """
        return store.result(handle.job_id)

    def dumps(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def loads(data: bytes) -> PauliAveragingProtocol:
        return pickle.loads(data)
