"""Backward-compatible integrations re-exports remain importable after chem layer moves."""

from __future__ import annotations


def test_integrations_schmidt_dmet_shim_reexports() -> None:
    from qchem_stack.integrations.schmidt_dmet_self_consistent import (
        FCISchmidtImpuritySolver,
        run_schmidt_density_feedback_cycles,
        run_schmidt_multifragment_density_cycles,
    )

    assert callable(run_schmidt_density_feedback_cycles)
    assert callable(run_schmidt_multifragment_density_cycles)
    assert FCISchmidtImpuritySolver is not None


def test_integrations_rdm_corrections_shim_reexports() -> None:
    from qchem_stack.integrations.rdm_corrections import (
        run_nevpt2_casci_correction,
        run_pyscf_nevpt2_casci_correction,
    )

    assert callable(run_nevpt2_casci_correction)
    assert callable(run_pyscf_nevpt2_casci_correction)
