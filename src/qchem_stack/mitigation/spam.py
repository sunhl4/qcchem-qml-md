"""State Preparation and Measurement (SPAM) error mitigation.

This module provides production-ready SPAM correction implementations including:
- Single-bit readout correction from calibrated assignment matrices
- Multi-qubit histogram inversion with Tikhonov regularization
- Tensor-product structure for independent qubit errors
- Uncertainty propagation via condition number estimation
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class SPAMCalibration:
    """Readout assignment matrix ``P(read=i | true=j)`` (column-stochastic).

    For a single qubit, the matrix is 2x2::

        [[P(0|0), P(0|1)],
         [P(1|0), P(1|1)]]

    For n qubits with independent errors, provide per-qubit 2x2 matrices
    via ``per_qubit_matrices``. For correlated errors, provide the full
    ``2^n x 2^n`` matrix via ``readout_assignment``.
    """

    readout_assignment: list[list[float]] | None = None
    """Full assignment matrix (for correlated readout errors)."""

    per_qubit_matrices: list[list[list[float]]] | None = None
    """Per-qubit 2x2 assignment matrices (for independent errors, tensor-product structure)."""


def default_two_qubit_spam_matrix() -> list[list[float]]:
    """Toy symmetric assignment matrix for two qubits (diagonal dominant).

    Returns a 4x4 matrix with ``P(correct) = 0.94`` and symmetric crosstalk.
    For production use, replace with experimentally calibrated matrices.
    """
    eps = 0.02
    return [
        [1.0 - eps, eps, eps, eps],
        [eps, 1.0 - eps, eps, eps],
        [eps, eps, 1.0 - eps, eps],
        [eps, eps, eps, 1.0 - eps],
    ]


def apply_spam(prob_0: float, cal: SPAMCalibration) -> float:
    """Correct a single-bit probability using the calibration matrix.

    Given the measured ``P(measured=0)`` and a 2x2 assignment matrix::

        M = [[P(0|0), P(0|1)],
             [P(1|0), P(1|1)]]

    The corrected ``P(true=0)`` is computed via matrix inversion::

        [P(true=0)]   = M^{-1} @ [P(measured=0)]
        [P(true=1)]              [P(measured=1)]

    Parameters
    ----------
    prob_0
        Measured probability of outcome ``0``.
    cal
        Calibration data. If ``readout_assignment`` is a 2x2 matrix, uses it
        directly. If ``per_qubit_matrices`` has one entry, uses that.
        If ``None``, returns ``prob_0`` unchanged.

    Returns
    -------
    Corrected ``P(true=0)``, clamped to ``[0, 1]``.
    """
    mat = None
    if cal.per_qubit_matrices is not None and len(cal.per_qubit_matrices) >= 1:
        mat = np.asarray(cal.per_qubit_matrices[0], dtype=float)
    elif cal.readout_assignment is not None:
        mat = np.asarray(cal.readout_assignment, dtype=float)
        if mat.shape != (2, 2):
            logger.warning(
                "apply_spam expects 2x2 matrix for single-bit correction, got %s; "
                "returning uncorrected probability",
                mat.shape,
            )
            return prob_0

    if mat is None:
        return prob_0

    prob_1 = 1.0 - prob_0
    measured = np.array([prob_0, prob_1], dtype=float)

    try:
        true_probs = np.linalg.solve(mat.T, measured)
    except np.linalg.LinAlgError:
        logger.warning("Singular calibration matrix; returning uncorrected probability")
        return prob_0

    corrected = float(true_probs[0])
    return max(0.0, min(1.0, corrected))


def correct_two_qubit_histogram(
    counts: dict[str, int],
    cal: SPAMCalibration,
    *,
    regularization: float = 0.0,
) -> dict[str, float]:
    """Invert a 2-qubit assignment matrix on ``00/01/10/11`` counts.

    Solves ``M^T @ true_probs = observed_probs`` where ``M`` is the readout
    assignment matrix. Optionally applies Tikhonov regularization to stabilize
    inversion of ill-conditioned matrices.

    Parameters
    ----------
    counts
        Measurement counts keyed by bitstring (e.g., ``{"00": 500, "01": 10, ...}``).
    cal
        Calibration data with a 4x4 ``readout_assignment`` matrix.
    regularization
        Tikhonov regularization parameter ``lambda`` (default 0 = no regularization).
        Adds ``lambda * I`` to ``M^T M`` before solving, which stabilizes inversion
        but biases the result toward uniform distribution.

    Returns
    -------
    Corrected probability distribution over ``{"00", "01", "10", "11"}``.
    """
    keys = ["00", "01", "10", "11"]

    if cal.readout_assignment is None:
        total = max(sum(counts.values()), 1)
        return {k: float(counts.get(k, 0)) / float(total) for k in keys}

    mat = np.asarray(cal.readout_assignment, dtype=float)
    if mat.shape != (4, 4):
        raise ValueError(f"Expected 4x4 assignment matrix, got {mat.shape}")

    obs = np.array([float(counts.get(k, 0)) for k in keys], dtype=float)
    total = obs.sum()
    if total <= 0:
        return {k: 0.25 for k in keys}
    obs = obs / total

    if regularization > 0:
        # Tikhonov: solve (M^T M + λI) x = M^T obs
        mtm = mat.T @ mat + regularization * np.eye(4)
        try:
            true_probs = np.linalg.solve(mtm, mat.T @ obs)
        except np.linalg.LinAlgError:
            logger.warning("Regularized solve failed; falling back to unregularized")
            true_probs = obs
    else:
        try:
            true_probs = np.linalg.solve(mat.T, obs)
        except np.linalg.LinAlgError:
            logger.warning("Singular calibration matrix; returning observed distribution")
            true_probs = obs

    true_probs = np.clip(true_probs, 0.0, None)
    s = float(true_probs.sum()) or 1.0
    true_probs = true_probs / s
    return {k: float(true_probs[i]) for i, k in enumerate(keys)}


def correct_n_qubit_histogram(
    counts: dict[str, int],
    cal: SPAMCalibration,
    n_qubits: int,
    *,
    regularization: float = 0.0,
) -> dict[str, float]:
    """Correct an n-qubit measurement histogram.

    Supports two modes:
    1. **Full matrix**: Provide a ``2^n x 2^n`` ``readout_assignment`` for
       correlated readout errors.
    2. **Tensor product**: Provide ``per_qubit_matrices`` (list of n 2x2 matrices)
       for independent per-qubit errors. The full matrix is constructed as the
       Kronecker product, which is memory-efficient for ``n <= 12`` qubits.

    Parameters
    ----------
    counts
        Measurement counts keyed by n-bit bitstrings.
    cal
        Calibration data (full matrix or per-qubit matrices).
    n_qubits
        Number of qubits.
    regularization
        Tikhonov regularization parameter (default 0).

    Returns
    -------
    Corrected probability distribution over all ``2^n`` bitstrings.
    """
    MAX_FULL_MATRIX_QUBITS = 12

    uses_tensor_product = (
        cal.per_qubit_matrices is not None and len(cal.per_qubit_matrices) == n_qubits
    )
    if not uses_tensor_product and n_qubits > MAX_FULL_MATRIX_QUBITS:
        raise ValueError(
            f"Full-matrix SPAM correction for {n_qubits} qubits would require "
            f"a {2**n_qubits}x{2**n_qubits} matrix (~{2 ** (2 * n_qubits) * 8 / 1e9:.1f} GB). "
            f"Use per_qubit_matrices (tensor-product) or limit n_qubits <= {MAX_FULL_MATRIX_QUBITS}."
        )

    dim = 2**n_qubits

    # Runtime memory guard for matrix construction
    required_bytes = dim * dim * 8  # 8 bytes per float64
    try:
        import psutil

        available = psutil.virtual_memory().available
    except ImportError:
        available = None

    if available is not None and required_bytes > available * 0.8:
        raise MemoryError(
            f"SPAM correction requires ~{required_bytes / 1e9:.1f} GB but only "
            f"{available / 1e9:.1f} GB available. Use per_qubit_matrices or reduce n_qubits."
        )

    if uses_tensor_product:
        assert cal.per_qubit_matrices is not None
        # Build tensor-product matrix
        mat = np.asarray(cal.per_qubit_matrices[0], dtype=float)
        for q_mat in cal.per_qubit_matrices[1:]:
            mat = np.kron(mat, np.asarray(q_mat, dtype=float))
    elif cal.readout_assignment is not None:
        mat = np.asarray(cal.readout_assignment, dtype=float)
        if mat.shape != (dim, dim):
            raise ValueError(
                f"Expected {dim}x{dim} assignment matrix for {n_qubits} qubits, got {mat.shape}"
            )
    else:
        # No calibration: return observed distribution
        total = max(sum(counts.values()), 1)
        keys = [format(i, f"0{n_qubits}b") for i in range(dim)]
        return {k: float(counts.get(k, 0)) / float(total) for k in keys}

    keys = [format(i, f"0{n_qubits}b") for i in range(dim)]
    obs = np.array([float(counts.get(k, 0)) for k in keys], dtype=float)
    total = obs.sum()
    if total <= 0:
        return {k: 1.0 / dim for k in keys}
    obs = obs / total

    if regularization > 0:
        mtm = mat.T @ mat + regularization * np.eye(dim)
        try:
            true_probs = np.linalg.solve(mtm, mat.T @ obs)
        except np.linalg.LinAlgError:
            logger.warning("Regularized solve failed; returning observed distribution")
            true_probs = obs
    else:
        try:
            true_probs = np.linalg.solve(mat.T, obs)
        except np.linalg.LinAlgError:
            logger.warning("Singular calibration matrix; returning observed distribution")
            true_probs = obs

    true_probs = np.clip(true_probs, 0.0, None)
    s = float(true_probs.sum()) or 1.0
    true_probs = true_probs / s
    return {k: float(true_probs[i]) for i, k in enumerate(keys)}


def propagate_spam_uncertainty(
    counts: dict[str, int],
    cal: SPAMCalibration,
    n_qubits: int = 2,
) -> dict[str, float]:
    """Estimate uncertainty in corrected probabilities via condition number.

    Uses the condition number of the calibration matrix to propagate statistical
    uncertainty from shot noise. For a well-conditioned matrix (condition number
    close to 1), the uncertainty is approximately ``sqrt(p * (1-p) / N)`` where
    ``N`` is the total shot count. For ill-conditioned matrices, the uncertainty
    is amplified by the condition number.

    Parameters
    ----------
    counts
        Measurement counts.
    cal
        Calibration data.
    n_qubits
        Number of qubits (default 2).

    Returns
    -------
    Dictionary mapping bitstrings to their estimated standard errors.
    """
    dim = 2**n_qubits
    keys = [format(i, f"0{n_qubits}b") for i in range(dim)]

    if cal.per_qubit_matrices is not None and len(cal.per_qubit_matrices) == n_qubits:
        mat = np.asarray(cal.per_qubit_matrices[0], dtype=float)
        for q_mat in cal.per_qubit_matrices[1:]:
            mat = np.kron(mat, np.asarray(q_mat, dtype=float))
    elif cal.readout_assignment is not None:
        mat = np.asarray(cal.readout_assignment, dtype=float)
    else:
        # No calibration: return shot-noise uncertainty
        total = max(sum(counts.values()), 1)
        return {
            k: float(
                np.sqrt(
                    float(counts.get(k, 0)) / total * (1 - float(counts.get(k, 0)) / total) / total
                )
            )
            for k in keys
        }

    try:
        cond = np.linalg.cond(mat)
    except np.linalg.LinAlgError:
        logger.warning("Cannot compute condition number; returning shot-noise uncertainty")
        cond = 1.0

    total = max(sum(counts.values()), 1)
    obs_probs = np.array([float(counts.get(k, 0)) / total for k in keys])

    # Shot noise: sigma = sqrt(p * (1-p) / N), amplified by condition number
    uncertainties = np.sqrt(obs_probs * (1 - obs_probs) / total) * cond
    return {k: float(uncertainties[i]) for i, k in enumerate(keys)}
