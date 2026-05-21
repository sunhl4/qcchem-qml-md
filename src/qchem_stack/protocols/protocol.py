from __future__ import annotations

import hashlib
import pickle
import uuid
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, cast

import numpy as np

from qchem_stack.backends.spec import BackendSpec, CircuitIR, CompilerPassBundle
from qchem_stack.protocols.protocol_build import build_logical_circuits, compile_circuits
from qchem_stack.protocols.protocol_job import (
    dataframe_circuit_shot_rows,
    process_pauli_protocol_job,
)
from qchem_stack.protocols.protocol_phase import ProtocolPhase
from qchem_stack.protocols.protocol_run import run_energy_estimation

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.executor_base import HamiltonianExpectationExecutor
    from qchem_stack.backends.pauli_grouping import PauliMeasurementPlan
    from qchem_stack.config import NexusAnalogSpec
    from qchem_stack.jobs.store import JobHandle, SqliteJobStore
    from qchem_stack.mitigation.pmsv import PMSVConfig

# Pauli ``run``/``evaluate`` expectation paths (P0): exact executor vs grouped statevector MC vs Qiskit
# ``get_counts`` — see ``docs/技术文档_设备比特串与Qiskit采样路径.md`` §2 and
# ``protocols.product_contract.protocol_expectation_semantics_public``.


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
    run_qiskit_shots: bool = False
    record_histograms: bool = False
    executor: HamiltonianExpectationExecutor | None = None
    nexus_analog: NexusAnalogSpec | None = None
    pauli_support_max_terms: int | None = None
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
        build_logical_circuits(self, angles, hea_depth)

    def compile(self) -> None:
        compile_circuits(self)

    def run(
        self,
        noise_rng: np.random.Generator | None = None,
        executor: HamiltonianExpectationExecutor | None = None,
    ) -> None:
        run_energy_estimation(self, noise_rng, executor)

    def evaluate(self) -> float:
        self._phase = ProtocolPhase.EVALUATE
        return float(self._counts.get("expectation", 0.0))

    def dataframe_circuit_shot_rows(self) -> list[dict[str, Any]]:
        return dataframe_circuit_shot_rows(self)

    def launch(self, store: SqliteJobStore) -> JobHandle:
        blob = pickle.dumps(self)
        jid = str(uuid.uuid4())
        ph = hashlib.sha256(blob).hexdigest()[:32]
        return store.enqueue(jid, blob, protocol_hash=ph)

    @staticmethod
    def process_job(store: SqliteJobStore, job_id: str) -> None:
        process_pauli_protocol_job(store, job_id)

    def retrieve(self, store: SqliteJobStore, handle: JobHandle) -> dict[str, Any]:
        return store.result(handle.job_id)

    def dumps(self) -> bytes:
        return pickle.dumps(self)

    @staticmethod
    def loads(data: bytes) -> PauliAveragingProtocol:
        return cast("PauliAveragingProtocol", pickle.loads(data))


__all__ = ["PauliAveragingProtocol", "ProtocolPhase"]
