"""GQE (Generative Quantum Eigensolver) — product integration path.

Plan B: classical generative model proposes operator-token sequences; energy
scoring reuses ``HamiltonianExpectationExecutor`` and the chem / operator-pool
stack. JAX/optax are optional via ``pip install 'qchem-stack[gqe]'``.

Canonical entry: :func:`qchem_stack.integrations.gqe.api.run_gqe_from_config`.
Orchestration may invoke the same API when ``gqe.enabled: true``. The package
does **not** register a ``quantum.algorithm`` or place JAX under ``quantum/``.
"""

from __future__ import annotations

from qchem_stack.integrations.gqe.api import run_gqe_from_config
from qchem_stack.integrations.gqe.blueprint import gqe_integration_blueprint
from qchem_stack.integrations.gqe.probe_cudaq import probe_cudaq_solvers_installation
from qchem_stack.integrations.gqe.probe_jax import probe_gqe_jax_installation

__all__ = [
    "gqe_integration_blueprint",
    "probe_cudaq_solvers_installation",
    "probe_gqe_jax_installation",
    "run_gqe_from_config",
]
