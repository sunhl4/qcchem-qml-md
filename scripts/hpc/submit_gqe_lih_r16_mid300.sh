#!/bin/bash
# LiH R=1.6 mid300 — sized from pilot walltime (+checkpoint, 7-day limit).
# Pilot: ~20.65 h for 200 ep / seq=20 → mid300 raw ~46 h, +1.5× safety ≈ 3 d.
#   bash scripts/hpc/submit_gqe_lih_r16_mid300.sh

set -euo pipefail
REPO="${QCHEM_REPO:-$HOME/projects/qchem_qml_md}"
cd "$REPO"
mkdir -p logs

BOND=1.6
SEED="${SEED:-0}"
EPOCHS="${EPOCHS:-300}"
SEQ_LEN="${SEQ_LEN:-30}"
SAMPLES="${SAMPLES:-50}"
RUN_TAG="${RUN_TAG:-mid300}"
CKPT_EVERY="${CKPT_EVERY:-25}"

echo "[submit] LiH R=1.6 mid300 (seq=$SEQ_LEN ep=$EPOCHS ckpt_every=$CKPT_EVERY, 7d)"
echo "[submit] walltime estimate (from pilot 20.65h / 200ep / seq20):"
PYBIN="${PYBIN:-}"
if [[ -z "$PYBIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then PYBIN=python3
  elif command -v python >/dev/null 2>&1; then PYBIN=python
  fi
fi
if [[ -n "${PYBIN}" ]]; then
  "$PYBIN" scripts/hpc/estimate_gqe_walltime.py \
    --pilot-hours 20.65 --pilot-epochs 200 --pilot-seq-len 20 \
    --target-epochs "$EPOCHS" --target-seq-len "$SEQ_LEN" \
    --safety 1.5 --label "lih-mid300" || true
else
  echo "  (skip estimate: no python on PATH; raw≈46h +1.5× ≈3d, using 7d)"
fi

jid=$(sbatch \
  --job-name="gqe-lih-R1.6-mid300" \
  --time=7-00:00:00 \
  --mem=64G \
  --export=ALL,BOND="$BOND",SEED="$SEED",EPOCHS="$EPOCHS",SEQ_LEN="$SEQ_LEN",SAMPLES="$SAMPLES",RUN_TAG="$RUN_TAG",PAPER_MODEL=0,D_MODEL=64,N_LAYERS=2,OUT_SUBDIR=gqe_nakaji_lih_long,CKPT_EVERY="$CKPT_EVERY",LOG_EVERY=1 \
  scripts/hpc/gqe_nakaji_lih_bond.sbatch | awk '{print $4}')
echo "  mid300 -> $jid"
echo "[submit] monitor: squeue -u \$USER | grep gqe-lih"
echo "[submit] ckpt: ~/results/gqe_nakaji_lih_long/ckpt_R${BOND}_s${SEED}_${RUN_TAG}/checkpoint_latest.json"
