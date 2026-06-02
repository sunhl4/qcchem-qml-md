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


def _mask_token(token: str) -> str:
    """Mask an API token for safe logging (show first 4 and last 4 chars)."""
    if len(token) <= 8:
        return "***"
    return f"{token[:4]}...{token[-4:]}"


def _resolve_uqc_token(meta: dict[str, Any] | None) -> str:
    """Resolve UQC API token from meta dict or environment variables.

    Raises ValueError if no token is found.
    """
    meta = meta or {}
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
    return token


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
        self._last_mitigation_trace: dict[str, Any] | None = None
        self._last_protocol_counts: dict[str, Any] | None = None

    def _try_uqc_zne_circuit_fold(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
        *,
        client: Any | None = None,
        energy_fn: Any | None = None,
    ) -> float | None:
        from qchem_stack_uqc.uqc_zne_fold import run_uqc_zne_circuit_fold, uqc_zne_mode

        meta = self.spec.meta or {}
        if uqc_zne_mode(meta) != "circuit_scale_fold":
            return None
        if client is None and energy_fn is None:
            client = self._get_uqc_client()
        extrapolated, protocol_counts, trace = run_uqc_zne_circuit_fold(
            hamiltonian,
            n_qubits,
            hea_depth,
            np.asarray(angles, dtype=float),
            int(self.spec.shots_per_circuit),
            client,
            self.spec,
            energy_fn=energy_fn,
        )
        self._last_mitigation_trace = trace
        self._last_protocol_counts = protocol_counts
        return float(extrapolated)

    def _apply_uqc_mitigation(self, raw_energy: float, meta: dict[str, Any]) -> float:
        from qchem_stack_uqc.uqc_mitigation import apply_uqc_zne_mitigation

        mitigated, trace = apply_uqc_zne_mitigation(
            raw_energy,
            meta,
            protocol_counts=self._last_protocol_counts,
        )
        self._last_mitigation_trace = trace
        if trace is not None:
            logger.debug(
                "UQC ZNE mitigation raw=%.8f extrapolated=%.8f scales=%s",
                trace["raw_energy"],
                trace["zne_extrapolated_energy"],
                trace["zne_scales"],
            )
        return mitigated

    def _get_uqc_client(self) -> Any:
        """Lazily initialize UQC client connection."""
        if self._client is not None:
            return self._client

        from qchem_stack_uqc.uqc_env import load_repo_dotenv

        load_repo_dotenv()

        try:
            from uqc_client import UQC
        except ImportError as e:
            raise ImportError(
                "UQC provider requires uqc-client. Install: pip install uqc-client"
            ) from e

        token = _resolve_uqc_token(self.spec.meta)
        self._client = UQC(token=token)
        logger.info("UQC client initialized (token=%s)", _mask_token(token))
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

        token = _resolve_uqc_token(self.spec.meta)
        self._backend = UQCBackend(token=token)
        logger.info("UQC Qiskit backend initialized (token=%s)", _mask_token(token))
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

            folded = self._try_uqc_zne_circuit_fold(
                hamiltonian,
                n_qubits,
                angles,
                hea_depth,
                energy_fn=lambda h, n, ang, depth, _shots, _client, _spec: StatevectorHeaExecutor().expectation_hea(  # noqa: ARG005
                    h, n, ang, depth
                ),
            )
            if folded is not None:
                return folded
            return StatevectorHeaExecutor().expectation_hea(
                hamiltonian, n_qubits, angles, hea_depth
            )

        return self._execute_on_uqc(hamiltonian, n_qubits, angles, hea_depth)

    def _execute_on_uqc(
        self,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
    ) -> float:
        """Submit HEA + grouped Pauli measurements to UQC (default) or legacy Z-only path."""
        from qiskit.quantum_info import Statevector

        from qchem_stack.backends.qiskit_executor import (
            hea_circuit_qiskit,
            openfermion_to_sparse_pauli_op,
        )
        from qchem_stack_uqc.uqc_transpiler import transpile_to_uqc_native

        meta = self.spec.meta or {}
        use_multi_basis = meta.get("uqc_multi_basis_pauli", True)

        try:
            client = self._get_uqc_client()
            folded = self._try_uqc_zne_circuit_fold(
                hamiltonian, n_qubits, angles, hea_depth, client=client
            )
            if folded is not None:
                return folded
            if use_multi_basis:
                from qchem_stack_uqc.uqc_pauli_shots import energy_estimate_grouped_uqc_shots

                raw = energy_estimate_grouped_uqc_shots(
                    hamiltonian,
                    n_qubits,
                    hea_depth,
                    np.asarray(angles, dtype=float),
                    int(self.spec.shots_per_circuit),
                    client,
                    self.spec,
                )
                return self._apply_uqc_mitigation(raw, meta)
            raw = self._execute_on_uqc_single_z_basis(
                client, hamiltonian, n_qubits, angles, hea_depth, meta
            )
            return self._apply_uqc_mitigation(raw, meta)

        except (ValueError, KeyError) as e:
            # Authentication or configuration errors - fail immediately
            logger.error("UQC configuration/authentication error: %s", e)
            raise RuntimeError(
                f"UQC configuration error (no fallback allowed): {e}"
            ) from e
        except (TimeoutError, ConnectionError, OSError) as e:
            # Transient network errors - can fallback
            logger.warning("UQC transient error: %s", e)
            allow_fallback = meta.get("uqc_allow_fallback", True)
            if not allow_fallback:
                raise RuntimeError(
                    f"UQC transient error (uqc_allow_fallback=false): {e}"
                ) from e
        except Exception as e:
            # Permanent errors (circuit invalid, hardware failure) - limited fallback
            logger.error("UQC permanent error: %s", e)
            allow_fallback = meta.get("uqc_allow_fallback", True)
            if not allow_fallback:
                raise RuntimeError(
                    f"UQC execution failed (uqc_allow_fallback=false): {e}"
                ) from e

        logger.warning("Falling back to statevector simulation")
        qc = hea_circuit_qiskit(n_qubits, hea_depth, np.asarray(angles, dtype=float))
        opt_level = int(meta.get("uqc_transpile_opt_level", self.spec.uqc_transpile_opt_level))
        qc_transpiled = transpile_to_uqc_native(qc, optimization_level=opt_level)
        sv = Statevector.from_instruction(qc_transpiled)
        op = openfermion_to_sparse_pauli_op(hamiltonian, n_qubits)
        return float(np.real(sv.expectation_value(op)))

    def _execute_on_uqc_single_z_basis(
        self,
        client: Any,
        hamiltonian: QubitOperator,
        n_qubits: int,
        angles: np.ndarray,
        hea_depth: int,
        meta: dict[str, Any],
    ) -> float:
        """Legacy: one Z-basis measurement (deprecated; biased for mixed Pauli)."""
        from qiskit import QuantumCircuit
        from qiskit.qasm3 import dumps

        from qchem_stack.backends.qiskit_executor import hea_circuit_qiskit
        from qchem_stack_uqc.uqc_transpiler import transpile_to_uqc_native

        qc = hea_circuit_qiskit(n_qubits, hea_depth, np.asarray(angles, dtype=float))
        opt_level = int(meta.get("uqc_transpile_opt_level", self.spec.uqc_transpile_opt_level))
        qc_transpiled = transpile_to_uqc_native(qc, optimization_level=opt_level)
        if qc_transpiled.num_clbits == 0:
            qc_meas = QuantumCircuit(qc_transpiled.num_qubits, qc_transpiled.num_qubits)
            qc_meas.compose(qc_transpiled, inplace=True)
            qc_meas.barrier()
            qc_meas.measure(range(qc_transpiled.num_qubits), range(qc_transpiled.num_qubits))
            qc_transpiled = qc_meas
        qasm3_str = dumps(qc_transpiled)
        shots = max(100, min(1000, int(self.spec.shots_per_circuit)))
        shots = ((shots + 99) // 100) * 100
        target = meta.get("uqc_target", "Matrix2")
        task_id = client.submit_task(convert_qprog=qasm3_str, target=target, shots=shots)
        if task_id is None:
            raise RuntimeError("UQC submit_task returned None")
        max_wait = float(meta.get("uqc_timeout_s", 300.0))
        poll_interval = float(meta.get("uqc_poll_interval_s", 2.0))
        elapsed = 0.0
        while elapsed < max_wait:
            status = client.get_task_status(task_id)
            if status == "SUCCESS":
                break
            if status == "FAILURE":
                raise RuntimeError(f"UQC task {task_id} failed on hardware")
            time.sleep(poll_interval)
            elapsed += poll_interval
        else:
            raise TimeoutError(f"UQC task {task_id} timed out after {max_wait}s")
        raw_result = client.get_task_result(task_id)
        if raw_result is None:
            raise RuntimeError(f"UQC task {task_id} returned no results")
        hist_data = raw_result[0]["datasets"]["computational_basis_histogram"]
        counts = self._artiq_histogram_to_counts(hist_data, n_qubits)
        return float(np.real(self._compute_expectation_from_counts(counts, hamiltonian, n_qubits)))

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
        from qchem_stack_uqc.uqc_pauli_measurement import (
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
