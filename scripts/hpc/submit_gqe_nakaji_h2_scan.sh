#!/bin/bash
# Submit Nakaji H2 bond-length scan: 9 geometries × N_TRIALS (default 3).
# Run on HPC login node from repo root:
#   bash scripts/hpc/submit_gqe_nakaji_h2_scan.sh
#   N_TRIALS=1 EPOCHS=120 bash scripts/hpc/submit_gqe_nakaji_h2_scan.sh  # quick

set -euo pipefail

REPO="${QCHEM_REPO:-$HOME/projects/qchem_qml_md}"
cd "$REPO"
mkdir -p logs

BONDS=(0.5 0.6 0.7 0.8 0.9 1.0 1.2 1.5 2.0)
N_TRIALS="${N_TRIALS:-3}"
EPOCHS="${EPOCHS:-200}"
SAMPLES="${SAMPLES:-50}"
SEQ_LEN="${SEQ_LEN:-10}"
PAPER_MODEL="${PAPER_MODEL:-0}"

echo "[submit] H2 scan: ${#BONDS[@]} bonds × $N_TRIALS trials (epochs=$EPOCHS)"

for bond in "${BONDS[@]}"; do
  for seed in $(seq 0 $((N_TRIALS - 1))); do
    jobname="gqe-h2-R${bond}-s${seed}"
    jid=$(sbatch \
      --job-name="$jobname" \
      --export=ALL,BOND="$bond",SEED="$seed",EPOCHS="$EPOCHS",SAMPLES="$SAMPLES",SEQ_LEN="$SEQ_LEN",PAPER_MODEL="$PAPER_MODEL" \
      scripts/hpc/gqe_nakaji_h2_bond.sbatch | awk '{print $4}')
    echo "  submitted $jobname -> $jid"
  done
done

echo "[submit] done. monitor: squeue -u \$USER"
