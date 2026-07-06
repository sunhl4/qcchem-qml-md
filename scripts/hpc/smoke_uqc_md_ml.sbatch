#!/bin/bash
#SBATCH --job-name=uqc-mdml-smoke
#SBATCH --partition=hpc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/uqc_mdml_smoke_%j.out
#SBATCH --error=logs/uqc_mdml_smoke_%j.err

# 力场在线学习 smoke（默认 UQC mock；改 PROFILE=uqc_cloud 需 .env 中 token）
# 输出与依赖均在 $HOME；禁止写入 /data/scratch/（不定期清理）。
#   cd ~/projects/qchem_qml_md
#   mkdir -p logs
#   PROFILE=uqc_mock sbatch scripts/hpc/smoke_uqc_md_ml.sbatch
#   PROFILE=uqc_cloud sbatch scripts/hpc/smoke_uqc_md_ml.sbatch

set -euo pipefail

PROFILE="${PROFILE:-uqc_mock}"
HPC_HOME="${HPC_HOME:-${HOME:-/data/home/$(whoami)}}"
REPO="${QCHEM_REPO:-$HPC_HOME/projects/qchem_qml_md}"
ENV_PATH="${ENV_PATH:-$HPC_HOME/envs/qchem-stack}"
CONDA_ROOT="${CONDA_PREFIX:-$HPC_HOME/miniforge3}"

# shellcheck source=/dev/null
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate "$ENV_PATH"
cd "$REPO"
export JAX_PLATFORMS="${JAX_PLATFORMS:-cpu}"
export QCHEM_STACK_PYTHON="$(which python)"

# 注册 pipeline runner + UQC backend
python -c "import qchem_stack.orchestration, qchem_stack_uqc  # noqa"

echo "=== node=$(hostname) profile=$PROFILE python=$QCHEM_STACK_PYTHON ==="

if [[ "$PROFILE" == "uqc_cloud" ]]; then
  EXP=configs/example_h2_uqc_cloud_sim_md_ml.yaml
  LOOP=configs/example_h2_uqc_cloud_sim_qmlff_loop_smoke.yaml
  OUT=$HPC_HOME/results/hpc_slurm_uqc_cloud_${SLURM_JOB_ID}
  unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
  python scripts/check_uqc_connectivity.py
else
  EXP=configs/example_h2_uqc_mock_md_ml.yaml
  LOOP=configs/example_h2_uqc_mock_qmlff_loop_smoke.yaml
  OUT=$HPC_HOME/results/hpc_slurm_uqc_mock_${SLURM_JOB_ID}
fi

python scripts/run_uqc_md_ml.py \
  --backend-profile "$PROFILE" \
  --experiment "$EXP" \
  --loop "$LOOP" \
  --output "$OUT"

echo "=== done: $OUT/md_validation_summary.json ==="
