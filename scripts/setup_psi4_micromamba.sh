#!/usr/bin/env bash
# Install Psi4 + PySCF into a project-local micromamba env (Linux x86_64).
# Usage: ./scripts/setup_psi4_micromamba.sh
# Then:  .micromamba/envs/.conda-psi4/bin/python -m pytest -m psi4 -q
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-$ROOT/.micromamba}"
if [[ ! -x "$ROOT/bin/micromamba" ]]; then
  mkdir -p "$ROOT/bin"
  curl -Ls https://micro.mamba.pm/api/micromamba/linux-64/latest \
    | tar -xj -C "$ROOT/bin" bin/micromamba --strip-components=1
fi
"$ROOT/bin/micromamba" create -y -p "$MAMBA_ROOT_PREFIX/envs/.conda-psi4" \
  -c conda-forge \
  python=3.12 psi4 pyscf pytest pydantic pyyaml openfermion scipy pandas opt_einsum
"$MAMBA_ROOT_PREFIX/envs/.conda-psi4/bin/python" -m pip install -U pip
"$MAMBA_ROOT_PREFIX/envs/.conda-psi4/bin/python" -m pip install -e ".[dev]"
echo "Psi4 env ready: $MAMBA_ROOT_PREFIX/envs/.conda-psi4/bin/python"
"$MAMBA_ROOT_PREFIX/envs/.conda-psi4/bin/python" -c "import psi4, pyscf; print('psi4', psi4.__version__, 'pyscf', pyscf.__version__)"
