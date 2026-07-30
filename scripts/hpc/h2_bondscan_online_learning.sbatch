#!/bin/bash
#SBATCH --job-name=h2-bondscan-ol
#SBATCH --partition=hpc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --mem=120G
#SBATCH --time=2-00:00:00
#SBATCH --output=logs/h2_bondscan_ol_%j.out
#SBATCH --error=logs/h2_bondscan_ol_%j.err

# H₂ 量子化学键长扫描 → 预训练 → 在线学习
#
# 资源规则：1 核对应 4 GB 内存（默认 30 核 / 120G）
#
# 提交：
#   # P0–P2 改进（推荐）：
#   LOOP=configs/example_h2_qmlff_bondscan_ol_p0p2.yaml MAX_ROUNDS=40 \
#     sbatch --cpus-per-task=30 --mem=120G --time=2-00:00:00 \
#     scripts/hpc/h2_bondscan_online_learning.sbatch
#   # 旧 20 轮：
#   MAX_ROUNDS=20 sbatch scripts/hpc/h2_bondscan_online_learning.sbatch
#
# 输出写在 $HOME/results/（禁止 /data/scratch/）

set -euo pipefail

PROFILE="${PROFILE:-statevector}"
MAX_ROUNDS="${MAX_ROUNDS:-40}"
LOOP="${LOOP:-}"
HPC_HOME="${HPC_HOME:-${HOME:-/data/home/$(whoami)}}"
REPO="${QCHEM_REPO:-$HPC_HOME/projects/qchem_qml_md}"
ENV_PATH="${ENV_PATH:-$HPC_HOME/envs/qchem-stack}"
CONDA_ROOT="${CONDA_PREFIX:-$HPC_HOME/miniforge3}"

# shellcheck source=/dev/null
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate "$ENV_PATH"
cd "$REPO"
export JAX_PLATFORMS="${JAX_PLATFORMS:-cpu}"
export OMP_NUM_THREADS="${SLURM_CPUS_PER_TASK:-30}"
export OPENBLAS_NUM_THREADS="${SLURM_CPUS_PER_TASK:-30}"
export QCHEM_STACK_PYTHON="$(which python)"

python -c "import qchem_stack.orchestration  # noqa"

echo "=== node=$(hostname) job=$SLURM_JOB_ID ==="
echo "=== cpus=${SLURM_CPUS_PER_TASK:-?} mem_rule=1cpu→4G profile=$PROFILE rounds=$MAX_ROUNDS ==="

if [[ -z "$LOOP" ]]; then
  case "$MAX_ROUNDS" in
    40|p0p2) LOOP=configs/example_h2_qmlff_bondscan_ol_p0p2.yaml ;;
    50) LOOP=configs/example_h2_qmlff_bondscan_ol_50rounds.yaml ;;
    *)  LOOP=configs/example_h2_qmlff_bondscan_ol_20rounds.yaml ;;
  esac
fi
echo "=== loop=$LOOP ==="

case "$PROFILE" in
  uqc_cloud)
    EXP=configs/example_h2_uqc_cloud_sim_md_ml.yaml
    unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY || true
    python scripts/check_uqc_connectivity.py
    ;;
  uqc_mock)
    EXP=configs/example_h2_uqc_mock_md_ml.yaml
    ;;
  *)
    # 默认：本地 statevector VQE（量子计算化学键长扫描，不依赖 UQC）
    EXP=configs/example_h2.yaml
    PROFILE=statevector
    ;;
esac

TAG="r${MAX_ROUNDS}"
if [[ "$LOOP" == *p0p2* ]]; then TAG="p0p2_r${MAX_ROUNDS}"; fi
OUT="$HPC_HOME/results/h2_bondscan_ol_${PROFILE}_${TAG}_${SLURM_JOB_ID}"
mkdir -p "$OUT" logs

python scripts/run_uqc_md_ml.py \
  --backend-profile "$PROFILE" \
  --experiment "$EXP" \
  --loop "$LOOP" \
  --output "$OUT"

echo "=== done: $OUT/md_validation_summary.json ==="
test -f "$OUT/round_bond_schedule.json" && echo "=== bond schedule: $OUT/round_bond_schedule.json ==="
test -f "$OUT/dissociation_cutoff_policy.json" && echo "=== dissociation policy: $OUT/dissociation_cutoff_policy.json ==="
