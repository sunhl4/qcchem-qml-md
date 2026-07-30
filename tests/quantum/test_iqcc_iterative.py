"""Unit tests for iterative iQCC dressing and EN2."""

from __future__ import annotations

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
from qchem_stack.quantum.algorithms.iqcc import (
    IQCCVQE,
    build_genin_style_entanglers,
    en2_correction,
)
from qchem_stack.quantum.algorithms.iqcc_dressing import (
    dress_by_pauli_rotation,
    truncate_qubit_operator,
)
from qchem_stack.quantum.variational_plugins.registry import list_registered_variational_ids


def test_iqcc_registered_as_variational_algorithm() -> None:
    assert "iqcc" in list_registered_variational_ids()
    assert "iqcc" in list_registered_algorithm_ids()


def test_dress_preserves_spectrum_on_2q() -> None:
    h = QubitOperator("Z0", 1.0) + QubitOperator("Z1", 0.5) + QubitOperator("X0 X1", 0.2)
    p = QubitOperator("Y0 X1", 1.0)
    dressed = dress_by_pauli_rotation(h, p, tau=0.3)
    from openfermion import get_sparse_operator

    e0 = np.linalg.eigvalsh(get_sparse_operator(h, n_qubits=2).toarray())
    e1 = np.linalg.eigvalsh(get_sparse_operator(dressed, n_qubits=2).toarray())
    np.testing.assert_allclose(sorted(e0), sorted(e1), atol=1e-8)


def test_truncate_drops_tiny_terms() -> None:
    op = QubitOperator("Z0", 1.0) + QubitOperator("X1", 1e-12)
    out = truncate_qubit_operator(op, coeff_atol=1e-10)
    assert len(out.terms) == 1


def test_genin_entanglers_have_single_y() -> None:
    gens = build_genin_style_entanglers(4, max_weight=4)
    assert gens
    for g in gens:
        term = next(iter(g.terms.keys()))
        ys = [p for _, p in term if p == "Y"]
        zs = [p for _, p in term if p == "Z"]
        assert len(ys) == 1
        assert not zs
        assert len(term) % 2 == 0


def test_iqcc_h2_like_toy_lowers_or_matches_hf() -> None:
    # Minimal 2-qubit Ising-like problem with HF |00>.
    h = (
        QubitOperator((), -1.0)
        + QubitOperator("Z0", 0.4)
        + QubitOperator("Z1", 0.4)
        + QubitOperator("X0 X1", 0.2)
    )
    qh = QubitHamiltonian(operator=h, n_qubits=2, fermion_space=None)
    algo = IQCCVQE(
        qh,
        max_steps=2,
        top_k=1,
        enable_pt=False,
        pool_mode="genin_dis",
        max_weight=2,
        maxiter_inner=40,
    )
    from qchem_stack.quantum.algorithms.iqcc_dressing import reference_pauli_expectation

    ref = np.zeros(4, dtype=complex)
    ref[0] = 1.0
    e_hf = reference_pauli_expectation(h, ref, 2)
    out = algo.run(seed=0)
    assert out.energy <= e_hf + 1e-6
    assert out.meta["n_terms_final"] >= 1


def test_en2_finite_on_unused_pool() -> None:
    h = QubitOperator("Z0", 1.0) + QubitOperator("X0 X1", 0.1)
    ref = np.zeros(4, dtype=complex)
    ref[0] = 1.0
    gens = build_genin_style_entanglers(2, max_weight=2)
    delta, rows = en2_correction(h, generators=gens, reference=ref, n_qubits=2, denom_cutoff=1e-8)
    assert np.isfinite(delta)
    assert rows
