#!/usr/bin/env bash
# 幺正量子 HPC：在 $HOME（/data/home/<user>）创建 qchem-stack + QML-FF 环境。
# 禁止安装到 /data/scratch/ — 该目录会被集群不定期清理。

set -euo pipefail

HPC_HOME="${HPC_HOME:-${HOME:-/data/home/$(whoami)}}"
QCHEM_REPO="${QCHEM_REPO:-$HPC_HOME/projects/qchem_qml_md}"
QMLFF_REPO="${QMLFF_REPO:-$HPC_HOME/projects/QML-FF}"
CONDA_PREFIX="${CONDA_PREFIX:-$HPC_HOME/miniforge3}"
ENV_PATH="${ENV_PATH:-$HPC_HOME/envs/qchem-stack}"

mkdir -p "$HPC_HOME"/{projects,envs,logs,results}

log() { echo "[setup] $*"; }

proxy_on() {
  if declare -F proxy_on >/dev/null 2>&1; then
    proxy_on
    return
  fi
  export http_proxy="${http_proxy:-http://192.168.110.143:7897}"
  export https_proxy="${https_proxy:-$http_proxy}"
  export HTTP_PROXY="$http_proxy"
  export HTTPS_PROXY="$https_proxy"
  export no_proxy="${no_proxy:-localhost,127.0.0.1,::1,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,.local}"
  export NO_PROXY="$no_proxy"
  log "proxy on: $http_proxy"
}

proxy_off() {
  if declare -F proxy_off >/dev/null 2>&1; then
    proxy_off
    return
  fi
  unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY || true
  log "proxy off"
}

install_miniforge() {
  if [[ -x "$CONDA_PREFIX/bin/conda" ]]; then
    log "conda at $CONDA_PREFIX"
    return
  fi
  log "installing Miniforge -> $CONDA_PREFIX"
  proxy_on
  tmp="$(mktemp -d)"
  curl -fsSL -o "$tmp/miniforge.sh" \
    https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh
  bash "$tmp/miniforge.sh" -b -p "$CONDA_PREFIX"
  rm -rf "$tmp"
}

source_conda() {
  # shellcheck source=/dev/null
  source "$CONDA_PREFIX/etc/profile.d/conda.sh"
}

create_env() {
  install_miniforge
  source_conda
  if [[ ! -x "$ENV_PATH/bin/python" ]]; then
    log "conda env create -> $ENV_PATH"
    conda env create -f "$QCHEM_REPO/environment-hpc.yml" -p "$ENV_PATH"
  fi
  conda activate "$ENV_PATH"
  log "python: $(which python) ($(python -V))"
}

install_pip_stack() {
  proxy_on
  pip install -U pip wheel setuptools
  cd "$QCHEM_REPO"
  pip install -e ".[chem,quantum,uqc,qmlff]"
  pip install -e packages/qchem-stack-uqc
  pip install uqc-client nest-asyncio "aiofiles~=24.1.0"
  # jaxlib 可能由 conda 安装；避免 force-reinstall 触发 uninstall-no-record-file
  pip install \
    "numpy>=2.0,<3" "jax==0.7.1" \
    "pennylane==0.44.1" "autoray==0.8.2" \
    "flax>=0.10" "optax>=0.2" "chex>=0.1.90" "jax-md>=0.2.29"
  pip install "jaxlib==0.7.1" 2>/dev/null || true
  pip install -e "$QMLFF_REPO" --no-deps
  export QCHEM_STACK_PYTHON="$(which python)"
  export JAX_PLATFORMS="${JAX_PLATFORMS:-cpu}"
}

write_env_template() {
  local envfile="$QCHEM_REPO/.env"
  if [[ -f "$envfile" ]]; then
    return
  fi
  cat >"$envfile" <<EOF
SERVER_HOST=192.168.110.148
SERVER_PORT=8003
UQC_API_TOKEN=
JAX_PLATFORMS=cpu
EOF
  chmod 600 "$envfile"
  log "wrote $envfile"
}

write_env_sh() {
  local envsh="$HPC_HOME/env.sh"
  cat >"$envsh" <<EOF
# 每次登录 HPC 后: source $envsh
source $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate $ENV_PATH
export JAX_PLATFORMS=cpu
cd $QCHEM_REPO
EOF
  chmod 644 "$envsh"
  log "wrote $envsh"
}

verify() {
  cd "$QCHEM_REPO"
  python -c "
import importlib.metadata as m
import pyscf, qmlff, jax_md, qchem_stack_uqc
import qchem_stack.orchestration
print('OK jax', m.version('jax'), 'pennylane', m.version('pennylane'))
"
  python scripts/smoke_pipeline.py
  proxy_off
  python scripts/check_uqc_connectivity.py || log "UQC: set token in .env for API check"
}

run_mock_smoke() {
  cd "$QCHEM_REPO"
  export JAX_PLATFORMS=cpu
  python scripts/run_uqc_md_ml.py \
    --backend-profile uqc_mock \
    --experiment configs/example_h2_uqc_mock_md_ml.yaml \
    --loop configs/example_h2_uqc_mock_qmlff_loop_smoke.yaml \
    --output "$HPC_HOME/results/hpc_smoke_uqc_mock"
  test -f "$HPC_HOME/results/hpc_smoke_uqc_mock/md_validation_summary.json"
  log "mock smoke OK"
}

main() {
  log "HPC_HOME=$HPC_HOME HOME=${HOME:-unset}"
  [[ -d "$QCHEM_REPO" ]] || { echo "missing $QCHEM_REPO — rsync projects first"; exit 1; }
  [[ -d "$QMLFF_REPO" ]] || { echo "missing $QMLFF_REPO"; exit 1; }
  create_env
  install_pip_stack
  write_env_template
  write_env_sh
  verify
  run_mock_smoke
  cat <<EOF

=== Done (workspace: $HPC_HOME) ===
  source $HPC_HOME/env.sh   # or see docs/HPC登录与环境配置教程_幺正量子集群.md
EOF
}

main "$@"
