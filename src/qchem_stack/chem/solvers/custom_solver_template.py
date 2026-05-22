"""Template for user-provided classical chemistry backend adapters.

Copy this module, replace ``backend_id``, and implement **L1 Driver** hooks only
(see ``docs/execution/multi_backend_integration_philosophy.md``).

Typical minimal path:

1. Implement ``run_molecular_mean_field`` → return :class:`MolecularMeanFieldResult`.
2. Wrap your wavefunction in :class:`~qchem_stack.chem.bridges.ao_basis_view.AOBasisView`.
3. Set :class:`SolverCapabilities` honestly (``False`` for unimplemented features).
4. Register via ``register_solver`` or entry point group ``qchem_stack.chem_solvers``.
5. Use :func:`~qchem_stack.chem.integration.merge_integration_driver_meta` for
   ``kernel_bindings`` / ``epistemic_bound``.
6. Run :func:`~qchem_stack.chem.integration.run_integration_checklist`.

Complex steps (AVAS, CASCI integrals, NEVPT2) should **delegate** to L3 kernels in
``qchem_stack.chem.kernels`` / ``active_space`` rather than reimplement in the driver.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from qchem_stack.chem.bridges.mean_field_like import wrap_mean_field_like
from qchem_stack.chem.integration.meta_schema import merge_integration_driver_meta
from qchem_stack.chem.integration.presets import capabilities_driver_scf_only
from qchem_stack.chem.kernels.catalog import KERNEL_MEAN_FIELD_SCF, kernel_binding
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities

if TYPE_CHECKING:
    from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
    from qchem_stack.config import ExperimentConfig


class CustomExternalIntegralSolver:
    """Minimal adapter template implementing the ChemIntegralSolver shape.

    This class is intentionally conservative: it validates config binding and
    raises ``NotImplementedError`` for backend-specific execution hooks.
    """

    def __init__(self, cfg: ExperimentConfig) -> None:
        self._cfg = cfg

    @property
    def capabilities(self) -> SolverCapabilities:
        caps = capabilities_driver_scf_only("custom_external_template")
        return SolverCapabilities(
            backend_id=caps.backend_id,
            supports_molecular_scf=False,
            supports_pbc_scf=caps.supports_pbc_scf,
            supports_pbc_k_mesh=caps.supports_pbc_k_mesh,
            supports_rhf=caps.supports_rhf,
            supports_rohf=caps.supports_rohf,
            supports_uhf=caps.supports_uhf,
            supports_implicit_solvent_ddcosmo=caps.supports_implicit_solvent_ddcosmo,
            supports_qmmm=caps.supports_qmmm,
            supports_restricted_active_space_qubit_hamiltonian=False,
            capability_notes={
                "molecular_scf": "Set supports_molecular_scf=True after implementing run_molecular_mean_field.",
            },
        )

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> CustomExternalIntegralSolver:
        inst = cls(cfg)
        inst.set_physical_data(cfg)
        return inst

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        self._cfg = cfg

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        if periodic:
            return self.run_periodic_mean_field()
        return self.run_molecular_mean_field()

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        raise NotImplementedError(
            "CustomExternalIntegralSolver.run_molecular_mean_field is a template. "
            "Populate this using your backend's SCF result and return MolecularMeanFieldResult."
        )

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        raise NotImplementedError(
            "CustomExternalIntegralSolver.run_periodic_mean_field is a template. "
            "Set supports_pbc_scf=True only after implementing this method."
        )

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError(
            "CustomExternalIntegralSolver.get_integrals is a template hook for MO/AO integrals."
        )

    def build_embedding_input_system(
        self,
        reference: ClassicalMeanFieldReference,
        *,
        representation: str,
    ) -> dict[str, Any]:
        raise NotImplementedError(
            "CustomExternalIntegralSolver.build_embedding_input_system is a template hook for "
            "embedding_input_representation payload exports."
        )


def build_stub_mean_field_result(*, n_mo: int = 1) -> MolecularMeanFieldResult:
    """Tiny helper for template prototyping/tests before real backend wiring."""
    n = max(1, int(n_mo))
    meta = merge_integration_driver_meta(
        {"adapter_template_stub": True},
        backend_tag="custom_external_template",
        kernel_bindings=[
            kernel_binding(
                KERNEL_MEAN_FIELD_SCF,
                provider="custom_external_template",
                implementation_id="template_stub_v1",
                native=True,
                note="Replace with real SCF before production use.",
            )
        ],
        epistemic_bound="Template stub only — not a quantum chemistry calculation.",
    )
    return MolecularMeanFieldResult(
        mf=wrap_mean_field_like(
            backend_tag="custom_external_template",
            raw_mf={"template": "replace_with_backend_handle"},
            e_tot=0.0,
            mo_energy=np.zeros(n, dtype=float),
        ),
        e_tot=0.0,
        mo_energy=np.zeros(n, dtype=float),
        driver_meta=meta,
    )
