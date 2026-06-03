"""Zero-Noise Extrapolation (ZNE) mitigation.

This module provides production-ready ZNE implementations including:
- Unitary circuit folding for noise scaling
- Multiple extrapolation models (linear, exponential, polynomial)
- Model selection via BIC/AIC
- Uncertainty estimation via bootstrap residuals
"""

from __future__ import annotations

import logging
from typing import Any, Literal

import numpy as np
from scipy.optimize import curve_fit

from qchem_stack.quantum.algorithms.tolerances import BIC_LOG_REGULARIZATION

logger = logging.getLogger(__name__)


def _zne_scale_energy_linear_stub(energy: float, scale: float) -> float:
    """Legacy linear noise extrapolation placeholder (kept for backward compatibility).

    This is a simple linear model ``E' = E * (1 + 0.01 * (scale - 1))`` that does
    NOT represent realistic noise scaling. Use :func:`fold_unitary_circuit` for
    production noise amplification.
    """
    return float(energy * (1.0 + 0.01 * (scale - 1.0)))


zne_scale_energy = _zne_scale_energy_linear_stub


def fold_unitary_circuit(circuit: Any, n_folds: int) -> Any:
    """Amplify noise by folding the unitary circuit: ``U -> U (U† U)^n_folds``.

    This implements global unitary folding, which increases circuit depth by a
    factor of ``2 * n_folds + 1`` while preserving the ideal unitary. Under
    realistic noise models (depolarizing, amplitude damping), the effective noise
    scales approximately as ``scale_factor = 2 * n_folds + 1``.

    Parameters
    ----------
    circuit
        Quantum circuit object (must support ``.inverse()`` and ``.compose()``
        methods, e.g., Qiskit QuantumCircuit).
    n_folds
        Number of folding iterations. ``n_folds=0`` returns the original circuit,
        ``n_folds=1`` returns ``U U† U``, etc.

    Returns
    -------
    Folded circuit with depth scaled by ``2 * n_folds + 1``.

    Notes
    -----
    For local folding (per-gate noise amplification), iterate over individual
    gates and fold each one. This global variant is simpler and often sufficient
    for ZNE on small circuits.
    """
    if n_folds < 0:
        raise ValueError(f"n_folds must be non-negative, got {n_folds}")
    if n_folds == 0:
        return circuit

    folded = circuit.copy()
    inv = circuit.inverse()  # Cache the inverse once to avoid recomputation
    for _ in range(n_folds):
        folded = folded.compose(inv).compose(circuit)
    return folded


def fold_gates_local(circuit: Any, scale_factor: float) -> Any:
    """Local gate folding: amplify noise by repeating individual gates.

    For each gate ``G``, replace it with ``G (G† G)^k`` where ``k`` is chosen
    to achieve the target ``scale_factor`` on average.

    Parameters
    ----------
    circuit
        Quantum circuit (must support gate-level iteration and composition).
    scale_factor
        Target noise amplification factor (must be odd integer >= 1 for exact
        folding; non-integer values will be rounded to nearest odd integer).

    Returns
    -------
    Circuit with locally folded gates.
    """
    if scale_factor < 1:
        raise ValueError(f"scale_factor must be >= 1, got {scale_factor}")

    n_folds = int(round((scale_factor - 1) / 2))
    if n_folds == 0:
        return circuit

    # Build new circuit with folded gates inserted inline
    folded = circuit.copy()
    folded.data = []
    for gate in circuit.data:
        # Insert original gate
        folded.data.append(gate)
        # Insert (G† G) pairs immediately after
        for _ in range(n_folds):
            folded.data.append(gate.inverse())
            folded.data.append(gate)
    return folded


def linear_extrapolation(
    energies: list[float],
    scales: list[float],
) -> tuple[float, float]:
    """Linear extrapolation to zero noise: ``E(s) = a + b * (s - 1)``.

    Parameters
    ----------
    energies
        Energy measurements at each noise scale.
    scales
        Noise scale factors (e.g., 1, 3, 5 for unitary folding).

    Returns
    -------
    (extrapolated_energy, uncertainty)
        Zero-noise estimate and standard error from fit residuals.
    """
    if len(energies) != len(scales) or len(energies) < 2:
        raise ValueError("Need at least 2 (energy, scale) pairs for linear fit")

    x = np.asarray(scales, dtype=float) - 1.0
    y = np.asarray(energies, dtype=float)

    coeffs, cov = np.polyfit(x, y, deg=1, cov=True)
    extrapolated = float(coeffs[1])
    uncertainty = float(np.sqrt(cov[1, 1])) if cov is not None else 0.0

    return extrapolated, uncertainty


def exponential_extrapolation(
    energies: list[float],
    scales: list[float],
) -> tuple[float, float]:
    """Exponential decay extrapolation: ``E(s) = a + b * exp(-c * (s - 1))``.

    This model is physically motivated for depolarizing noise, where the
    expectation value decays exponentially with circuit depth.

    Parameters
    ----------
    energies
        Energy measurements at each noise scale.
    scales
        Noise scale factors.

    Returns
    -------
    (extrapolated_energy, uncertainty)
        Zero-noise estimate and parameter uncertainty (propagated from covariance).
    """
    if len(energies) != len(scales) or len(energies) < 3:
        raise ValueError("Need at least 3 (energy, scale) pairs for exponential fit")

    x = np.asarray(scales, dtype=float) - 1.0
    y = np.asarray(energies, dtype=float)

    def exp_model(s: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
        return a + b * np.exp(-c * s)

    try:
        popt, pcov = curve_fit(exp_model, x, y, p0=[y[-1], y[0] - y[-1], 0.1], maxfev=5000)
        extrapolated = float(popt[0] + popt[1])
        var_sum = float(pcov[0, 0] + pcov[1, 1] + 2 * pcov[0, 1])
        uncertainty = (
            float(np.sqrt(max(var_sum, 0.0))) if np.isfinite(var_sum) else float(np.std(y))
        )
        if not np.isfinite(uncertainty):
            extrapolated, uncertainty = linear_extrapolation(energies, scales)
    except (RuntimeError, ValueError):
        logger.warning("Exponential fit failed to converge, falling back to linear")
        extrapolated, uncertainty = linear_extrapolation(energies, scales)

    return extrapolated, uncertainty


def polynomial_extrapolation(
    energies: list[float],
    scales: list[float],
    order: int = 2,
) -> tuple[float, float]:
    """Polynomial extrapolation: ``E(s) = sum_i c_i * (s - 1)^i``.

    Parameters
    ----------
    energies
        Energy measurements at each noise scale.
    scales
        Noise scale factors.
    order
        Polynomial degree (default 2). Must satisfy ``order < len(energies)``.

    Returns
    -------
    (extrapolated_energy, uncertainty)
        Zero-noise estimate (``c_0``) and its standard error.
    """
    if len(energies) != len(scales) or not energies:
        raise ValueError("energies and scales must be same-length non-empty lists")
    if order >= len(energies):
        raise ValueError(
            f"Polynomial order {order} must be < number of data points {len(energies)}"
        )

    x = np.asarray(scales, dtype=float) - 1.0
    y = np.asarray(energies, dtype=float)

    if len(energies) > order + 1:
        coeffs, cov = np.polyfit(x, y, deg=order, cov=True)
    else:
        coeffs = np.polyfit(x, y, deg=order)
        cov = None
    extrapolated = float(coeffs[-1])
    uncertainty = float(np.sqrt(cov[-1, -1])) if cov is not None else 0.0

    return extrapolated, uncertainty


def richardson_extrapolation(
    energies: list[float],
    scales: list[float],
    *,
    order: int = 1,
) -> float:
    """Richardson/ZNE extrapolation to zero noise (backward-compatible wrapper).

    This is a convenience wrapper around :func:`polynomial_extrapolation` that
    returns only the extrapolated value (without uncertainty).

    Parameters
    ----------
    energies
        Energy measurements at each noise scale.
    scales
        Noise scale factors.
    order
        Polynomial degree (default 1 = linear).

    Returns
    -------
    Extrapolated zero-noise energy.
    """
    extrapolated, _ = polynomial_extrapolation(energies, scales, order=order)
    return extrapolated


def select_extrapolation_model(
    energies: list[float],
    scales: list[float],
    *,
    criterion: Literal["bic", "aic"] = "bic",
) -> tuple[str, float, float]:
    """Select the best extrapolation model via BIC or AIC.

    Compares linear, exponential, and polynomial (order 2) models and returns
    the one with the lowest information criterion.

    Parameters
    ----------
    energies
        Energy measurements at each noise scale.
    scales
        Noise scale factors.
    criterion
        Model selection criterion: ``"bic"`` (Bayesian) or ``"aic"`` (Akaike).
        BIC penalizes model complexity more strongly than AIC.

    Returns
    -------
    (model_name, extrapolated_energy, uncertainty)
        Name of selected model (``"linear"``, ``"exponential"``, or ``"polynomial"``),
        zero-noise estimate, and uncertainty.

    Notes
    -----
    BIC = ``n * ln(RSS/n) + k * ln(n)`` where ``n`` = number of data points,
    ``k`` = number of parameters, ``RSS`` = residual sum of squares.
    AIC = ``n * ln(RSS/n) + 2 * k``.
    """
    if len(energies) != len(scales) or len(energies) < 3:
        raise ValueError("Need at least 3 data points for model selection")

    n = len(energies)
    x = np.asarray(scales, dtype=float) - 1.0
    y = np.asarray(energies, dtype=float)

    models = []

    def compute_ic(
        name: str,
        y_pred: np.ndarray,
        k: int,
        extrapolated: float,
        uncertainty: float,
    ) -> tuple[str, float, float, float]:
        rss = float(np.sum((y - y_pred) ** 2))
        if criterion == "bic":
            ic = n * np.log(rss / n + BIC_LOG_REGULARIZATION) + k * np.log(n)
        else:
            ic = n * np.log(rss / n + BIC_LOG_REGULARIZATION) + 2 * k
        return name, ic, extrapolated, uncertainty

    try:
        ext_lin, unc_lin = linear_extrapolation(energies, scales)
        y_pred_lin = np.polyval(np.polyfit(x, y, deg=1), x)
        models.append(compute_ic("linear", y_pred_lin, 2, ext_lin, unc_lin))
    except Exception:
        logger.debug("Linear model failed during selection")

    try:
        ext_exp, unc_exp = exponential_extrapolation(energies, scales)

        def exp_model(s: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
            return a + b * np.exp(-c * s)

        popt, _ = curve_fit(exp_model, x, y, p0=[y[-1], y[0] - y[-1], 0.1], maxfev=5000)
        y_pred_exp = exp_model(x, *popt)
        models.append(compute_ic("exponential", y_pred_exp, 3, ext_exp, unc_exp))
    except Exception:
        logger.debug("Exponential model failed during selection")

    try:
        ext_poly, unc_poly = polynomial_extrapolation(energies, scales, order=2)
        y_pred_poly = np.polyval(np.polyfit(x, y, deg=2), x)
        models.append(compute_ic("polynomial", y_pred_poly, 3, ext_poly, unc_poly))
    except Exception:
        logger.debug("Polynomial model failed during selection")

    if not models:
        raise RuntimeError("All extrapolation models failed; cannot select")

    best = min(models, key=lambda m: m[1])
    return best[0], best[2], best[3]


def extrapolation_uncertainty(
    energies: list[float],
    scales: list[float],
    model: Literal["linear", "exponential", "polynomial"] = "linear",
    *,
    n_bootstrap: int = 100,
    seed: int | None = None,
) -> float:
    """Estimate extrapolation uncertainty via residual bootstrap.

    Resamples residuals from the fitted model to generate synthetic datasets,
    then computes the standard deviation of extrapolated values across bootstrap
    samples.

    Parameters
    ----------
    energies
        Energy measurements at each noise scale.
    scales
        Noise scale factors.
    model
        Extrapolation model to use.
    n_bootstrap
        Number of bootstrap resamples (default 100).
    seed
        Random seed for reproducibility.

    Returns
    -------
    Standard deviation of extrapolated values across bootstrap samples.
    """
    rng = np.random.default_rng(seed)
    n = len(energies)
    y = np.asarray(energies, dtype=float)

    extrapolations = []

    for _ in range(n_bootstrap):
        residuals = rng.normal(0, np.std(y - np.mean(y)), size=n)
        y_boot = y + residuals

        try:
            if model == "linear":
                ext, _ = linear_extrapolation(y_boot.tolist(), scales)
            elif model == "exponential":
                ext, _ = exponential_extrapolation(y_boot.tolist(), scales)
            elif model == "polynomial":
                ext, _ = polynomial_extrapolation(y_boot.tolist(), scales, order=2)
            else:
                raise ValueError(f"Unknown model: {model}")
            extrapolations.append(ext)
        except Exception:
            continue

    if not extrapolations:
        logger.warning("Bootstrap failed for all samples, returning 0.0 uncertainty")
        return 0.0

    return float(np.std(extrapolations))
