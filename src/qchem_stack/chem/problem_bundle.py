"""Unified chemistry problem container (optional layering over existing quantum-problem tuples)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.contracts.schema_ids import CHEMISTRY_PROBLEM_BUNDLE_V1

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.chem.fermion import FermionSpace
    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.chem.molecular_problem import RestrictedActiveSpaceQuantumProblem


@dataclass
class ChemistryProblemBundle:
    """Snapshots a variational-ready chemistry instance for pipeline / exporters.

    Wraps quantities already produced by ``RestrictedActiveSpaceQuantumProblem`` without replacing it.
    """

    constant_energies_au: dict[str, float]
    fermion_space: FermionSpace
    interaction_operator_constant: float
    interaction_operator_summary: dict[str, Any]
    qubit_hamiltonian: QubitHamiltonian
    reference_energy_hf_au: float | None
    backend_driver_meta: dict[str, Any] = field(default_factory=dict)
    classical_mean_field_snapshot: ClassicalMeanFieldReference | None = None
    """Backend-agnostic mean-field snapshot for exporter / diagnostics."""

    def model_dump_public(self) -> dict[str, Any]:
        """JSON-friendly summary (arrays omitted)."""

        qh = self.qubit_hamiltonian
        return {
            "schema": CHEMISTRY_PROBLEM_BUNDLE_V1,
            "constant_energies_au": dict(self.constant_energies_au),
            "fermion_space": {
                "n_spin_orbitals": self.fermion_space.n_spin_orbitals,
                "n_electrons": self.fermion_space.n_electrons,
            },
            "interaction_operator_constant": float(self.interaction_operator_constant),
            "qubit_hamiltonian": {
                "n_qubits": qh.n_qubits,
                "n_terms": len(getattr(qh.operator, "terms", {}) or {}),
            },
            "reference_energy_hf_au": self.reference_energy_hf_au,
            "backend_driver_family": self.backend_driver_meta.get("driver_family"),
        }

    @classmethod
    def from_restricted_active_space_problem(
        cls,
        prob: RestrictedActiveSpaceQuantumProblem,
        *,
        reference: ClassicalMeanFieldReference | None = None,
    ) -> ChemistryProblemBundle:
        from qchem_stack.chem.molecular_problem import RestrictedActiveSpaceQuantumProblem as RASP

        if not isinstance(prob, RASP):  # pragma: no cover
            raise TypeError("expected RestrictedActiveSpaceQuantumProblem")
        mol_op = prob.interaction_operator
        c = float(mol_op.constant)
        hf_e = float(reference.e_tot) if reference is not None else None
        meta_backend = dict(reference.driver_meta) if reference is not None else {}
        hf_block = mol_op.two_body_tensor  # noqa: SLF001
        return cls(
            constant_energies_au={"interaction_constant": c, "hf_total_au": hf_e}
            if hf_e is not None
            else {"interaction_constant": c},
            fermion_space=prob.fermion_space,
            interaction_operator_constant=c,
            interaction_operator_summary={
                "one_body_shape": list(np.asarray(mol_op.one_body_tensor).shape),
                "two_body_shape": list(np.asarray(hf_block).shape),
            },
            qubit_hamiltonian=prob.qubit_hamiltonian,
            reference_energy_hf_au=hf_e,
            backend_driver_meta=meta_backend,
            classical_mean_field_snapshot=reference,
        )
