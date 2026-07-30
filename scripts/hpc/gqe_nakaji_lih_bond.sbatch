#!/bin/bash
#SBATCH --job-name=gqe-lih
#SBATCH --partition=hpc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=48:00:00
#SBATCH --output=logs/gqe_nakaji_lih_%x_%j.out
#SBATCH --error=logs/gqe_nakaji_lih_%x_%j.err

# Env: BOND SEED EPOCHS SAMPLES SEQ_LEN RUN_TAG PAPER_MODEL D_MODEL N_LAYERS
#      OUT_SUBDIR CKPT_EVERY LOG_EVERY

set -euo pipefail

HPC_HOME="${HPC_HOME:-${HOME:-/data/home/$(whoami)}}"
REPO="${QCHEM_REPO:-$HPC_HOME/projects/qchem_qml_md}"
ENV_PATH="${ENV_PATH:-$HPC_HOME/envs/qchem-stack}"
CONDA_ROOT="${CONDA_ROOT:-$HPC_HOME/miniforge3}"

BOND="${BOND:-1.6}"
SEED="${SEED:-0}"
EPOCHS="${EPOCHS:-200}"
SAMPLES="${SAMPLES:-50}"
SEQ_LEN="${SEQ_LEN:-20}"
WARMUP="${WARMUP:-200}"
BUFFER="${BUFFER:-1000}"
BATCH="${BATCH:-50}"
N_ITER="${N_ITER:-5}"
LOSS="${LOSS:-grpo}"
RUN_TAG="${RUN_TAG:-pilot}"
PAPER_MODEL="${PAPER_MODEL:-0}"
D_MODEL="${D_MODEL:-64}"
N_LAYERS="${N_LAYERS:-2}"
OUT_SUBDIR="${OUT_SUBDIR:-gqe_nakaji_lih_pilot}"
CKPT_EVERY="${CKPT_EVERY:-25}"
LOG_EVERY="${LOG_EVERY:-1}"

OUT_DIR="$HPC_HOME/results/${OUT_SUBDIR}"
mkdir -p "$OUT_DIR" "$REPO/logs"

source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate "$ENV_PATH"
cd "$REPO"
export JAX_PLATFORMS="${JAX_PLATFORMS:-cpu}"
export PYTHONUNBUFFERED=1

TAG="R${BOND}_s${SEED}_${RUN_TAG}"
OUT_JSON="$OUT_DIR/lih_${TAG}.json"
CKPT_DIR="$OUT_DIR/ckpt_${TAG}"

EXTRA=()
if [[ "$PAPER_MODEL" == "1" ]]; then
  EXTRA+=(--paper-model)
else
  EXTRA+=(--d-model "$D_MODEL" --n-layers "$N_LAYERS")
fi

echo "=== gqe nakaji lih bond=$BOND seed=$SEED epochs=$EPOCHS seq_len=$SEQ_LEN paper_model=$PAPER_MODEL tag=$RUN_TAG ckpt_every=$CKPT_EVERY node=$(hostname) ==="
python -u examples/gqe_nakaji_paper_repro.py \
  --molecule lih \
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
  --checkpoint-dir "$CKPT_DIR" \
  --checkpoint-every "$CKPT_EVERY" \
  --log-every "$LOG_EVERY" \
  "${EXTRA[@]}" \
  --out "$OUT_JSON"

echo "=== done: $OUT_JSON ==="
