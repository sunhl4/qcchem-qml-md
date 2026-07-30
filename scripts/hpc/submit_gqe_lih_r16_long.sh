#!/bin/bash
# LiH R=1.6 — paper-scale (Nakaji §3.1) + compromise walltime estimate.
#   bash scripts/hpc/submit_gqe_lih_r16_long.sh

set -euo pipefail
REPO="${QCHEM_REPO:-$HOME/projects/qchem_qml_md}"
cd "$REPO"
mkdir -p logs

BOND=1.6
SEED=0

echo "[submit] LiH R=1.6 long runs (paper + compromise)"

# 1) Paper-scale: seq_len=40, epochs=500, GPT-2 size (d=192, L=6)
jid1=$(sbatch \
  --job-name="gqe-lih-R1.6-paper" \
  --time=2-00:00:00 \
  --mem=96G \
  --export=ALL,BOND="$BOND",SEED="$SEED",EPOCHS=500,SEQ_LEN=40,SAMPLES=50,RUN_TAG=paper500,PAPER_MODEL=1,OUT_SUBDIR=gqe_nakaji_lih_long \
  scripts/hpc/gqe_nakaji_lih_bond.sbatch | awk '{print $4}')
echo "  paper500 seq40 d192 L6 -> $jid1"

# 2) Compromise: seq_len=30, epochs=400, small transformer (walltime probe)
jid2=$(sbatch \
  --job-name="gqe-lih-R1.6-mid" \
  --time=2-00:00:00 \
  --mem=64G \
  --export=ALL,BOND="$BOND",SEED="$SEED",EPOCHS=400,SEQ_LEN=30,SAMPLES=50,RUN_TAG=mid400,PAPER_MODEL=0,D_MODEL=64,N_LAYERS=2,OUT_SUBDIR=gqe_nakaji_lih_long \
  scripts/hpc/gqe_nakaji_lih_bond.sbatch | awk '{print $4}')
echo "  mid400 seq30 d64 L2 -> $jid2"

echo "[submit] done. monitor: squeue -u \$USER | grep gqe-lih"
