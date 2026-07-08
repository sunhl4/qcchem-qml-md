#!/bin/bash
#SBATCH --job-name=h2o-uqc-mdml
#SBATCH --partition=hpc
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=08:00:00
#SBATCH --output=logs/h2o_uqc_mdml_%j.out
#SBATCH --error=logs/h2o_uqc_mdml_%j.err

# H2O STO-3G CAS(4,4) + UQC 力场在线学习（mock 或内网云）
#   cd ~/projects/qchem_qml_md && mkdir -p logs
#   PROFILE=uqc_mock LOOP=configs/example_h2o_uqc_mock_qmlff_loop_hpc.yaml sbatch scripts/hpc/run_h2o_uqc_md_ml.sbatch
#   PROFILE=uqc_mock LOOP=configs/example_h2o_uqc_mock_qmlff_loop_5rounds.yaml sbatch scripts/hpc/run_h2o_uqc_md_ml.sbatch
#   PROFILE=uqc_cloud LOOP=configs/example_h2o_uqc_cloud_sim_qmlff_loop_5rounds.yaml sbatch scripts/hpc/run_h2o_uqc_md_ml.sbatch

set -euo pipefail

PROFILE="${PROFILE:-uqc_mock}"
HPC_HOME="${HPC_HOME:-${HOME:-/data/home/$(whoami)}}"
REPO="${QCHEM_REPO:-$HPC_HOME/projects/qchem_qml_md}"
ENV_PATH="${ENV_PATH:-$HPC_HOME/envs/qchem-stack}"
CONDA_ROOT="${CONDA_PREFIX:-$HPC_HOME/miniforge3}"
OUT="${OUT:-$HPC_HOME/results/hpc_h2o_${PROFILE}_${SLURM_JOB_ID}}"

# shellcheck source=/dev/null
source "$CONDA_ROOT/etc/profile.d/conda.sh"
conda activate "$ENV_PATH"
cd "$REPO"
export JAX_PLATFORMS="${JAX_PLATFORMS:-cpu}"
export QMLFF_QUANTUM_DEVICE="${QMLFF_QUANTUM_DEVICE:-default.qubit}"
export QCHEM_STACK_PYTHON="$(which python)"

python -c "import qchem_stack.orchestration, qchem_stack_uqc  # noqa"

if [[ "$PROFILE" == "uqc_cloud" ]]; then
  EXP=configs/example_h2o_uqc_cloud_sim_md_ml.yaml
  LOOP="${LOOP:-configs/example_h2o_uqc_cloud_sim_qmlff_loop_5rounds.yaml}"
  unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY
  python scripts/check_uqc_connectivity.py
else
  EXP=configs/example_h2o_uqc_mock_md_ml.yaml
  LOOP="${LOOP:-configs/example_h2o_uqc_mock_qmlff_loop_hpc.yaml}"
fi

echo "=== node=$(hostname) job=$SLURM_JOB_ID profile=$PROFILE loop=$LOOP out=$OUT ==="

python scripts/run_uqc_md_ml.py \
  --backend-profile "$PROFILE" \
  --experiment "$EXP" \
  --loop "$LOOP" \
  --output "$OUT"

echo "=== summary ==="
python - <<PY
import json
from pathlib import Path
p = Path("$OUT") / "md_validation_summary.json"
s = json.loads(p.read_text())
print(json.dumps({k: s.get(k) for k in [
    "converged","science_kpi_met","backend_profile","rounds_completed",
    "final_energy_error_hartree","max_energy_error_hartree"
]}, indent=2))
PY
echo "=== done: $OUT/md_validation_summary.json ==="
