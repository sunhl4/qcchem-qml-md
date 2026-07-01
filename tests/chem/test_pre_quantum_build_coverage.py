"""Pre-quantum build branch registry and capability error paths."""

from __future__ import annotations

from qchem_stack.chem.pre_quantum_builder_registry import list_pre_quantum_branch_builders
from qchem_stack.exceptions import PreQuantumCapabilityError


def test_pre_quantum_builder_registry_nonempty() -> None:
    from qchem_stack.chem.pre_quantum_build import _register_default_pre_quantum_branch_builders

    _register_default_pre_quantum_branch_builders()
    builders = list_pre_quantum_branch_builders()
    assert len(builders) >= 1


def test_pre_quantum_capability_error_message() -> None:
    err = PreQuantumCapabilityError("missing restricted active space export")
    assert "restricted active space" in str(err)
