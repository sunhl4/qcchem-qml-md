from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.quantum.algorithms.vqe import VQE, VQEResult

if TYPE_CHECKING:
    from qchem_stack.backends.spec import BackendSpec
    from qchem_stack.config import ExperimentConfig


def vqe_from_backend_spec(
    spec: BackendSpec,
    hamiltonian: QubitHamiltonian,
    depth: int = 1,
    **run_kw: Any,
) -> VQEResult:
    """Run VQE with :func:`~qchem_stack.backends.factory.executor_from_spec`."""
    ex = executor_from_spec(spec)
    return VQE(hamiltonian, depth=depth, executor=ex).run(**run_kw)


def vqe_from_experiment_config(
    cfg: ExperimentConfig,
    hamiltonian: QubitHamiltonian,
    depth: int = 1,
    **run_kw: Any,
) -> VQEResult:
    """Run VQE using experiment YAML ``backend`` block."""
    from qchem_stack.config import backend_spec_from_config

    return vqe_from_backend_spec(backend_spec_from_config(cfg), hamiltonian, depth=depth, **run_kw)
