from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.chem.integration.checklist import run_integration_checklist
from qchem_stack.chem.integration.meta_schema import (
    append_kernel_bindings,
    merge_integration_driver_meta,
)
from qchem_stack.chem.kernels.catalog import (
    KERNEL_MEAN_FIELD_SCF,
    kernel_binding,
    list_known_kernels,
)
from qchem_stack.chem.solvers.custom_solver_template import CustomExternalIntegralSolver


def test_merge_integration_driver_meta_kernel_bindings() -> None:
    meta = merge_integration_driver_meta(
        {"foo": 1},
        backend_tag="demo",
        kernel_bindings=[
            kernel_binding(
                KERNEL_MEAN_FIELD_SCF, provider="demo", implementation_id="demo_scf_v1", native=True
            )
        ],
        epistemic_bound="test only",
    )
    assert meta["driver_meta_schema_version"] == 1
    assert meta["upstream_classical_software_tag"] == "demo"
    assert meta["kernel_bindings"][0]["kernel_id"] == KERNEL_MEAN_FIELD_SCF
    assert meta["epistemic_bound"] == "test only"


def test_append_kernel_bindings_dedupes_by_kernel_id() -> None:
    meta: dict = {}
    b1 = kernel_binding(KERNEL_MEAN_FIELD_SCF, provider="a", implementation_id="v1", native=True)
    b2 = kernel_binding(KERNEL_MEAN_FIELD_SCF, provider="b", implementation_id="v2", native=False)
    append_kernel_bindings(meta, [b1])
    append_kernel_bindings(meta, [b2])
    assert len(meta["kernel_bindings"]) == 1
    assert meta["kernel_bindings"][0]["implementation_id"] == "v2"


def test_known_kernels_catalog() -> None:
    ids = list_known_kernels()
    assert "casci_active_integrals" in ids
    assert "avas_projection" in ids


def test_psi4_capabilities_include_notes() -> None:
    pytest.importorskip("psi4")
    from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver
    from qchem_stack.config import load_experiment_config

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2_psi4_rhf_sto3g.yaml")
    caps = Psi4IntegralSolver.from_experiment_config(cfg).capabilities
    assert caps.supports_pbc_k_mesh is False
    assert "avas_active_space_projection" in caps.capability_notes


def test_integration_presets_public_exports() -> None:
    from qchem_stack.chem.integration import (
        capabilities_precomputed_offline,
        capabilities_psi4_production,
        capabilities_pyscf_production,
    )

    assert capabilities_pyscf_production().backend_id == "pyscf"
    assert capabilities_psi4_production().backend_id == "psi4"
    assert capabilities_precomputed_offline().backend_id == "precomputed"


def test_integration_checklist_template_solver() -> None:
    sol = CustomExternalIntegralSolver(
        cfg=type("_Cfg", (), {"scf": type("_S", (), {"driver": "custom"})()})()
    )
    rep = run_integration_checklist(sol, run_mean_field=False)
    assert rep.backend_id == "custom_external_template"
    assert rep.ready_for_smoke
