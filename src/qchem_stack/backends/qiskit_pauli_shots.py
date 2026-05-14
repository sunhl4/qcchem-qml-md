"""
Grouped Pauli measurements via Qiskit ``Backend.run`` + shot *bitstrings* (Aer or hardware).

This is the public-stack analogue of a device / sampler histogram path: :func:`get_counts` feeds
the same per-group energy recombination as :mod:`qchem_stack.backends.pauli_shot_sim`, but
probabilities come from empirical frequencies instead of a statevector.
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.pauli_grouping import PauliMeasurementPlan
from qchem_stack.backends.pauli_measure_expand import deserialize_basis_key
from qchem_stack.backends.pauli_shot_sim import _pauli_eigenvalue_on_comp_bit
from qchem_stack.backends.qiskit_executor import hea_circuit_qiskit
from qchem_stack.backends.spec import BackendSpec


def _basis_key_for_term(term: tuple[tuple[int, str], ...]) -> tuple[tuple[int, str], ...]:
    return tuple(sorted(((int(q), str(p)) for q, p in term), key=lambda x: x[0]))


def _bit_reverse_n(value: int, n_qubits: int) -> int:
    """Reverse the ``n_qubits`` low bits (maps Qiskit wire-0-LSB index ↔ OpenFermion tensor axis-0-LSB)."""
    t = int(value) & ((1 << n_qubits) - 1)
    r = 0
    for _ in range(n_qubits):
        r = (r << 1) | (t & 1)
        t >>= 1
    return r


def qiskit_bitstring_to_comp_index(bitstr: str, n_qubits: int) -> int:
    """
    Map a Qiskit ``get_counts`` key to OpenFermion / ``hea_state`` computational index
    (logical qubit ``q`` as LSB: ``(comp_index >> q) & 1``).

    :func:`hea_circuit_qiskit` places logical qubit ``q`` on **physical** wire ``n-1-q`` (Qiskit
    labels wires ``0..n-1`` with qubit-0 = LSB of the *simulator* index). A measurement bitstring
    ``s`` (MSB = physical ``n-1``) has integer `K = int(s,2)` in wire order; the tensor / OF index is
    ``bit_reverse_n(K, n_qubits)`` (this stack's basis convention matches
    :func:`~qchem_stack.backends.pauli_shot_sim._pauli_eigenvalue_on_comp_bit`).
    """
    s = str(bitstr).replace(" ", "")
    s = s.split("|")[-1].strip() if "|" in s else s
    if s.startswith("0x") or s.startswith("0X"):
        k = int(s, 16) & ((1 << n_qubits) - 1)
        return _bit_reverse_n(k, n_qubits)
    s2 = s.zfill(n_qubits)[-n_qubits:]
    if not all(c in "01" for c in s2):
        raise ValueError(f"invalid Qiskit bitstring: {bitstr!r}")
    k = int(s2, 2)
    return _bit_reverse_n(k, n_qubits)


def _append_pauli_basis_to_qiskit(
    qc: Any, basis_key: tuple[tuple[int, str], ...], n_qubits: int
) -> None:
    """Apply the same single-qubit Cliffords as ``basis_change_operations`` on the ``hea_circuit_qiskit`` wire map ``w(q)=n-1-q``."""

    def w(q: int) -> int:
        return n_qubits - 1 - q

    axis = ["I"] * n_qubits
    for idx, p in basis_key:
        if p not in ("X", "Y", "Z", "I"):
            raise ValueError(f"Unknown Pauli axis {p!r}")
        axis[int(idx)] = p
    for q in range(n_qubits):
        p = axis[q]
        if p in ("I", "Z"):
            continue
        ww = w(q)
        if p == "X":
            qc.h(ww)
        else:  # Y
            qc.sdg(ww)
            qc.h(ww)


def _resolve_shot_backend(spec: BackendSpec) -> Any:
    """Return a Qiskit :class:`~qiskit.providers.Backend` (Aer by default from ``spec.meta``)."""
    try:
        import qiskit  # noqa: F401
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "Qiskit Pauli shots require qiskit. Install: pip install qchem-stack[quantum]"
        ) from e
    meta = spec.meta or {}
    b = meta.get("qiskit_shots_backend")
    if b is not None and not isinstance(b, str):
        if hasattr(b, "run"):
            return b
        raise TypeError("qiskit_shots_backend must be a str name or a Qiskit Backend with .run()")
    name = (b or "aer").lower()
    if name in ("aer", "aer_simulator", "aer_statevector", "qasm", "qasm_simulator"):
        try:
            from qiskit_aer import AerSimulator
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "Aer is required for default Qiskit shots. Install: pip install qiskit-aer"
            ) from e
        method = meta.get("aer_method", "automatic")
        return AerSimulator(method=method)
    raise ValueError(
        f"Unknown qiskit_shots_backend name {name!r}. "
        "Use 'aer' / 'aer_simulator', or pass a Backend instance in backend.meta['qiskit_shots_backend']."
    )


def _run_counts(
    qc: Any,
    *,
    shots: int,
    seed: int,
    backend: Any,
    transpile_level: int,
) -> dict[str, int]:
    from qiskit import transpile

    tqc = transpile(qc, backend=backend, optimization_level=int(transpile_level))
    try:
        job = backend.run(
            tqc,
            shots=int(shots),
            seed_transpiler=seed,
            seed_simulator=seed,
        )
    except TypeError:
        # IBM / some non-Aer backends ignore seed_* kwargs
        job = backend.run(tqc, shots=int(shots))
    return dict(job.result().get_counts())


def energy_estimate_grouped_qiskit_shots(
    hamiltonian: QubitOperator,
    plan: PauliMeasurementPlan,
    n_qubits: int,
    hea_depth: int,
    angles: np.ndarray,
    shots_per_circuit: int,
    spec: BackendSpec,
    rng: np.random.Generator,
    *,
    return_histograms: bool = True,
) -> tuple[float, float, dict[str, Any]]:
    """
    Energy from grouped Pauli readouts, each group executed as **HEA + basis + measure** on Qiskit.

    * Commuting groups with a synthesized ``basis_key``: one circuit, ``shots`` bitstrings.
    * ``greedy_commuting`` with ``basis_key is None``: one circuit **per Pauli term** in that
      group (same fallback structure as :func:`~qchem_stack.backends.pauli_shot_sim.energy_estimate_grouped_shot_simulation`).

    Returns ``(mean_energy, stderr, meta)``. Stderr is a sum of per-(sub)circuit **shot noise**
    contributions (independent groups approximation, same family as the statevector shot sim).
    """
    terms_dict = {k: float(np.real(v)) for k, v in dict(hamiltonian.terms).items()}
    ident = float(terms_dict.get((), 0.0))
    metas = plan.to_circuit_metas()
    group_means: list[float] = []
    per_group_var_over_shots: list[float] = []
    total_shots_used = 0
    histogram_rows: list[dict[str, Any]] = []
    qiskit_counts_log: list[dict[str, Any]] = []
    meta_in = spec.meta or {}
    transpile_level = int(meta_in.get("qiskit_transpile_optimization", 0))
    backend = _resolve_shot_backend(spec)
    angles = np.asarray(angles, dtype=float).ravel()

    for gid, g in enumerate(plan.groups):
        cmeta = metas[gid] if gid < len(metas) else {}
        bk = deserialize_basis_key(cmeta.get("basis_key"))
        coeffs = [(t, float(terms_dict[t])) for t in g if t in terms_dict]
        if not coeffs:
            continue
        seed = int(rng.integers(0, 2**31 - 1))

        if bk is None:
            sub_shots = max(1, shots_per_circuit // max(1, len(coeffs)))
            mean_sum = 0.0
            var_sum = 0.0
            for t, c in coeffs:
                bk1 = _basis_key_for_term(t)
                qc = hea_circuit_qiskit(n_qubits, hea_depth, angles)
                _append_pauli_basis_to_qiskit(qc, bk1, n_qubits)
                qc.barrier()
                qc.measure_all()
                counts = _run_counts(
                    qc, shots=sub_shots, seed=seed, backend=backend, transpile_level=transpile_level
                )
                idx_to_v: dict[int, int] = {}
                for bitstr, num in counts.items():
                    j = qiskit_bitstring_to_comp_index(str(bitstr), n_qubits)
                    idx_to_v[j] = idx_to_v.get(j, 0) + int(num)
                sshots = int(sum(idx_to_v.values())) or 1
                p_comp: dict[int, float] = {k: v / sshots for k, v in idx_to_v.items()}
                ev_one = 0.0
                e2 = 0.0
                for bidx, p in p_comp.items():
                    lam = c * _pauli_eigenvalue_on_comp_bit(t, bidx, n_qubits, bk1)
                    ev_one += p * float(lam)
                    e2 += p * (float(lam) ** 2)
                vdraw = e2 - ev_one**2
                vmean = (vdraw / sshots) if sshots > 0 else 0.0
                mean_sum += ev_one
                var_sum += vmean
                if return_histograms:
                    histogram_rows.append(
                        {
                            "group_id": gid,
                            "mode": "greedy_sequential_term",
                            "pauli_term": str(t),
                            "source": "qiskit_shot_counts",
                            "histogram_comp_index": {str(k): int(v) for k, v in idx_to_v.items()},
                        }
                    )
                qiskit_counts_log.append(
                    {
                        "group_id": gid,
                        "mode": "greedy_sequential_term",
                        "pauli_term": str(t),
                        "raw_qiskit_counts": {str(k): int(v) for k, v in counts.items()},
                        "shots": int(sshots),
                    }
                )
            total_shots_used += len(coeffs) * sub_shots
            group_means.append(mean_sum)
            per_group_var_over_shots.append(var_sum)
            continue

        qc = hea_circuit_qiskit(n_qubits, hea_depth, angles)
        _append_pauli_basis_to_qiskit(qc, bk, n_qubits)
        qc.barrier()
        qc.measure_all()
        counts = _run_counts(
            qc, shots=shots_per_circuit, seed=seed, backend=backend, transpile_level=transpile_level
        )
        idx_to_v: dict[int, int] = {}
        for bitstr, num in counts.items():
            j = qiskit_bitstring_to_comp_index(str(bitstr), n_qubits)
            idx_to_v[j] = idx_to_v.get(j, 0) + int(num)
        sshots = int(sum(idx_to_v.values())) or 1
        p_comp = {k: v / sshots for k, v in idx_to_v.items()}
        ev = 0.0
        e2 = 0.0
        for bidx, p in p_comp.items():
            vshot = 0.0
            for t, c in coeffs:
                vshot += c * _pauli_eigenvalue_on_comp_bit(t, bidx, n_qubits, bk)
            vshot = float(vshot)
            ev += p * vshot
            e2 += p * (vshot**2)
        vdraw = max(0.0, e2 - ev**2)
        stderr_one = (vdraw / sshots) if sshots > 1 else 0.0
        group_means.append(ev)
        per_group_var_over_shots.append(stderr_one)
        total_shots_used += shots_per_circuit
        if return_histograms:
            histogram_rows.append(
                {
                    "group_id": gid,
                    "mode": "commuting_group",
                    "source": "qiskit_shot_counts",
                    "histogram_comp_index": {str(k): int(v) for k, v in idx_to_v.items()},
                }
            )
        qiskit_counts_log.append(
            {
                "group_id": gid,
                "mode": "commuting_group",
                "raw_qiskit_counts": {str(k): int(v) for k, v in counts.items()},
                "shots": int(sshots),
            }
        )

    mean_e = ident + float(sum(group_means))
    stderr = math.sqrt(sum(per_group_var_over_shots)) if per_group_var_over_shots else 0.0
    meta_out: dict[str, Any] = {
        "identity_coeff": ident,
        "n_groups": len(group_means),
        "shot_noise_model": "qiskit_get_counts_empirical",
        "total_shots_used": int(total_shots_used),
        "qiskit_counts_per_group": qiskit_counts_log,
    }
    if return_histograms:
        meta_out["measurement_histogram_rows"] = histogram_rows
    return float(mean_e), float(stderr), meta_out
