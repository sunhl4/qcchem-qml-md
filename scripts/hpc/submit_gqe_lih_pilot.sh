#!/bin/bash
# LiH pilot: 3 bond lengths × 1 trial (paper equilibrium + stretch).
#   bash scripts/hpc/submit_gqe_lih_pilot.sh

set -euo pipefail
REPO="${QCHEM_REPO:-$HOME/projects/qchem_qml_md}"
cd "$REPO"
mkdir -p logs

BONDS=(1.4 1.6 2.0)
EPOCHS="${EPOCHS:-200}"
SEQ_LEN="${SEQ_LEN:-20}"
SAMPLES="${SAMPLES:-50}"
RUN_TAG="${RUN_TAG:-pilot}"

echo "[submit] LiH pilot: bonds=${BONDS[*]} epochs=$EPOCHS seq_len=$SEQ_LEN"

for bond in "${BONDS[@]}"; do
  jobname="gqe-lih-R${bond}-pilot"
  jid=$(sbatch \
    --job-name="$jobname" \
    --export=ALL,BOND="$bond",SEED=0,EPOCHS="$EPOCHS",SEQ_LEN="$SEQ_LEN",SAMPLES="$SAMPLES",RUN_TAG="$RUN_TAG" \
    scripts/hpc/gqe_nakaji_lih_bond.sbatch | awk '{print $4}')
  echo "  submitted $jobname -> $jid"
done

echo "[submit] done"
