#!/usr/bin/env python3
"""Compare VQE / energy-estimate behaviour for different ``shots_per_circuit`` values.

Uses the same single-circuit Z-measurement path as ``UQCCloudHeaExecutor``
(HEA → measure all qubits → ``compute_hamiltonian_expectation_from_counts``),
with Qiskit Aer locally so we can sweep shots without hundreds of cloud jobs.

Optional ``--uqc-real``: one fixed-angle cloud submission per shots setting
(requires intranet + ``UQC_API_TOKEN``).
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]


def _load_h2_hamiltonian():
    from qchem_stack.chem.pre_quantum_build import build_pre_quantum_input_with_context
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.scf_stage import run_scf_reference

    cfg = load_experiment_config(REPO / "configs" / "example_h2_uqc_cloud_sim_md_ml.yaml")
    rhf = run_scf_reference(cfg)
    pre_q_input, _schmidt = build_pre_quantum_input_with_context(cfg, rhf, cfg_path=None)
    qh = pre_q_input.qubit_hamiltonian
    rs = {"n_pauli_terms": len(qh.operator.terms), "n_qubits": qh.n_qubits}
    return cfg, qh, rs


def _exact_energy(qh, angles: np.ndarray, depth: int) -> float:
    from qchem_stack.backends.qiskit_executor import QiskitStatevectorHeaExecutor

    exe = QiskitStatevectorHeaExecutor()
    return float(exe.expectation_hea(qh.operator, qh.n_qubits, angles, depth))


def _shot_energy_aer(qh, angles: np.ndarray, depth: int, shots: int, seed: int) -> float:
    """Mirror UQC: transpile HEA, measure all, histogram → H expectation."""
    from qiskit import QuantumCircuit
    from qiskit_aer import AerSimulator

    from qchem_stack.backends.qiskit_executor import hea_circuit_qiskit
    from qchem_stack.backends.uqc_pauli_measurement import (
        compute_hamiltonian_expectation_from_counts,
    )
    from qchem_stack.backends.uqc_transpiler import transpile_to_uqc_native

    qc = hea_circuit_qiskit(qh.n_qubits, depth, np.asarray(angles, dtype=float))
    qc_t = transpile_to_uqc_native(qc, optimization_level=2)
    qc_meas = QuantumCircuit(qc_t.num_qubits, qc_t.num_qubits)
    qc_meas.compose(qc_t, inplace=True)
    qc_meas.barrier()
    qc_meas.measure(range(qc_t.num_qubits), range(qc_t.num_qubits))

    sim = AerSimulator()
    result = sim.run(qc_meas, shots=int(shots), seed_simulator=int(seed)).result()
    counts = result.get_counts()
    # Aer bitstrings are MSB-left; keep as returned.
    return float(compute_hamiltonian_expectation_from_counts(counts, qh.operator, qh.n_qubits))


class AerUqcLikeExecutor:
    def __init__(self, shots: int, seed: int) -> None:
        self.shots = int(shots)
        self.seed = int(seed)
        self.n_calls = 0

    def expectation_hea(self, hamiltonian, n_qubits, angles, hea_depth):
        self.n_calls += 1
        from qchem_stack.chem.hamiltonian import QubitHamiltonian

        qh = QubitHamiltonian(operator=hamiltonian, n_qubits=n_qubits, meta={})
        return _shot_energy_aer(
            qh, np.asarray(angles, dtype=float), hea_depth, self.shots, self.seed + self.n_calls
        )


def _noise_sweep(qh, depth: int, shots_list: list[int], n_repeats: int, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    angles = rng.uniform(-np.pi, np.pi, size=2 * qh.n_qubits * depth)
    exact = _exact_energy(qh, angles, depth)
    out: dict[str, object] = {"reference_angles": angles.tolist(), "exact_energy_hartree": exact}
    for shots in shots_list:
        samples = [
            _shot_energy_aer(qh, angles, depth, shots, seed + 1000 * shots + i)
            for i in range(n_repeats)
        ]
        deltas = [s - exact for s in samples]
        out[str(shots)] = {
            "shots_per_circuit": shots,
            "n_repeats": n_repeats,
            "mean_energy_hartree": statistics.mean(samples),
            "std_energy_hartree": statistics.pstdev(samples) if len(samples) > 1 else 0.0,
            "mean_abs_error_hartree": statistics.mean(abs(d) for d in deltas),
            "max_abs_error_hartree": max(abs(d) for d in deltas),
            "samples_hartree": samples,
        }
    return out


def _vqe_sweep(qh, cfg, shots_list: list[int], n_trials: int, seed: int) -> dict:
    from qchem_stack.config.quantum_resolvers import resolve_vqe_maxiter
    from qchem_stack.quantum.algorithms.vqe import VQE

    depth = int(cfg.quantum.vqe.depth)
    maxiter = int(resolve_vqe_maxiter(cfg))
    exact = _exact_energy(
        qh,
        np.random.default_rng(seed).uniform(-np.pi, np.pi, 2 * qh.n_qubits * depth),
        depth,
    )
    del exact
    fci = -1.1372759436170443
    out: dict[str, object] = {
        "vqe_depth": depth,
        "vqe_maxiter": maxiter,
        "fci_reference_hartree": fci,
    }
    for shots in shots_list:
        trials = []
        for t in range(n_trials):
            exe = AerUqcLikeExecutor(shots=shots, seed=seed + 10000 * shots + t * 17)
            vqe = VQE(qh, depth=depth, executor=exe, optimizer_method="COBYLA")
            vqe.build()
            res = vqe.run(maxiter=maxiter, seed=seed + t)
            trials.append(
                {
                    "trial": t,
                    "energy_hartree": float(res.energy),
                    "nfev": int(res.nfev),
                    "n_uqc_like_calls": exe.n_calls,
                    "error_vs_fci_hartree": float(res.energy - fci),
                }
            )
        energies = [tr["energy_hartree"] for tr in trials]
        out[str(shots)] = {
            "shots_per_circuit": shots,
            "n_trials": n_trials,
            "mean_final_energy_hartree": statistics.mean(energies),
            "std_final_energy_hartree": statistics.pstdev(energies) if len(energies) > 1 else 0.0,
            "total_shots_per_trial_approx": trials[0]["nfev"] * shots,
            "trials": trials,
        }
    return out


def _uqc_real_single(qh, angles: np.ndarray, depth: int, shots: int) -> float:
    from qchem_stack.backends.spec import BackendSpec
    from qchem_stack.backends.uqc_env import load_repo_dotenv
    from qchem_stack.backends.uqc_executor import UQCCloudHeaExecutor

    load_repo_dotenv()
    spec = BackendSpec(
        name="uqc-iontrap-sim",
        provider="uqc",
        shots_per_circuit=shots,
        uqc_mode="real",
        meta={
            "uqc_target": "iontrap-sim",
            "uqc_allow_fallback": False,
            "uqc_timeout_s": 600.0,
            "uqc_poll_interval_s": 2.0,
        },
    )
    exe = UQCCloudHeaExecutor(spec)
    return float(exe.expectation_hea(qh.operator, qh.n_qubits, angles, depth))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shots", type=int, nargs="+", default=[100, 500, 1000])
    ap.add_argument("--noise-repeats", type=int, default=30)
    ap.add_argument("--vqe-trials", type=int, default=3)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument(
        "--output", type=Path, default=REPO / "results" / "shots_per_circuit_comparison.json"
    )
    ap.add_argument(
        "--uqc-real", action="store_true", help="Also run 1 cloud eval per shots (slow)"
    )
    args = ap.parse_args()

    cfg, qh, rs = _load_h2_hamiltonian()
    depth = int(cfg.quantum.vqe.depth)
    summary = {
        "experiment": "example_h2_uqc_cloud_sim_md_ml",
        "n_qubits": qh.n_qubits,
        "n_pauli_terms": rs.get("n_pauli_terms"),
        "n_pauli_groups": rs.get("n_pauli_groups"),
        "measurement_path": "uqc_like_single_z_circuit",
        "shots_tested": args.shots,
        "fixed_angle_noise_sweep": _noise_sweep(
            qh, depth, args.shots, args.noise_repeats, args.seed
        ),
        "vqe_trials_sweep": _vqe_sweep(qh, cfg, args.shots, args.vqe_trials, args.seed),
    }
    if args.uqc_real:
        angles = np.asarray(summary["fixed_angle_noise_sweep"]["reference_angles"], dtype=float)
        exact = float(summary["fixed_angle_noise_sweep"]["exact_energy_hartree"])
        cloud = {}
        for shots in args.shots:
            e = _uqc_real_single(qh, angles, depth, shots)
            cloud[str(shots)] = {
                "shots_per_circuit": shots,
                "energy_hartree": e,
                "error_vs_exact_hartree": e - exact,
            }
        summary["uqc_cloud_single_eval"] = cloud

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                k: summary[k]
                for k in summary
                if k.endswith("_sweep") or k == "uqc_cloud_single_eval"
            },
            indent=2,
        )
    )
    print(f"\nWrote {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
