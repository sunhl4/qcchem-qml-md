from __future__ import annotations

from qchem_stack.chem.kernels.rdm_corrections import (
    build_rdm_correction_readiness,
    run_rdm_correction,
)
from qchem_stack.chem.rdm_bundle import RDMBundle


def test_readiness_reads_psi4_nevpt2_block() -> None:
    bundle = RDMBundle(
        rdm1_spatial=[[1.0]],
        rdm_basis="spatial_ao_psi4",
        rdm_source="psi4_scf_rdm1",
        spin_model="restricted",
    )
    report = {
        "reference_wavefunction": "casci",
        "kernel_class": "pyscf_mrpt_nevpt2",
        "psi4_nevpt2": {"status": "ok"},
        "nevpt2": {"status": "ok"},
    }
    ready = build_rdm_correction_readiness(
        requested_method="psi4_nevpt2_casci",
        correction_report=report,
        bundle_meta=dict(bundle.metadata),
    )
    assert ready["nevpt2_status"] == "ok"
    assert ready["nevpt2_pyscf_status"] == "ok"


def test_readiness_stub_nevpt2_not_run() -> None:
    bundle = RDMBundle(
        rdm1_spatial=[[1.0]], rdm_basis="test", rdm_source="test", spin_model="restricted"
    )
    report = run_rdm_correction("stub_nevpt2", bundle)
    ready = build_rdm_correction_readiness(
        requested_method="stub_nevpt2", correction_report=report, bundle_meta=dict(bundle.metadata)
    )
    assert ready["nevpt2_status"] == "not_run"
