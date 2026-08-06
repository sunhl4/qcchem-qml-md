"""Computational-basis sampling helpers for SQD-family algorithms."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from qchem_stack.quantum.statevector import hea_state

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


def resolve_n_electrons(hamiltonian: QubitHamiltonian, override: int | None = None) -> int | None:
    if override is not None:
        return int(override)
    fs = hamiltonian.fermion_space
    if fs is None:
        return None
    return int(fs.n_electrons)


def hf_bitstring(n_qubits: int, n_electrons: int | None) -> int:
    """OpenFermion JW HF index: occupy lowest spin-orbitals (MSB = orbital 0)."""
    if n_electrons is None:
        return 0
    ne = max(0, min(int(n_electrons), n_qubits))
    idx = 0
    for i in range(ne):
        idx |= 1 << (n_qubits - 1 - i)
    return idx


def hf_state(n_qubits: int, n_electrons: int | None) -> np.ndarray:
    psi = np.zeros(2**n_qubits, dtype=np.complex128)
    psi[hf_bitstring(n_qubits, n_electrons)] = 1.0
    return psi


def sample_bitstrings_from_state(
    state: np.ndarray,
    *,
    n_shots: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Draw computational-basis indices from ``|amp|^2``."""
    from qchem_stack.quantum.algorithms.tolerances import STATE_NORMALIZATION_FLOOR

    psi = np.asarray(state, dtype=np.complex128).ravel()
    probs = np.abs(psi) ** 2
    s = float(probs.sum())
    if s < STATE_NORMALIZATION_FLOOR:
        raise ValueError("cannot sample from near-zero state")
    probs = probs / s
    return rng.choice(probs.size, size=int(n_shots), p=probs)


def prepare_hea_sampling_state(
    n_qubits: int,
    angles: np.ndarray,
    depth: int,
    *,
    n_electrons: int | None = None,
) -> np.ndarray:
    """Apply HEA unitaries on the HF reference when ``n_electrons`` is known.

    HEA+CNOT does not conserve particle number; callers should postselect with
    :func:`filter_particle_number` (QSCI-style) when a sector is required.
    """
    angles_arr = np.asarray(angles, dtype=float)
    if n_electrons is None:
        return hea_state(angles_arr, n_qubits, depth)
    return hea_state(
        angles_arr,
        n_qubits,
        depth,
        initial_state=hf_state(n_qubits, n_electrons),
    )


def default_hea_angles(n_qubits: int, depth: int, rng: np.random.Generator) -> np.ndarray:
    return rng.uniform(-0.15, 0.15, size=2 * n_qubits * depth)


def popcount(x: int) -> int:
    return int(bin(int(x)).count("1"))


def filter_particle_number(bitstrings: np.ndarray, n_electrons: int | None) -> np.ndarray:
    if n_electrons is None:
        return np.asarray(bitstrings, dtype=int)
    ne = int(n_electrons)
    return np.asarray([b for b in bitstrings if popcount(int(b)) == ne], dtype=int)


def top_k_unique(bitstrings: np.ndarray, k: int) -> list[int]:
    if bitstrings.size == 0:
        return []
    vals, counts = np.unique(np.asarray(bitstrings, dtype=int), return_counts=True)
    order = np.argsort(counts)[::-1]
    return [int(vals[i]) for i in order[: max(1, int(k))]]


def ensure_nonempty_basis(
    basis: list[int],
    *,
    n_qubits: int,
    n_electrons: int | None,
) -> tuple[list[int], bool]:
    """Fall back to HF determinant when sampling yields an empty support.

    Returns ``(basis, fallback_hf)``.
    """
    if basis:
        return list(basis), False
    return [hf_bitstring(n_qubits, n_electrons)], True


def select_sampled_basis(
    samples: np.ndarray,
    *,
    subspace_size: int,
    n_qubits: int,
    n_electrons: int | None,
) -> tuple[list[int], dict[str, object]]:
    """Ne-filter → top-k → HF fallback; return basis and postselect diagnostics."""
    raw = np.asarray(samples, dtype=int)
    filtered = filter_particle_number(raw, n_electrons)
    basis, fallback_hf = ensure_nonempty_basis(
        top_k_unique(filtered, subspace_size),
        n_qubits=n_qubits,
        n_electrons=n_electrons,
    )
    n_raw = int(raw.size)
    n_kept = int(filtered.size)
    frac = (float(n_kept) / float(n_raw)) if n_raw > 0 else 0.0
    return basis, {
        "n_raw_samples": n_raw,
        "n_kept_after_ne_filter": n_kept,
        "postselect_kept_fraction": frac,
        "fallback_hf": bool(fallback_hf),
    }


def particle_number_preserving_singles(bitstring: int, n_qubits: int) -> list[int]:
    """Classical singles: move one electron from occupied → virtual orbital."""
    b0 = int(bitstring)
    occ = [q for q in range(n_qubits) if (b0 >> (n_qubits - 1 - q)) & 1]
    virt = [q for q in range(n_qubits) if not ((b0 >> (n_qubits - 1 - q)) & 1)]
    out: list[int] = []
    for i in occ:
        for a in virt:
            out.append(b0 ^ (1 << (n_qubits - 1 - i)) ^ (1 << (n_qubits - 1 - a)))
    return out


def fragment_qubit_ranges(n_qubits: int, n_fragments: int) -> list[tuple[int, int]]:
    n_frag = max(1, min(int(n_fragments), n_qubits))
    frag_size = int(np.ceil(n_qubits / n_frag))
    ranges: list[tuple[int, int]] = []
    for f in range(n_frag):
        lo = f * frag_size
        hi = min(n_qubits, (f + 1) * frag_size)
        if lo < hi:
            ranges.append((lo, hi))
    return ranges


def overlapping_fragment_ranges(n_qubits: int, n_fragments: int) -> list[tuple[int, int]]:
    """Contiguous fragments with one-qubit overlap for QBE-lite bootstrap."""
    base = fragment_qubit_ranges(n_qubits, n_fragments)
    if len(base) <= 1:
        return base
    out: list[tuple[int, int]] = []
    for i, (lo, hi) in enumerate(base):
        if i == 0:
            out.append((lo, min(n_qubits, hi + 1)))
        elif i == len(base) - 1:
            out.append((max(0, lo - 1), hi))
        else:
            out.append((max(0, lo - 1), min(n_qubits, hi + 1)))
    return out
