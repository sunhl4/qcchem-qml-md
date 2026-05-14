"""Restricted MO integral compact container vs dense CASCI bridge."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")

from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver, active_space_integrals
from qchem_stack.chem.restricted_integral_operator import (
    RestrictedActiveSpaceIntegralOperatorCompact,
    interaction_operator_to_dataframe,
)
from qchem_stack.config import load_experiment_config


def test_compact_restores_same_dense_quantities_as_active_space_integrals() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    rhf = drv.run_rhf()
    na, ne = 2, 2
    c0, h1_ref, h2_ref = active_space_integrals(rhf, na, ne)
    compact = RestrictedActiveSpaceIntegralOperatorCompact.from_pyscf_rhf(
        rhf, n_active_orbitals=na, n_active_electrons=ne
    )
    assert compact.constant == pytest.approx(c0)
    np.testing.assert_allclose(compact.h1_active_mo, h1_ref, atol=1e-10)
    from qchem_stack.chem.integral_convention import spatial_mo_eri_pyscf_to_openfermion_mo_ordering

    h2_from_compact = spatial_mo_eri_pyscf_to_openfermion_mo_ordering(
        compact.dense_h2_chemist_spatial()
    )
    np.testing.assert_allclose(h2_from_compact, h2_ref, atol=1e-10)


def test_df_mo_and_spin_sectors_have_rows() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    rhf = drv.run_rhf()
    compact = RestrictedActiveSpaceIntegralOperatorCompact.from_pyscf_rhf(
        rhf, n_active_orbitals=2, n_active_electrons=2
    )
    mo_df = compact.df_mo_integrals(max_two_body=500)
    assert len(mo_df) >= 3
    assert "sector" in mo_df.columns
    spin_df = interaction_operator_to_dataframe(
        compact.to_interaction_operator(), max_spinorb_two_body=500
    )
    assert len(spin_df) >= 3


def test_ao_system_summary_df_smoke() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    drv = PySCFDriver.from_config(cfg)
    ao = drv.get_system_ao(run_hf=True)
    dfa = ao.ao_driver_summary_df()
    assert list(dfa.columns) == ["quantity", "value"]
    assert int(dfa.loc[dfa["quantity"] == "nao_nr", "value"].iloc[0]) >= 2
