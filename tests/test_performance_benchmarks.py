"""Performance benchmarks for qchem_stack operations.

This module provides benchmark tests to track performance metrics and detect regressions.
Benchmarks are marked with @pytest.mark.perf and excluded from default test runs.

Run with: pytest tests/test_performance_benchmarks.py -v -m perf
"""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pytest
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle
from qchem_stack.config import NexusAnalogSpec
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.protocols.protocol import PauliAveragingProtocol


class TestPipelinePerformance:
    """End-to-end pipeline performance benchmarks."""

    @pytest.mark.perf
    @pytest.mark.pyscf
    def test_h2_pipeline_performance(self, tmp_path: Path) -> None:
        """H2 pipeline should complete in < 5 seconds."""
        pytest.importorskip("pyscf")
        from qchem_stack.orchestration.pipeline import run_pipeline_from_config
        from tests.helpers.paths import configs_path

        cfg_path = configs_path("example_h2.yaml")
        db_path = tmp_path / "jobs.sqlite"

        start = time.perf_counter()
        run_pipeline_from_config(cfg_path, job_db=db_path)
        elapsed = time.perf_counter() - start

        # Baseline: should complete in < 5 seconds on modern hardware
        assert elapsed < 5.0, f"H2 pipeline took {elapsed:.2f}s (expected < 5s)"

    @pytest.mark.perf
    @pytest.mark.pyscf
    def test_h4_pipeline_performance(self, tmp_path: Path) -> None:
        """H4 pipeline should complete in < 10 seconds."""
        pytest.importorskip("pyscf")
        from qchem_stack.orchestration.pipeline import run_pipeline_from_config
        from tests.helpers.paths import configs_path

        cfg_path = configs_path("example_h4_schmidt_multifragment.yaml")
        if not cfg_path.exists():
            pytest.skip("H4 config not available")

        db_path = tmp_path / "jobs.sqlite"

        start = time.perf_counter()
        run_pipeline_from_config(cfg_path, job_db=db_path)
        elapsed = time.perf_counter() - start

        # Baseline: should complete in < 10 seconds
        assert elapsed < 10.0, f"H4 pipeline took {elapsed:.2f}s (expected < 10s)"


class TestZNEPerformance:
    """ZNE circuit folding performance benchmarks."""

    @pytest.mark.perf
    def test_zne_circuit_folding_performance(self) -> None:
        """ZNE circuit folding should be efficient (1000 gates in < 1 second)."""
        from qiskit import QuantumCircuit

        from qchem_stack.mitigation.zne import fold_unitary_circuit

        # Create a circuit with ~1000 gates
        qc = QuantumCircuit(10)
        for _ in range(100):
            for q in range(10):
                qc.rx(0.1, q)
            for q in range(9):
                qc.cx(q, q + 1)

        start = time.perf_counter()
        folded = fold_unitary_circuit(qc, n_folds=2)
        elapsed = time.perf_counter() - start

        # Baseline: should fold 1000-gate circuit in < 1 second
        assert elapsed < 1.0, f"ZNE folding took {elapsed:.2f}s (expected < 1s)"
        assert folded.num_qubits == 10


class TestSPAMPerformance:
    """SPAM correction performance benchmarks."""

    @pytest.mark.perf
    def test_spam_correction_performance(self) -> None:
        """SPAM correction for 12-qubit matrix should complete in < 2 seconds."""
        from qchem_stack.mitigation.spam import SPAMCalibration, correct_n_qubit_histogram

        n_qubits = 12
        dim = 2**n_qubits

        # Create a realistic assignment matrix (diagonal dominant)
        np.random.seed(42)
        mat = np.eye(dim) * 0.95
        for i in range(dim):
            for j in range(dim):
                if i != j:
                    mat[i, j] = 0.05 / (dim - 1)

        cal = SPAMCalibration(readout_assignment=mat.tolist())

        # Create realistic counts
        counts = {f"{i:0{n_qubits}b}": np.random.randint(0, 100) for i in range(dim)}

        start = time.perf_counter()
        result = correct_n_qubit_histogram(counts, cal, n_qubits)
        elapsed = time.perf_counter() - start

        # Baseline: should complete in < 2 seconds
        assert elapsed < 2.0, f"SPAM correction took {elapsed:.2f}s (expected < 2s)"
        assert len(result) == dim


class TestJobStorePerformance:
    """Job store throughput benchmarks."""

    @pytest.mark.perf
    def test_job_store_throughput(self, tmp_path: Path) -> None:
        """Job store should handle 1000 enqueues in < 1 second."""
        db_path = tmp_path / "perf.sqlite"
        store = SqliteJobStore(str(db_path))

        start = time.perf_counter()
        for i in range(1000):
            store.enqueue(f"job-{i}", b"test-payload")
        elapsed = time.perf_counter() - start

        # Baseline: should enqueue 1000 jobs in < 1 second
        assert elapsed < 1.0, f"Job enqueue took {elapsed:.2f}s (expected < 1s)"

    @pytest.mark.perf
    def test_job_store_query_performance(self, tmp_path: Path) -> None:
        """Job store queries should be fast (< 100ms for 1000 jobs)."""
        db_path = tmp_path / "query.sqlite"
        store = SqliteJobStore(str(db_path))

        # Enqueue 1000 jobs
        for i in range(1000):
            store.enqueue(f"job-{i}", b"test-payload")

        start = time.perf_counter()
        jobs = store.list_jobs(limit=100)
        elapsed = time.perf_counter() - start

        # Baseline: should query in < 100ms
        assert elapsed < 0.1, f"Job query took {elapsed:.3f}s (expected < 0.1s)"
        assert len(jobs) == 100


class TestProtocolPerformance:
    """Protocol processing performance benchmarks."""

    @pytest.mark.perf
    def test_protocol_instantiation_performance(self) -> None:
        """Protocol instantiation should be fast (< 10ms)."""
        h = QubitOperator(((0, "Z"),), 0.5) + QubitOperator((), 0.0)
        na = NexusAnalogSpec(enabled=True, project_label="perf")

        start = time.perf_counter()
        for _ in range(100):
            proto = PauliAveragingProtocol(
                hamiltonian=h,
                n_qubits=1,
                backend=BackendSpec(name="sim", shots_per_circuit=10),
                pass_bundle=CompilerPassBundle(),
                nexus_analog=na,
            )
            proto.instantiate()
        elapsed = time.perf_counter() - start

        # Baseline: should instantiate 100 protocols in < 1 second (10ms each)
        assert elapsed < 1.0, f"Protocol instantiation took {elapsed:.2f}s (expected < 1s)"

    @pytest.mark.perf
    def test_protocol_build_performance(self) -> None:
        """Protocol build should be efficient (< 50ms for small systems)."""
        h = QubitOperator("Z0", 0.5) + QubitOperator("X0 Y1", 0.3) + QubitOperator((), 0.0)
        na = NexusAnalogSpec(enabled=True, project_label="perf")

        proto = PauliAveragingProtocol(
            hamiltonian=h,
            n_qubits=2,
            backend=BackendSpec(name="sim", shots_per_circuit=10),
            pass_bundle=CompilerPassBundle(),
            nexus_analog=na,
        )
        proto.instantiate()

        start = time.perf_counter()
        for _ in range(20):
            proto.build(np.array([0.1, 0.2, 0.3, 0.4]), hea_depth=1)
        elapsed = time.perf_counter() - start

        # Baseline: should build 20 protocols in < 1 second (50ms each)
        assert elapsed < 1.0, f"Protocol build took {elapsed:.2f}s (expected < 1s)"


class TestHamiltonianPerformance:
    """Hamiltonian construction performance benchmarks."""

    @pytest.mark.perf
    @pytest.mark.pyscf
    def test_hamiltonian_build_performance(self) -> None:
        """Hamiltonian build should be fast (< 2 seconds for H2)."""
        pytest.importorskip("pyscf")
        from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input
        from qchem_stack.config import load_experiment_config
        from tests.helpers.paths import configs_path

        cfg_path = configs_path("example_h2.yaml")
        cfg = load_experiment_config(cfg_path)

        start = time.perf_counter()
        # Build pre-quantum input (includes Hamiltonian construction)
        from qchem_stack.chem.bridges.facade import classical_mean_field_via_solver_bridge

        ref = classical_mean_field_via_solver_bridge(cfg)
        pqi = build_pre_quantum_input(cfg, ref, cfg_path=cfg_path)
        elapsed = time.perf_counter() - start

        # Baseline: should build in < 2 seconds
        assert elapsed < 2.0, f"Hamiltonian build took {elapsed:.2f}s (expected < 2s)"
        assert pqi.n_qubits > 0
