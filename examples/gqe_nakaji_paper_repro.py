#!/usr/bin/env python3
"""Reproduce Nakaji et al. GPT-QE numerical experiments (arXiv:2401.09253).

Default: H2 smoke at one bond length (paper-faithful pool/loss/loop, reduced epochs).
Full paper runs are opt-in via --full / molecule flags (CPU-heavy for LiH/BeH2/N2).

Usage:
  pip install -e '.[chem,gqe]'
  python examples/gqe_nakaji_paper_repro.py --molecule h2 --bond 0.74 --epochs 30
  python examples/gqe_nakaji_paper_repro.py --checklist
  python examples/gqe_nakaji_paper_repro.py --molecule h2 --scan --epochs 20 --samples 20
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Nakaji GPT-QE paper reproduction")
    parser.add_argument("--molecule", choices=("h2", "lih", "beh2", "n2"), default="h2")
    parser.add_argument("--bond", type=float, default=0.74, help="Bond length in Å")
    parser.add_argument("--scan", action="store_true", help="Scan paper bond-length grid")
    parser.add_argument("--epochs", type=int, default=None, help="Override paper epoch count")
    parser.add_argument("--samples", type=int, default=None, help="N_sample per epoch")
    parser.add_argument("--seq-len", type=int, default=None)
    parser.add_argument("--loss", choices=("lm", "grpo"), default="grpo")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--d-model", type=int, default=64, help="Default reduced vs paper 192")
    parser.add_argument("--n-layers", type=int, default=2, help="Default reduced vs paper 6")
    parser.add_argument(
        "--paper-model",
        action="store_true",
        help="Use paper transformer size (d_model=192, n_layers=6)",
    )
    parser.add_argument("--warmup", type=int, default=None, help="Warmup oracle count (paper=200)")
    parser.add_argument("--buffer", type=int, default=None)
    parser.add_argument("--batch", type=int, default=None)
    parser.add_argument("--n-iter", type=int, default=None)
    parser.add_argument(
        "--train-mode",
        choices=("gpt", "prefill", "condition"),
        default="gpt",
        help="gpt=warmup+GPT; prefill=warmup-only; condition=instance-conditioned GPT",
    )
    parser.add_argument(
        "--condition-bonds",
        type=float,
        nargs="*",
        default=None,
        help="Bond lengths (Å) for --train-mode condition",
    )
    parser.add_argument("--checklist", action="store_true")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument(
        "--checkpoint-dir",
        type=Path,
        default=None,
        help="Write progress JSON every --checkpoint-every epochs (survives TIMEOUT)",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=0,
        help="Epoch interval for checkpoints (default 25 if --checkpoint-dir set)",
    )
    parser.add_argument("--log-every", type=int, default=1, help="Print every N epochs")
    args = parser.parse_args()

    from qchem_stack.integrations.gqe.native.paper_spec import (
        PAPER_BOND_LENGTHS_ANG,
        PAPER_MOLECULES,
        paper_reproduction_checklist,
    )

    if args.checklist:
        print(json.dumps(paper_reproduction_checklist(), indent=2))
        return 0

    from qchem_stack.config import load_experiment_config
    from qchem_stack.integrations.gqe import run_gqe_from_config
    from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation

    mol = args.molecule
    spec = PAPER_MOLECULES[mol]
    bonds = list(PAPER_BOND_LENGTHS_ANG[mol]) if args.scan else [float(args.bond)]
    d_model = 192 if args.paper_model else args.d_model
    n_layers = 6 if args.paper_model else args.n_layers
    epochs = int(args.epochs) if args.epochs is not None else min(30, spec.n_epochs)
    n_sample = int(args.samples) if args.samples is not None else 20
    seq_len = (
        int(args.seq_len)
        if args.seq_len is not None
        else min(spec.seq_len, 10 if mol == "h2" else spec.seq_len)
    )
    warmup = int(args.warmup) if args.warmup is not None else 200
    buffer = int(args.buffer) if args.buffer is not None else 1000
    batch = int(args.batch) if args.batch is not None else 50
    n_iter = int(args.n_iter) if args.n_iter is not None else 5
    if args.train_mode == "prefill":
        epochs = 0

    probe = probe_gqe_jax_installation()
    if not probe.get("available"):
        print("[paper-repro] jax/optax missing — pip install 'qchem-stack[gqe]'")
        return 1

    base_yaml = Path(__file__).resolve().parents[1] / "configs" / "example_h2_gqe_plan_b.yaml"
    results: list[dict] = []
    for r in bonds:
        print(
            f"[paper-repro] molecule={mol} R={r} Å train_mode={args.train_mode} "
            f"via run_gqe_from_config…"
        )
        gqe_update = {
            "enabled": True,
            "mode": "paper",
            "train_mode": args.train_mode,
            "molecule": mol,
            "bond_angstrom": float(r),
            "epochs": epochs,
            "n_sample": n_sample,
            "seq_len": seq_len,
            "loss": args.loss,
            "d_model": d_model,
            "n_layers": n_layers,
            "paper_model": bool(args.paper_model),
            "warmup_samples": warmup,
            "buffer_max": buffer,
            "n_batch": batch,
            "n_iter": n_iter,
            "seed": args.seed,
            "checkpoint_dir": str(args.checkpoint_dir) if args.checkpoint_dir else None,
            "checkpoint_every": int(args.checkpoint_every),
            "log_every": int(args.log_every),
            "skip_variational": True,
        }
        if args.train_mode == "condition":
            gqe_update["condition_bonds"] = (
                list(args.condition_bonds)
                if args.condition_bonds
                else list(PAPER_BOND_LENGTHS_ANG[mol][:3])
            )
            # condition mode trains across bonds in one call
            if len(bonds) > 1:
                print("[paper-repro] condition mode ignores --scan grid; using condition_bonds")
            experiment = load_experiment_config(base_yaml)
            experiment = experiment.model_copy(
                update={"gqe": experiment.gqe.model_copy(update=gqe_update)}
            )
            report = run_gqe_from_config(experiment, cfg_path=base_yaml)
            meta = report.get("bundle_meta") or {}
            ca = report.get("chemical_accuracy") or {}
            print(
                f"  vocab={meta.get('vocab_size')} bonds={meta.get('bonds')} "
                f"best_E={report.get('best_energy'):.8f} n_evals={report.get('n_energy_evals')}"
            )
            results.append({"train_mode": "condition", "train": report})
            break

        experiment = load_experiment_config(base_yaml)
        experiment = experiment.model_copy(
            update={"gqe": experiment.gqe.model_copy(update=gqe_update)}
        )
        report = run_gqe_from_config(experiment, cfg_path=base_yaml)
        meta = report.get("bundle_meta") or {}
        ca = report.get("chemical_accuracy") or {}
        print(
            f"  n_qubits={meta.get('n_qubits')} (paper expect {spec.n_qubits}) "
            f"vocab={meta.get('vocab_size')} scf={meta.get('scf_energy')} fci={meta.get('fci_energy')}"
        )
        print(
            f"  best_E={report.get('best_energy'):.8f} n_evals={report.get('n_energy_evals')} "
            f"abs_err={ca.get('abs_error_hartree')} within={ca.get('within_chemical_accuracy')}"
        )
        results.append(
            {
                "bond_angstrom": r,
                "train_mode": args.train_mode,
                "scf": meta.get("scf_energy"),
                "fci": meta.get("fci_energy"),
                "train": report,
            }
        )

    out = {
        "paper": "arXiv:2401.09253",
        "molecule": mol,
        "checklist": paper_reproduction_checklist(),
        "results": results,
    }
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(out, indent=2), encoding="utf-8")
        print(f"[paper-repro] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
