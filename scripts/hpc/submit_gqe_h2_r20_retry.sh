#!/bin/bash
# Retry H2 R=2.0 Å (dissociation) with longer training — 3 seeds.
#   bash scripts/hpc/submit_gqe_h2_r20_retry.sh

set -euo pipefail
REPO="${QCHEM_REPO:-$HOME/projects/qchem_qml_md}"
cd "$REPO"
mkdir -p logs

BOND=2.0
EPOCHS="${EPOCHS:-400}"
SEQ_LEN="${SEQ_LEN:-12}"
SAMPLES="${SAMPLES:-50}"
RUN_TAG="${RUN_TAG:-retry400}"

echo "[submit] H2 R=2.0 retry: epochs=$EPOCHS seq_len=$SEQ_LEN tag=$RUN_TAG"

for seed in 0 1 2; do
  jobname="gqe-h2-R2.0-retry-s${seed}"
  jid=$(sbatch \
    --job-name="$jobname" \
    --time=24:00:00 \
    --export=ALL,BOND="$BOND",SEED="$seed",EPOCHS="$EPOCHS",SEQ_LEN="$SEQ_LEN",SAMPLES="$SAMPLES",RUN_TAG="$RUN_TAG" \
    scripts/hpc/gqe_nakaji_h2_bond.sbatch | awk '{print $4}')
  echo "  submitted $jobname -> $jid"
done

echo "[submit] done"
