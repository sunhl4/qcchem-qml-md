#!/usr/bin/env python3
"""Additive GQE Plan-B demo on H2 (no pipeline.py changes).

Usage:
  pip install -e '.[chem,gqe]'
  python examples/gqe_h2_plan_b_demo.py
  python examples/gqe_h2_plan_b_demo.py --loss grpo
  python examples/gqe_h2_plan_b_demo.py --chem-accuracy --seq-len 8 --epochs 20 --samples 16
  python examples/gqe_h2_plan_b_demo.py --bond-scan --pretrain-epochs 5
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Native GQE Plan B demo (H2)")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("configs/example_h2_gqe_plan_b.yaml"),
        help="Experiment YAML (chem active-space); GQE knobs via CLI",
    )
    parser.add_argument("--pool-id", default="fermionic_uccsd")
    parser.add_argument("--seq-len", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--samples", type=int, default=8)
    parser.add_argument("--loss", choices=("lm", "grpo"), default="lm")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--baseline-only", action="store_true")
    parser.add_argument(
        "--beta-schedule",
        choices=("none", "constant", "linear", "exponential"),
        default="linear",
        help="β annealing (Nakaji: small → large). 'none' uses fixed --beta.",
    )
    parser.add_argument("--beta", type=float, default=5.0)
    parser.add_argument("--beta-start", type=float, default=1.0)
    parser.add_argument("--beta-end", type=float, default=20.0)
    parser.add_argument(
        "--chem-accuracy",
        action="store_true",
        help="Compute FCI reference and report chemical-accuracy metrics",
    )
    parser.add_argument(
        "--bond-scan",
        action="store_true",
        help="Multi-geometry: sample at R=1.2/1.4/1.6, reweight to target R=1.4, pretrain",
    )
    parser.add_argument("--pretrain-epochs", type=int, default=0)
    parser.add_argument(
        "--angle-grid",
        type=str,
        default="chem",
        help="Comma-separated angles, 'chem' (±0.05..0.3 + id), or 'single' (default_angle only)",
    )
    parser.add_argument("--out", type=Path, default=None, help="Optional JSON report path")
    args = parser.parse_args()

    from qchem_stack.integrations.gqe.native import (
        BetaSchedule,
        GQETrainConfig,
        build_gqe_problem_from_config,
        build_gqe_problems_bond_scan,
        run_gqe_lm_loop,
        run_random_baseline,
        transfer_dataset_to_bundle,
    )
    from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation

    if args.angle_grid == "chem":
        angle_grid: tuple[float, ...] | None = (
            -0.3,
            -0.2,
            -0.1,
            -0.05,
            0.05,
            0.1,
            0.2,
            0.3,
        )
    elif args.angle_grid == "single":
        angle_grid = None
    else:
        angle_grid = tuple(float(x) for x in args.angle_grid.split(",") if x.strip())

    compute_fci = bool(args.chem_accuracy)
    bundle = build_gqe_problem_from_config(
        args.config,
        pool_id=args.pool_id,
        default_angle=0.1,
        angle_grid=angle_grid,
        store_pauli_features=True,
        compute_fci=compute_fci,
    )
    print(
        f"[gqe] experiment={bundle.experiment_id} n_qubits={bundle.n_qubits} "
        f"n_electrons={bundle.n_electrons} pool={bundle.pool.pool_id} "
        f"vocab={bundle.pool.vocab_size}"
    )
    if bundle.scf_energy is not None:
        print(f"[gqe] scf_energy={bundle.scf_energy:.8f}")
    if bundle.fci_energy is not None:
        print(f"[gqe] fci_energy={bundle.fci_energy:.8f}")

    baseline = run_random_baseline(
        bundle.cost_fn,
        bundle.pool,
        seq_len=args.seq_len,
        n_samples=max(16, args.samples),
        seed=args.seed,
    )
    print(
        f"[gqe] random baseline best_E={baseline['best_energy']:.8f} "
        f"seq={baseline['best_sequence']}"
    )

    report: dict = {
        "baseline": baseline,
        "bundle_meta": bundle.meta,
        "scf_energy": bundle.scf_energy,
        "fci_energy": bundle.fci_energy,
    }

    pretrain_dataset = None
    if args.bond_scan:
        lengths = [1.2, 1.4, 1.6]
        print(f"[gqe] bond-scan geometries R={lengths} bohr → reweight to R=1.4")
        bundles = build_gqe_problems_bond_scan(
            args.config,
            bond_lengths_bohr=lengths,
            pool_id=args.pool_id,
            default_angle=0.1,
            angle_grid=angle_grid,
            store_pauli_features=True,
        )
        # Prefer the R=1.4 bundle as training target (matches default YAML)
        target = next(
            (b for b in bundles if abs(float(b.meta.get("bond_length_bohr", -1)) - 1.4) < 1e-9),
            bundles[1],
        )
        bundle = target
        report["bond_scan"] = {
            "lengths_bohr": lengths,
            "target_R": float(target.meta.get("bond_length_bohr", 1.4)),
            "n_geometries": len(bundles),
        }
        # Collect short random sequences at each geometry, then reweight to target H
        rng_records: list[dict] = []
        import numpy as np

        rng = np.random.default_rng(args.seed + 99)
        for b in bundles:
            for _ in range(max(4, args.samples // 2)):
                seq = rng.integers(0, b.pool.vocab_size, size=args.seq_len).tolist()
                rng_records.append(b.oracle_fn(seq))
        pretrain_dataset = transfer_dataset_to_bundle(rng_records, target)
        report["bond_scan"]["n_pretrain_records"] = len(pretrain_dataset)
        print(
            f"[gqe] collected {len(rng_records)} oracle records; "
            f"reweighted to target R={target.meta.get('bond_length_bohr')}"
        )
        if args.pretrain_epochs <= 0:
            args.pretrain_epochs = 5

    if not args.baseline_only:
        probe = probe_gqe_jax_installation()
        if not probe.get("available"):
            print("[gqe] jax/optax missing — skip trained loop. pip install 'qchem-stack[gqe]'")
            report["train"] = {"skipped": True, "probe": probe}
        else:
            beta_sched = None
            if args.beta_schedule != "none":
                beta_sched = BetaSchedule(
                    kind=args.beta_schedule,  # type: ignore[arg-type]
                    beta_start=args.beta_start,
                    beta_end=args.beta_end if args.beta_schedule != "constant" else args.beta,
                )
            result = run_gqe_lm_loop(
                bundle.cost_fn,
                bundle.pool,
                config=GQETrainConfig(
                    seq_len=args.seq_len,
                    n_epochs=args.epochs,
                    samples_per_epoch=args.samples,
                    loss_mode=args.loss,
                    seed=args.seed,
                    beta=args.beta,
                    beta_schedule=beta_sched,
                    replay_mix_fraction=0.25,
                    pretrain_epochs=args.pretrain_epochs,
                ),
                oracle_fn=bundle.oracle_fn,
                pretrain_dataset=pretrain_dataset,
                reference_energy=bundle.fci_energy if args.chem_accuracy else None,
                scf_energy=bundle.scf_energy,
            )
            print(
                f"[gqe] train({args.loss}) best_E={result.best_energy:.8f} "
                f"seq={result.best_sequence}"
            )
            for h in result.history:
                print(
                    f"  epoch={h['epoch']} β={h['beta']:.3f} T={h['temperature']:.4f} "
                    f"loss={h['loss']:.4e} minE={h['min_energy']:.8f} best={h['best_so_far']:.8f}"
                )
            ca = result.report.get("chemical_accuracy")
            if ca:
                print(
                    f"[gqe] vs FCI: abs_err={ca['abs_error_hartree']:.6e} Ha "
                    f"within_chem_acc={ca['within_chemical_accuracy']}"
                )
            report["train"] = result.report

    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"[gqe] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
