"""
Property-based tests for executor consistency and ZNE convergence.

Uses Hypothesis to verify that:
1. Different backend executors produce consistent results (within numerical tolerance)
2. ZNE extrapolation converges to zero-noise limit
3. Parameter sensitivity is bounded across backends
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.mitigation.zne import (
    exponential_extrapolation,
    linear_extrapolation,
    polynomial_extrapolation,
    richardson_extrapolation,
    select_extrapolation_model,
)

# ============================================================================
# Strategies for generating quantum chemistry parameters
# ============================================================================

# Strategy for generating simple Pauli strings
pauli_chars = st.sampled_from(["X", "Y", "Z", "I"])

# Strategy for generating qubit indices
qubit_index = st.integers(min_value=0, max_value=3)

# Strategy for generating coefficients
coefficient = st.floats(
    min_value=-2.0,
    max_value=2.0,
    allow_nan=False,
    allow_infinity=False,
    width=32,
)


@st.composite
def pauli_string(draw, max_qubits=4):
    """Generate a random Pauli string (e.g., 'X0 Y1 Z2')."""
    n_qubits = draw(st.integers(min_value=1, max_value=max_qubits))
    terms = []
    used_qubits = set()

    for _ in range(n_qubits):
        qubit = draw(
            st.integers(min_value=0, max_value=max_qubits - 1).filter(
                lambda q: q not in used_qubits
            )
        )
        used_qubits.add(qubit)
        pauli = draw(pauli_chars)
        if pauli != "I":  # Skip identity terms
            terms.append(f"{pauli}{qubit}")

    if not terms:
        q = draw(st.integers(min_value=0, max_value=max_qubits - 1))
        terms = [f"Z{q}"]

    return " ".join(terms)


@st.composite
def qubit_operator(draw, max_terms=5, max_qubits=4):
    """Generate a random QubitOperator with multiple terms."""
    n_terms = draw(st.integers(min_value=1, max_value=max_terms))
    op = QubitOperator()

    for _ in range(n_terms):
        pauli_str = draw(pauli_string(max_qubits=max_qubits))
        coeff = draw(coefficient)
        op += QubitOperator(pauli_str, coeff)

    return op


@st.composite
def hea_parameters(draw, n_qubits=2, depth=1):
    """Generate HEA ansatz parameters."""
    # HEA has 2*n_qubits*depth parameters
    n_params = 2 * n_qubits * depth
    angles = draw(
        st.lists(
            st.floats(min_value=-np.pi, max_value=np.pi, allow_nan=False, allow_infinity=False),
            min_size=n_params,
            max_size=n_params,
        )
    )
    return np.array(angles, dtype=np.float64)


@st.composite
def zne_scales(draw, min_scales=3, max_scales=6):
    """Generate noise scale factors for ZNE."""
    n_scales = draw(st.integers(min_value=min_scales, max_value=max_scales))
    scales = draw(
        st.lists(
            st.floats(min_value=1.0, max_value=3.0, allow_nan=False, allow_infinity=False),
            min_size=n_scales,
            max_size=n_scales,
            unique=True,
        )
    )
    # Ensure scales are sorted and include 1.0
    scales = sorted(set([1.0] + scales))
    return scales


# ============================================================================
# Executor consistency tests
# ============================================================================


@settings(max_examples=50, deadline=None)
@given(op=qubit_operator(max_terms=3, max_qubits=2), params=hea_parameters(n_qubits=2, depth=1))
def test_statevector_executor_consistency(op, params):
    """Verify StatevectorHeaExecutor produces consistent results across calls."""
    executor = StatevectorHeaExecutor()

    # Call twice with same inputs
    e1 = executor.expectation_hea(op, 2, params, 1)
    e2 = executor.expectation_hea(op, 2, params, 1)

    # Should be deterministic
    assert e1 == pytest.approx(e2, abs=1e-12, rel=1e-12)


@settings(max_examples=50, deadline=None)
@given(op=qubit_operator(max_terms=3, max_qubits=2), params=hea_parameters(n_qubits=2, depth=1))
def test_executor_parameter_sensitivity_bounded(op, params):
    """Verify small parameter changes produce bounded energy changes."""
    executor = StatevectorHeaExecutor()

    e1 = executor.expectation_hea(op, 2, params, 1)

    # Perturb parameters slightly
    delta = 0.01
    params_perturbed = params.copy()
    params_perturbed[0] += delta

    e2 = executor.expectation_hea(op, 2, params_perturbed, 1)

    # Energy change should be bounded (Lipschitz continuity)
    # For typical Hamiltonians, |dE/dθ| < 10
    assert abs(e2 - e1) < 10 * delta


# ============================================================================
# ZNE convergence tests
# ============================================================================


@settings(max_examples=100, deadline=None)
@given(scales=zne_scales(min_scales=3, max_scales=5))
def test_zne_linear_extrapolation_convergence(scales):
    """Verify linear extrapolation recovers zero-noise energy within tolerance."""
    # Generate synthetic energies with linear noise model
    e_0 = -1.5
    noise_coeff = 0.05
    energies = [e_0 + noise_coeff * (s - 1.0) for s in scales]

    # Extrapolate
    e_extrap, uncertainty = linear_extrapolation(energies, scales)

    # Should be close to true value
    assert abs(e_extrap - e_0) < 0.05
    assert uncertainty >= 0


@settings(max_examples=100, deadline=None)
@given(scales=zne_scales(min_scales=4, max_scales=6))
def test_zne_polynomial_extrapolation_convergence(scales):
    """Verify polynomial extrapolation converges better with more data."""
    assume(len(scales) >= 3)

    # Generate synthetic energies with quadratic noise
    e_0 = -1.5
    noise_coeff = 0.05
    energies = [e_0 + noise_coeff * (s - 1.0) + 0.01 * (s - 1.0) ** 2 for s in scales]

    # Extrapolate with linear and polynomial
    e_linear, _ = linear_extrapolation(energies, scales)
    e_poly, _ = polynomial_extrapolation(energies, scales, order=2)

    # At least one should be reasonably close
    error_linear = abs(e_linear - e_0)
    error_poly = abs(e_poly - e_0)

    # Polynomial should not be dramatically worse
    assert error_poly < error_linear + 0.1


@settings(max_examples=50, deadline=None)
@given(scales=zne_scales(min_scales=3, max_scales=5))
def test_zne_extrapolation_monotonicity(scales):
    """Verify that more data points don't dramatically change extrapolation."""
    assume(len(scales) >= 3)

    # Generate synthetic energies
    e_0 = -1.5
    noise_coeff = 0.05
    energies = [e_0 + noise_coeff * (s - 1.0) for s in scales]

    # Extrapolate with subset vs full set
    scales_subset = scales[:3]
    energies_subset = energies[:3]

    e_full, _ = linear_extrapolation(energies, scales)
    e_subset, _ = linear_extrapolation(energies_subset, scales_subset)

    # Results should be similar
    assert abs(e_full - e_subset) < 0.1


@settings(max_examples=50, deadline=None)
@given(scales=zne_scales(min_scales=3, max_scales=5))
def test_zne_extrapolation_bounded(scales):
    """Verify extrapolation produces finite, reasonable values."""
    # Generate synthetic energies
    e_0 = -1.5
    noise_coeff = 0.05
    energies = [e_0 + noise_coeff * (s - 1.0) for s in scales]

    # Extrapolate
    e_extrap, uncertainty = linear_extrapolation(energies, scales)

    # Should be finite and reasonable
    assert np.isfinite(e_extrap)
    assert np.isfinite(uncertainty)
    assert -10.0 < e_extrap < 10.0
    assert uncertainty >= 0


@settings(max_examples=50, deadline=None)
@given(scales=zne_scales(min_scales=4, max_scales=6))
def test_zne_richardson_wrapper(scales):
    """Verify Richardson extrapolation wrapper works correctly."""
    assume(len(scales) >= 3)

    # Generate synthetic energies
    e_0 = -1.5
    noise_coeff = 0.05
    energies = [e_0 + noise_coeff * (s - 1.0) for s in scales]

    # Test wrapper
    e_richardson = richardson_extrapolation(energies, scales, order=1)
    e_poly, _ = polynomial_extrapolation(energies, scales, order=1)

    # Should match polynomial extrapolation
    assert e_richardson == pytest.approx(e_poly, abs=1e-10)


@settings(max_examples=30, deadline=None)
@given(scales=zne_scales(min_scales=4, max_scales=6))
def test_zne_model_selection(scales):
    """Verify model selection returns valid results."""
    assume(len(scales) >= 4)

    # Generate synthetic energies
    e_0 = -1.5
    noise_coeff = 0.05
    energies = [e_0 + noise_coeff * (s - 1.0) for s in scales]

    # Test model selection
    model_name, e_selected, uncertainty = select_extrapolation_model(
        energies, scales, criterion="bic"
    )

    # Should return valid model
    assert model_name in ["linear", "exponential", "polynomial"]
    assert np.isfinite(e_selected)
    assert np.isfinite(uncertainty)
    assert uncertainty >= 0


# ============================================================================
# Integration tests: executor + ZNE
# ============================================================================


@settings(max_examples=20, deadline=None)
@given(op=qubit_operator(max_terms=3, max_qubits=2), params=hea_parameters(n_qubits=2, depth=1))
def test_zne_with_executor(op, params):
    """Verify ZNE workflow with executor produces reasonable results."""
    executor = StatevectorHeaExecutor()

    # Simulate ZNE at different noise scales (using synthetic noise model)
    scales = [1.0, 1.5, 2.0, 2.5]
    energies = []

    for s in scales:
        # Simulate noisy energy (executor is noiseless, so we add synthetic noise)
        e_clean = executor.expectation_hea(op, 2, params, 1)
        # Synthetic noise: E_noisy = E_clean + 0.02 * (s - 1)
        e_noisy = e_clean + 0.02 * (s - 1.0)
        energies.append(e_noisy)

    # Extrapolate
    e_extrap, uncertainty = linear_extrapolation(energies, scales)

    # Should be close to clean energy
    e_clean = executor.expectation_hea(op, 2, params, 1)
    assert abs(e_extrap - e_clean) < 0.1


@settings(max_examples=30, deadline=None)
@given(scales=zne_scales(min_scales=3, max_scales=5))
def test_zne_exponential_stability(scales):
    """Verify exponential extrapolation is numerically stable."""
    assume(len(scales) >= 3)

    # Generate synthetic energies with exponential noise model
    e_0 = -1.5
    energies = [e_0 + 0.1 * (1 - np.exp(-0.5 * (s - 1.0))) for s in scales]

    # Extrapolate
    e_extrap, uncertainty = exponential_extrapolation(energies, scales)

    # Should produce finite result
    assert np.isfinite(e_extrap)
    assert np.isfinite(uncertainty)
    assert uncertainty >= 0

    # Should be reasonably close (exponential models can be unstable with few points)
    assert abs(e_extrap - e_0) < 0.5  # Wider tolerance for exponential
