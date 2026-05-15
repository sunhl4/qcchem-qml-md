"""Precomputed classical bundle adapter.

This solver reads a previously generated classical reference bundle from disk
and surfaces it as :class:`MolecularMeanFieldResult` for pipeline integration.
"""

from __future__ import annotations

from typing import Any

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.precomputed_bundle import molecular_mean_field_result_from_bundle
from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.config import ExperimentConfig


class PrecomputedIntegralSolver:
    """File-backed solver for ``scf.driver='precomputed'``."""

    def __init__(self, cfg: ExperimentConfig) -> None:
        self._cfg = cfg
        self._validate_cfg(cfg)

    @staticmethod
    def _validate_cfg(cfg: ExperimentConfig) -> None:
        if str(cfg.scf.driver).strip().lower() != "precomputed":
            raise ValueError(
                "PrecomputedIntegralSolver requires cfg.scf.driver='precomputed' "
                f"(got {cfg.scf.driver!r})."
            )
        raw = (cfg.scf.precomputed_bundle_path or "").strip()
        if not raw:
            raise ValueError(
                "scf.driver='precomputed' requires scf.precomputed_bundle_path to be non-empty."
            )

    @property
    def capabilities(self) -> SolverCapabilities:
        return SolverCapabilities(
            backend_id="precomputed",
            supports_molecular_scf=True,
            supports_pbc_scf=False,
            supports_rhf=True,
            supports_rohf=True,
            supports_uhf=True,
            supports_implicit_solvent_ddcosmo=False,
            supports_qmmm=False,
            supports_restricted_active_space_qubit_hamiltonian=False,
            supports_projection_fragment_mulliken_hamiltonian=False,
            supports_schmidt_atomic_hamiltonian=False,
            supports_embedding_input_ao_lowdin=False,
            supports_casscf_orbital_audit=False,
            supports_avas_active_space_projection=False,
            supports_rdm_correction_hooks=False,
            supports_rdm_nevpt2_casci=False,
            supports_get_integrals=False,
        )

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> PrecomputedIntegralSolver:
        inst = cls(cfg)
        inst.set_physical_data(cfg)
        return inst

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        self._validate_cfg(cfg)
        self._cfg = cfg

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        if periodic:
            return self.run_periodic_mean_field()
        return self.run_molecular_mean_field()

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        raw = str(self._cfg.scf.precomputed_bundle_path or "")
        return molecular_mean_field_result_from_bundle(raw, cfg_path=None)

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        raise NotImplementedError("PrecomputedIntegralSolver does not implement periodic SCF.")

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError(
            "PrecomputedIntegralSolver.get_integrals is unavailable. "
            "Provide pre_quantum_input.qubit_hamiltonian in the bundle or use live backends."
        )

    def build_embedding_input_system(
        self,
        reference: ClassicalMeanFieldReference,
        *,
        representation: str,
    ) -> dict[str, Any]:
        raise NotImplementedError(
            "PrecomputedIntegralSolver does not implement AO/Lowdin embedding input payloads."
        )
