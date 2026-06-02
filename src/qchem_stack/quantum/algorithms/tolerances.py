"""Numerical tolerances for quantum algorithms.

This module defines named constants for numerical precision checks used throughout
the quantum algorithms package. Using named constants improves code readability
and makes it easier to adjust precision requirements globally.
"""

# Floating point precision for numerical stability
FLOAT_PRECISION_TINY = 1e-15  # For gradient norm, angle checks where we need near-zero detection

# Standard numerical tolerance for most quantum operations
NUMERICAL_TOLERANCE = 1e-14  # For matrix norms, coefficient magnitudes, imaginary part checks

# Gram-Schmidt orthogonalization tolerance
ORTHOGONALIZATION_TOLERANCE = 1e-10  # For Gram-Schmidt basis construction

# Statistical noise floor for shot-based estimation
SHOT_NOISE_FLOOR = 1e-6  # For statistical uncertainty lower bounds

# Probability floor for numerical stability
PROBABILITY_FLOOR = 1e-30  # For probability distributions to avoid log(0) or division by zero

# ADAPT-VQE default gradient convergence threshold
ADAPT_GRAD_TOLERANCE = 1e-2  # Default gradient tolerance for ADAPT convergence

# IQEB pool coefficient scaling and energy convergence
IQEB_POOL_COEFF_SCALE = 1e-4  # Scaling factor for pool operator addition
IQEB_ENERGY_TOLERANCE = 1e-8  # Energy convergence tolerance for IQEB rounds

# QITE gradient convergence threshold
QITE_GRAD_TOLERANCE = 1e-8  # Gradient norm threshold for QITE convergence

# Loose tolerance for convergence and regularization
CONVERGENCE_TOLERANCE = 1e-12  # For eigenvalue checks, delta norms, singular values

# Very loose tolerance for optimization and statistical regularization
OPTIMIZATION_TOLERANCE = 1e-9  # For ridge regularization, retention rates

# DMET self-consistency energy tolerance
DMET_ENERGY_TOLERANCE = 1e-5  # Energy convergence for DMET self-consistent loop

# Ridge regression regularization parameter
RIDGE_REGULARIZATION = 1e-3  # Default regularization strength for ridge regression

# Learning rate for gradient-based optimization
DEFAULT_LEARNING_RATE = 1e-3  # Default learning rate for training loops

# Finite difference step size for numerical derivatives
FINITE_DIFFERENCE_STEP = 1e-4  # Step size for finite difference approximations

# Projection embedding threshold
PROJECTION_THRESHOLD = 1e-8  # Threshold for projection embedding operations

# MO coefficient imaginary part tolerance
MO_IMAG_TOLERANCE = 1e-7  # Tolerance for imaginary parts in MO coefficients

# Schmidt decomposition residual tolerance
SCHMIDT_RESIDUAL_TOLERANCE = 1e-8  # Residual tolerance for Schmidt decomposition convergence

# BIC/AIC information criterion regularization
BIC_REGULARIZATION = 1e-12  # Regularization term for BIC/AIC calculations

# Schmidt orthonormalization singularity threshold
SCHMIDT_SINGULARITY_THRESHOLD = 1e-12  # Threshold for detecting singular overlap matrices
SCHMIDT_SINGULARITY_TOLERANCE = SCHMIDT_SINGULARITY_THRESHOLD  # Alias used by chem.embedding

# Chemistry module tolerances
LOWDIN_SINGULARITY_TOLERANCE = 1e-12  # Singularity threshold for Löwdin orthogonalization
MO_COEFFICIENT_TOLERANCE = 1e-14  # Threshold for near-zero MO coefficients
IMAGINARY_PART_TOLERANCE = 1e-14  # Threshold for imaginary parts in Hermitian matrices
ACTIVE_SPACE_IMAG_TOLERANCE = 1e-10  # Imaginary part tolerance for active space orbitals
ACTIVE_SPACE_IMAG_WARNING = 1e-7  # Warning threshold for large imaginary parts
SPIN_UCC_COMMUTATOR_TOLERANCE = 1e-9  # Tolerance for spin-UCC commutator checks
SCHMIDT_ORTHONORMALITY_TOLERANCE = (
    1e-8  # Tolerance for Schmidt impurity MO block orthonormality check
)
ONIOM_BOND_LENGTH_TOLERANCE = 1e-8  # Tolerance for ONIOM bond length detection
DMET_TRACE_TOLERANCE = 1e-14  # Tolerance for DMET density matrix trace normalization
PROJECTION_EMBEDDING_THRESHOLD = 1e-8  # Threshold for projection embedding operations
CUTOFF_ABS_INTEGRAL = 1e-14  # Absolute cutoff for near-zero integral coefficients

# Mitigation module tolerances
BIC_LOG_REGULARIZATION = 1e-12  # Regularization for log in BIC/AIC to avoid log(0)
RETENTION_RATE_MINIMUM = 1e-9  # Minimum retention rate for PMSV symmetry filtering

# Shot simulation tolerances
PROJECTION_NORM_TOLERANCE = 1e-14  # Tolerance for projection norm checks in shot simulation
STATE_NORMALIZATION_FLOOR = 1e-30  # Floor for state normalization to avoid division by zero

# Cost model parameters
UNIT_PER_SHOT = 1e-4  # Default cost unit per shot
UNIT_PER_DEPTH = 1e-3  # Default cost unit per circuit depth

# Determinant singularity tolerance
DETERMINANT_SINGULARITY_TOLERANCE = (
    1e-12  # Tolerance for detecting singular matrices via determinant
)

# Cell linear dependence tolerance
CELL_LINEAR_DEPENDENCE_TOLERANCE = (
    1e-12  # Tolerance for detecting linear dependence in cell vectors
)
