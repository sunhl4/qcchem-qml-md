#!/usr/bin/env bash
# 同步代码到幺正 HPC 并提交 H₂ 键长扫描 + 在线学习作业。
# 资源：默认 30 核 / 120G（1 核 ↔ 4G）；可用 CPUS / MEM_G 覆盖。
#
# 用法：
#   ./scripts/hpc/submit_h2_bondscan_online_learning.sh
#   MAX_ROUNDS=50 ./scripts/hpc/submit_h2_bondscan_online_learning.sh
#   PROFILE=uqc_mock DRY_RUN=1 ./scripts/hpc/submit_h2_bondscan_online_learning.sh

set -euo pipefail

LOCAL_QCHEM="${LOCAL_QCHEM:-/home/sunhl/projects/qchem_qml_md}"
LOCAL_QMLFF="${LOCAL_QMLFF:-/home/sunhl/projects/QML-FF}"
REMOTE="${REMOTE:-sun_hl@192.168.110.220}"
PROFILE="${PROFILE:-statevector}"
MAX_ROUNDS="${MAX_ROUNDS:-20}"
CPUS="${CPUS:-30}"
# 1 核 → 4G
MEM_G="${MEM_G:-$((CPUS * 4))}"
TIME="${TIME:-1-00:00:00}"
DRY_RUN="${DRY_RUN:-0}"
SKIP_RSYNC="${SKIP_RSYNC:-0}"

echo "[submit] remote=$REMOTE profile=$PROFILE rounds=$MAX_ROUNDS cpus=$CPUS mem=${MEM_G}G"

if [[ "$SKIP_RSYNC" != "1" ]]; then
  rsync -avz --progress \
    --exclude '.git' --exclude '.venv' --exclude '.micromamba' \
    --exclude 'htmlcov' --exclude 'docusaurus-site' --exclude 'results' \
    --exclude '__pycache__' --exclude '.pytest_cache' --exclude 'node_modules' \
    "$LOCAL_QCHEM/" "$REMOTE:~/projects/qchem_qml_md/"

  if [[ -d "$LOCAL_QMLFF" ]]; then
    rsync -avz --progress \
      --exclude '.git' --exclude '__pycache__' \
      "$LOCAL_QMLFF/" "$REMOTE:~/projects/QML-FF/"
  fi

  if [[ -f "$LOCAL_QCHEM/.env" ]]; then
    scp "$LOCAL_QCHEM/.env" "$REMOTE:~/projects/qchem_qml_md/.env"
  fi
fi

SBATCH_CMD=(
  sbatch
  --cpus-per-task="$CPUS"
  --mem="${MEM_G}G"
  --time="$TIME"
  --export="ALL,PROFILE=${PROFILE},MAX_ROUNDS=${MAX_ROUNDS}"
  scripts/hpc/h2_bondscan_online_learning.sbatch
)

REMOTE_SCRIPT=$(cat <<EOF
set -euo pipefail
cd ~/projects/qchem_qml_md
mkdir -p logs ~/results
echo "[remote] \$(hostname) submitting: ${SBATCH_CMD[*]}"
if [[ "$DRY_RUN" == "1" ]]; then
  echo "[remote] DRY_RUN=1 — not calling sbatch"
  exit 0
fi
${SBATCH_CMD[*]}
EOF
)

ssh "$REMOTE" "bash -s" <<<"$REMOTE_SCRIPT"
echo "[submit] done. On HPC: squeue -u \$USER ; ls ~/results/h2_bondscan_ol_*"
