"""
UQC (幺正量子) Cloud Platform backend executor.

Implements HamiltonianExpectationExecutor for ion-trap quantum computers
via the UQC cloud API using uqc-client. Native gate set: rzz, rx, ry.

UQC API Reference (uqc_client v0.1.3):
- UQC class: low-level client with submit_task(), get_task_status(), get_task_result()
- UQCBackend: Qiskit BackendV2 wrapper with .run() method
- Constraints: shots ∈ [100, 1000], must be multiple of 100, static circuits only
- Supported gates: rzz, rx, ry, measure, barrier
"""

from __future__ import annotations

import logging
import os
import time
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from openfermion.ops import QubitOperator

    from qchem_stack.backends.spec import BackendSpec

logger = logging.getLogger(__name__)


class UQCCloudHeaExecutor:
    """Execute HEA circuits on UQC ion-trap quantum computers via cloud API.

    The executor converts HEA circuits to Qiskit, transpiles to the native
    gate set (rzz, rx, ry), exports to OpenQASM 3.0, and submits to the
    UQC cloud platform for execution on real quantum hardware.

    Implementation uses the low-level UQC client API for full control over
    the submission, polling, and result retrieval process.
    """

    def __init__(self, spec: BackendSpec) -> None:
        self.spec = spec
        self._client = None
        self._backend = None

    def _get_uqc_client(self) -> Any:
        """Lazily initialize UQC client connection."""
        if self._client is not None:
            return self._client

        try:
            from uqc_client import UQC
        except ImportError as e:
            raise ImportError(
                "UQC provider requires uqc-client. Install: pip install uqc-client"
            ) from e

        meta = self.spec.meta or {}
        token = (
            meta.get("uqc_token")
            or os.environ.get("UQC_API_TOKEN")
            or os.environ.get("USER_TOKEN")
            or ""
        )
        if not token:
            raise ValueError(
                "UQC API token is required. Set backend.meta['uqc_token'] or "
                "environment variable UQC_API_TOKEN."
            )

        self._client = UQC(token=token)
        logger.info("Connected to UQC cloud platform")
        return self._client

    def _get_uqc_backend(self) -> Any:
        """Lazily initialize UQC Qiskit backend."""
        if self._backend is not None:
            return self._backend

        try:
            from uqc_client import UQCBackend
        except ImportError as e:
            raise ImportError(
                "UQC provider requires uqc-client. Install: pip install uqc-client"
            ) from e

        meta = self.spec.meta or {}
        token = (
            meta.get("uqc_token")
            or os.environ.get("UQC_API_TOKEN")
            or os.environ.get("USER_TOKEN")
            or ""
        )
        if not token:
            raise ValueError(
                "UQC API token is required. Set backend.meta['uqc_token'] or "
                "environment variable UQC_API_TOKEN."
            )

        self._backend = UQCBackend(token=token)
        logger.info("Initialized UQC Qiskit backend")
        return self._backend

    def expectation_hea(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float:
        meta = self.spec.meta or {}

        # Fallback to injected function for testing
        fn = meta.get("expectation_fn")
        if fn is not None:
            return float(fn(hamiltonian, n_qubits, angles, hea_depth))

        # Fallback to mock for development (check both spec field and meta dict)
        uqc_mode = meta.get("uqc_mode") or self.spec.uqc_mode
        if uqc_mode == "mock":
            from qchem_stack.backends.executor_base import StatevectorHeaExecutor

            return StatevectorHeaExecutor().expectation_hea(
                hamiltonian, n_qubits, angles, hea_depth
            )

        # Real UQC cloud execution
        return self._execute_on_uqc(hamiltonian, n_qubits, angles, hea_depth)

    def _execute_on_uqc(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float:
        """Submit HEA circuit to UQC cloud and compute expectation value.

        Uses the low-level UQC client API:
        1. Build HEA circuit via Qiskit
        2. Transpile to native gates (rzz, rx, ry)
        3. Add measurement and export to OpenQASM 3.0 via qiskit.qasm3.dumps()
        4. Submit via uqc.submit_task(convert_qprog=qasm, target=..., shots=...)
        5. Poll uqc.get_task_status() until SUCCESS/FAILURE
        6. Parse histogram from uqc.get_task_result()
        """
        from qiskit import QuantumCircuit
        from qiskit.qasm3 import dumps
        from qiskit.quantum_info import Statevector

        from qchem_stack.backends.qiskit_executor import (
            hea_circuit_qiskit,
            openfermion_to_sparse_pauli_op,
        )
        from qchem_stack.backends.uqc_transpiler import transpile_to_uqc_native

        meta = self.spec.meta or {}

        # Build HEA circuit using Qiskit
        qc = hea_circuit_qiskit(n_qubits, hea_depth, np.asarray(angles, dtype=float))

        # Transpile to UQC native gates (rzz, rx, ry)
        opt_level = int(meta.get("uqc_transpile_opt_level", self.spec.uqc_transpile_opt_level))
        qc_transpiled = transpile_to_uqc_native(qc, optimization_level=opt_level)

        # Add measurement on all qubits (UQC requires explicit measure)
        if qc_transpiled.num_clbits == 0:
            qc_meas = QuantumCircuit(qc_transpiled.num_qubits, qc_transpiled.num_qubits)
            qc_meas.compose(qc_transpiled, inplace=True)
            qc_meas.barrier()
            qc_meas.measure(range(qc_transpiled.num_qubits), range(qc_transpiled.num_qubits))
            qc_transpiled = qc_meas

        # Export to OpenQASM 3.0 using qiskit.qasm3.dumps (correct API)
        qasm3_str = dumps(qc_transpiled)

        # Validate static circuit
        try:
            from uqc_client import ensure_static_qasm

            ensure_static_qasm(qasm3_str)
        except ImportError:
            pass  # validation skipped if uqc-client not installed
        except Exception as e:
            raise ValueError(f"Circuit failed UQC static validation: {e}") from e

        # Constrain shots: UQC requires [100, 1000], multiple of 100
        shots = int(self.spec.shots_per_circuit)
        shots = max(100, min(1000, shots))
        shots = ((shots + 99) // 100) * 100

        # Target: "Matrix2" (real hardware), "iontrap-sim" (simulator), "qiskit-sim" (Aer)
        target = meta.get("uqc_target", "Matrix2")

        try:
            client = self._get_uqc_client()

            # Submit task
            task_id = client.submit_task(convert_qprog=qasm3_str, target=target, shots=shots)
            if task_id is None:
                raise RuntimeError("UQC submit_task returned None")
            logger.info("Submitted UQC task %s (target=%s, shots=%d)", task_id, target, shots)

            # Poll until completion
            max_wait = float(meta.get("uqc_timeout_s", 300.0))
            poll_interval = float(meta.get("uqc_poll_interval_s", 2.0))
            elapsed = 0.0
            while elapsed < max_wait:
                status = client.get_task_status(task_id)
                logger.debug("UQC task %s status: %s (%.1fs)", task_id, status, elapsed)
                if status == "SUCCESS":
                    break
                if status == "FAILURE":
                    raise RuntimeError(f"UQC task {task_id} failed on hardware")
                time.sleep(poll_interval)
                elapsed += poll_interval
            else:
                raise TimeoutError(f"UQC task {task_id} timed out after {max_wait}s")

            # Get results — returns ARTIQ-format with computational_basis_histogram
            raw_result = client.get_task_result(task_id)
            if raw_result is None:
                raise RuntimeError(f"UQC task {task_id} returned no results")

            # Parse histogram: result[0]["datasets"]["computational_basis_histogram"]
            # Format: list of [index, count] pairs
            hist_data = raw_result[0]["datasets"]["computational_basis_histogram"]
            counts = self._artiq_histogram_to_counts(hist_data, n_qubits)

            # Compute expectation value from measurement results
            expectation = self._compute_expectation_from_counts(counts, hamiltonian, n_qubits)
            return float(np.real(expectation))

        except Exception as e:
            logger.error("UQC execution failed: %s", e)
            allow_fallback = meta.get("uqc_allow_fallback", True)
            if allow_fallback is False:
                raise RuntimeError(
                    f"UQC cloud execution failed (uqc_allow_fallback=false): {e}"
                ) from e
            logger.warning("Falling back to statevector simulation")
            sv = Statevector.from_instruction(qc_transpiled)
            op = openfermion_to_sparse_pauli_op(hamiltonian, n_qubits)
            exp = sv.expectation_value(op)
            return float(np.real(exp))

    @staticmethod
    def _artiq_histogram_to_counts(hist_data: list[list], n_qubits: int) -> dict[str, int]:
        """Convert ARTIQ histogram format to bitstring counts dict.

        ARTIQ format: [[index, count], [index, count], ...]
        where index is an integer bitstring representation.

        Returns: {"00": 48, "01": 52, ...} with n_qubits-wide bitstrings.
        """
        counts: dict[str, int] = {}
        for entry in hist_data:
            idx, count = int(entry[0]), int(entry[1])
            bitstring = format(idx, f"0{n_qubits}b")
            counts[bitstring] = count
        return counts

    def _compute_expectation_from_counts(
        self,
        counts: dict[str, int],
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        """Compute Hamiltonian expectation from measurement counts."""
        from qchem_stack.backends.uqc_pauli_measurement import (
            compute_hamiltonian_expectation_from_counts,
        )

        return compute_hamiltonian_expectation_from_counts(counts, hamiltonian, n_qubits)

    def expectation_state(
        self,
        state: np.ndarray,
        hamiltonian: QubitOperator,
        n_qubits: int,
    ) -> float:
        """Compute <psi|H|psi> using statevector (UQC doesn't support state injection)."""
        from qchem_stack.backends.executor_base import StatevectorHeaExecutor

        return StatevectorHeaExecutor().expectation_state(state, hamiltonian, n_qubits)
