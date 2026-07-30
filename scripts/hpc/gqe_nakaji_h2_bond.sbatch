#!/bin/bash
#SBATCH --job-name=gqe-h2
#SBATCH --partition=hpc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --output=logs/gqe_nakaji_h2_%x_%j.out
#SBATCH --error=logs/gqe_nakaji_h2_%x_%j.err

# Nakaji GPT-QE H2 single bond-length job (arXiv:2401.09253).
# Submit via scripts/hpc/submit_gqe_nakaji_h2_scan.sh on the login node.
#
# Env overrides:
#   BOND=0.74  SEED=0  EPOCHS=200  SAMPLES=50  SEQ_LEN=10
#   PAPER_MODEL=1  → d_model=192 n_layers=6
#   LOSS=grpo|lm

set -euo pipefail

HPC_HOME="${HPC_HOME:-${HOME:-/data/home/$(whoami)}}"
REPO="${QCHEM_REPO:-$HPC_HOME/projects/qchem_qml_md}"
ENV_PATH="${ENV_PATH:-$HPC_HOME/envs/qchem-stack}"
CONDA_ROOT="${CONDA_ROOT:-$HPC_HOME/miniforge3}"

BOND="${BOND:-0.74}"
SEED="${SEED:-0}"
EPOCHS="${EPOCHS:-200}"
SAMPLES="${SAMPLES:-50}"
SEQ_LEN="${SEQ_LEN:-10}"
WARMUP="${WARMUP:-200}"
BUFFER="${BUFFER:-1000}"
BATCH="${BATCH:-50}"
N_ITER="${N_ITER:-5}"
LOSS="${LOSS:-grpo}"
PAPER_MODEL="${PAPER_MODEL:-0}"
RUN_TAG="${RUN_TAG:-}"

OUT_DIR="$HPC_HOME/results/gqe_nakaji_h2_scan"
mkdir -p "$OUT_DIR" "$REPO/logs"

# shellcheck source=/dev/null
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate "$ENV_PATH"
cd "$REPO"
export JAX_PLATFORMS="${JAX_PLATFORMS:-cpu}"
export PYTHONUNBUFFERED=1

if [[ -n "$RUN_TAG" ]]; then
  TAG="R${BOND}_s${SEED}_${RUN_TAG}"
else
  TAG="R${BOND}_s${SEED}"
fi
OUT_JSON="$OUT_DIR/h2_${TAG}.json"

EXTRA=()
if [[ "$PAPER_MODEL" == "1" ]]; then
  EXTRA+=(--paper-model)
fi

echo "=== gqe nakaji h2 bond=$BOND seed=$SEED epochs=$EPOCHS node=$(hostname) ==="
python -u examples/gqe_nakaji_paper_repro.py \
  --molecule h2 \
  --bond "$BOND" \
  --epochs "$EPOCHS" \
  --samples "$SAMPLES" \
  --seq-len "$SEQ_LEN" \
  --warmup "$WARMUP" \
  --buffer "$BUFFER" \
  --batch "$BATCH" \
  --n-iter "$N_ITER" \
  --loss "$LOSS" \
  --seed "$SEED" \
  "${EXTRA[@]}" \
  --out "$OUT_JSON"

echo "=== done: $OUT_JSON ==="
