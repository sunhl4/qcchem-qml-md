"""Cross-backend alignment tests (require PySCF + Psi4; run with ``pytest -m psi4``)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from qchem_stack.chem.active_space.avas_projection import apply_avas_projection
from qchem_stack.chem.bridges.pyscf_shadow_reference import build_pyscf_rhf_shadow
from qchem_stack.chem.embedding.impurity_eri import impurity_eri_chemist
from qchem_stack.chem.embedding.schmidt_dmet_self_consistent import (
    run_schmidt_density_feedback_cycles,
)
from qchem_stack.chem.embedding.schmidt_production import build_schmidt_impurity_integrals
from qchem_stack.chem.kernels.rdm_corrections import run_nevpt2_casci_correction
from qchem_stack.chem.solvers import create_solver
from qchem_stack.config import load_experiment_config
from qchem_stack.contracts.schema_ids import SCHMIDT_DMET_DENSITY_FEEDBACK_V1
from qchem_stack.orchestration.scf_stage import run_scf_reference

PSI4_PYSCF_ETOT_ATOL = 0.0002
PSI4_PYSCF_MO_MAX_ABS = 0.15
PSI4_PYSCF_NEVPT2_RTOL = 0.05
PSI4_PYSCF_NEVPT2_ATOL = 0.0001


def _h2_cfg(root: Path, *, driver: str):
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    return cfg.model_copy(update={"scf": cfg.scf.model_copy(update={"driver": driver})})


@pytest.mark.psi4
@pytest.mark.pyscf
def test_psi4_pyscf_h2_scf_energy_and_mo_parity() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    ref_py = run_scf_reference(_h2_cfg(root, driver="pyscf"))
    ref_psi = run_scf_reference(_h2_cfg(root, driver="psi4"))
    assert abs(float(ref_py.e_tot) - float(ref_psi.e_tot)) < PSI4_PYSCF_ETOT_ATOL
    mo_py = np.asarray(ref_py.ao_basis_view().mo_coeff_ao(), dtype=float)
    mo_psi = np.asarray(ref_psi.ao_basis_view().mo_coeff_ao(), dtype=float)
    assert mo_py.shape == mo_psi.shape
    assert float(np.max(np.abs(mo_py - mo_psi))) < PSI4_PYSCF_MO_MAX_ABS


@pytest.mark.psi4
@pytest.mark.pyscf
def test_psi4_pyscf_nevpt2_casci_correction_near_parity() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    cfg_py = _h2_cfg(root, driver="pyscf")
    cfg_psi = _h2_cfg(root, driver="psi4")
    ref_py = run_scf_reference(cfg_py)
    ref_psi = run_scf_reference(cfg_psi)
    na, ne = (2, 2)
    rep_py = run_nevpt2_casci_correction(ref_py, na, ne, cfg=cfg_py)
    rep_psi = run_nevpt2_casci_correction(ref_psi, na, ne, cfg=cfg_psi)
    assert rep_py["status"] == "ok"
    assert rep_psi["status"] == "ok"
    e_py = float(rep_py["energy_correction_au"])
    e_psi = float(rep_psi["energy_correction_au"])
    assert abs(e_py - e_psi) <= max(
        PSI4_PYSCF_NEVPT2_ATOL, PSI4_PYSCF_NEVPT2_RTOL * max(abs(e_py), abs(e_psi), 1e-12)
    )


@pytest.mark.psi4
@pytest.mark.pyscf
def test_psi4_avas_shadow_mo_shape_and_finite_energy() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_psi4_avas.yaml")
    ref = run_scf_reference(cfg)
    mo_before = np.asarray(ref.ao_basis_view().mo_coeff_ao(), dtype=float).copy()
    apply_avas_projection(cfg, ref)
    mo_after = np.asarray(ref.ao_basis_view().mo_coeff_ao(), dtype=float)
    assert mo_after.shape == mo_before.shape
    assert np.all(np.isfinite(mo_after))
    shadow = build_pyscf_rhf_shadow(cfg, ref, run_scf_if_needed=False)
    assert shadow.mo_coeff.shape == mo_after.shape
    from qchem_stack.chem.active_space.pyscf_active_space_hooks import (
        RESOLVED_ACTIVE_SPACE_META_KEY,
    )

    meta = ref.driver_meta.get(RESOLVED_ACTIVE_SPACE_META_KEY) or {}
    assert meta.get("source") == "pyscf_mcscf_avas_on_imported_mo_v1"


@pytest.mark.psi4
@pytest.mark.pyscf
def test_psi4_schmidt_impurity_eri_matches_pyscf_h2() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    cfg_py = _h2_cfg(root, driver="pyscf")
    cfg_psi = _h2_cfg(root, driver="psi4")
    ref_py = run_scf_reference(cfg_py)
    ref_psi = run_scf_reference(cfg_psi)
    frag = [0]
    model_py = build_schmidt_impurity_integrals(
        ref_py, fragment_atom_indices=frag, n_bath_orbitals=1, max_impurity_spatial_orbitals=2
    )
    model_psi = build_schmidt_impurity_integrals(
        ref_psi, fragment_atom_indices=frag, n_bath_orbitals=1, max_impurity_spatial_orbitals=2
    )
    assert model_py.h2.shape == model_psi.h2.shape
    assert float(np.max(np.abs(model_py.h2 - model_psi.h2))) < 0.2


@pytest.mark.psi4
@pytest.mark.pyscf
def test_psi4_schmidt_density_feedback_cycles_runs() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    ref_psi = run_scf_reference(_h2_cfg(root, driver="psi4"))
    _model, report, _d_final = run_schmidt_density_feedback_cycles(
        ref_psi,
        fragment_atom_indices=[0],
        n_bath_orbitals=1,
        max_impurity_spatial_orbitals=6,
        max_cycles=2,
        mixing_alpha=0.35,
        convergence_tol=1e-3,
    )
    assert report["schema"] == SCHMIDT_DMET_DENSITY_FEEDBACK_V1
    assert len(report["history"]) >= 1


@pytest.mark.psi4
def test_psi4_pbc_kmesh_gt_one_rejected() -> None:
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    cfg = cfg.model_copy(
        update={
            "scf": cfg.scf.model_copy(update={"driver": "psi4"}),
            "chemistry_extended": cfg.chemistry_extended.model_copy(
                update={
                    "pbc": cfg.chemistry_extended.pbc.model_copy(
                        update={
                            "cell_vectors_bohr": [
                                [10.0, 0.0, 0.0],
                                [0.0, 10.0, 0.0],
                                [0.0, 0.0, 10.0],
                            ],
                            "kpoint_mesh": [2, 1, 1],
                        }
                    ),
                }
            ),
        }
    )
    solver = create_solver(cfg)
    with pytest.raises(NotImplementedError, match="Gamma-only"):
        solver.compute_mean_field(periodic=True)


@pytest.mark.psi4
@pytest.mark.pyscf
def test_psi4_impurity_eri_direct_parity_h2() -> None:
    pytest.importorskip("pyscf")
    pytest.importorskip("psi4")
    root = Path(__file__).resolve().parents[1]
    ref_py = run_scf_reference(_h2_cfg(root, driver="pyscf"))
    ref_psi = run_scf_reference(_h2_cfg(root, driver="psi4"))
    c = np.asarray(ref_py.ao_basis_view().mo_coeff_ao(), dtype=float)[:, :2]
    eri_py = impurity_eri_chemist(
        ref_py.ao_basis_view(), c, molecular_system=ref_py.molecular_system
    )
    eri_psi = impurity_eri_chemist(
        ref_psi.ao_basis_view(), c, molecular_system=ref_psi.molecular_system
    )
    assert eri_py.shape == eri_psi.shape
    assert float(np.max(np.abs(eri_py - eri_psi))) < 0.25
