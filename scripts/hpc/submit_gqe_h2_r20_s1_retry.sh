#!/bin/bash
# H2 R=2.0 seed=1 only — push remaining miss to chemical accuracy.
# Previous retry400: s0/s2 ok, s1 err≈3.25 mHa.
#   bash scripts/hpc/submit_gqe_h2_r20_s1_retry.sh

set -euo pipefail
REPO="${QCHEM_REPO:-$HOME/projects/qchem_qml_md}"
cd "$REPO"
mkdir -p logs

BOND=2.0
SEED=1
EPOCHS="${EPOCHS:-600}"
SEQ_LEN="${SEQ_LEN:-14}"
SAMPLES="${SAMPLES:-50}"
RUN_TAG="${RUN_TAG:-retry600_s1}"

echo "[submit] H2 R=2.0 s1-only: epochs=$EPOCHS seq_len=$SEQ_LEN tag=$RUN_TAG"
jid=$(sbatch \
  --job-name="gqe-h2-R2.0-s1-r600" \
  --time=24:00:00 \
  --export=ALL,BOND="$BOND",SEED="$SEED",EPOCHS="$EPOCHS",SEQ_LEN="$SEQ_LEN",SAMPLES="$SAMPLES",RUN_TAG="$RUN_TAG" \
  scripts/hpc/gqe_nakaji_h2_bond.sbatch | awk '{print $4}')
echo "  submitted -> $jid"
echo "[submit] done"
