from __future__ import annotations

from qchem_stack.backends.executor_base import (
    HamiltonianExpectationExecutor,
    StatevectorHeaExecutor,
)
from qchem_stack.backends.ionstack_executor import IonStackHeaExecutor
from qchem_stack.backends.qiskit_executor import (
    QiskitPrimitivesHeaExecutor,
    QiskitStatevectorHeaExecutor,
)
from qchem_stack.backends.spec import BackendSpec


def executor_from_spec(spec: BackendSpec) -> HamiltonianExpectationExecutor:
    """Select simulator / device API from ``BackendSpec``."""
    provider = spec.provider.lower()
    if provider in ("statevector", "numpy", "local"):
        return StatevectorHeaExecutor()
    if provider in ("qiskit",):
        mode = (spec.qiskit_mode or "statevector").lower()
        if mode == "estimator":
            return QiskitPrimitivesHeaExecutor(spec)
        try:
            import qiskit  # noqa: F401
        except ImportError as e:  # pragma: no cover
            raise ImportError(
                "provider='qiskit' requires qiskit. Install: pip install qchem-stack[quantum]"
            ) from e
        return QiskitStatevectorHeaExecutor(spec)
    if provider in ("ionstack", "ion_stack"):
        return IonStackHeaExecutor(spec)
    raise ValueError(f"Unknown backend provider: {spec.provider!r}")
