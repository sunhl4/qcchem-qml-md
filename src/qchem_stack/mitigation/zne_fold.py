"""ZNE circuit folding helpers."""

from __future__ import annotations

from typing import Any


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
