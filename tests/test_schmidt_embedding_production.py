"""Schmidt atomic production embedding: PySCF-optional integration tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.embedding.schmidt_production import build_schmidt_impurity_integrals
from qchem_stack.chem.hamiltonian import qubit_hamiltonian_from_spatial_chemist_integrals
from qchem_stack.config import (
    ActiveSpaceSpec,
    BackendSpecConfig,
    ExperimentConfig,
    MoleculeSpec,
    QuantumSpec,
    SCFSpec,
)
from tests.embedding_nested import embedding_dmet, schmidt_embedding_dmet
from tests.fixtures.classical_reference import pyscf_rhf_from_config


def test_embedding_spec_rejects_schmidt_with_uniform_toy() -> None:
    with pytest.raises(ValueError, match="schmidt_atomic_production"):
        embedding_dmet(
            fragment_labels=["a", "b"],
            hamiltonian_source="schmidt_atomic_production",
            schmidt={"fragment_atom_indices": [0]},
            uniform_multifragment_toy=True,
        )


def test_embedding_spec_rejects_schmidt_indices_and_groups_together() -> None:
    with pytest.raises(ValueError, match="not both"):
        embedding_dmet(
            fragment_labels=["a", "b"],
            hamiltonian_source="schmidt_atomic_production",
            schmidt={
                "fragment_atom_indices": [0],
                "multi_fragment_atom_groups": [[0, 1], [2, 3]],
            },
        )


def test_embedding_spec_schmidt_pf_vqe_maxiter_bounds() -> None:
    with pytest.raises(ValueError, match="per_fragment_vqe_maxiter"):
        schmidt_embedding_dmet(
            fragment_labels=["a"],
            fragment_atom_indices=[0],
            per_fragment_vqe_maxiter=0,
        )


def test_qubit_hamiltonian_from_spatial_integrals_shape() -> None:
    import numpy as np

    h1 = np.eye(2)
    h2 = np.zeros((2, 2, 2, 2))
    qh = qubit_hamiltonian_from_spatial_chemist_integrals(0.0, h1, h2, 2)
    assert qh.n_qubits == 4
    assert qh.meta["n_active_orbitals"] == 2


def test_schmidt_density_feedback_accepts_psi4_backend_tag() -> None:
    import numpy as np

    from qchem_stack.chem.bridges.ao_basis_view import AOBasisView
    from qchem_stack.chem.embedding.schmidt_dmet_self_consistent import (
        _initial_ao_density_state,
        _schmidt_feedback_reference,
    )

    class _Psi4AOStub:
        backend_tag = "psi4"

        def overlap_ao(self) -> np.ndarray:
            return np.eye(2, dtype=float)

        def make_rdm1_ao(self) -> np.ndarray:
            return np.eye(2, dtype=float)

    class _Psi4RefStub:
        def __init__(self) -> None:
            self.driver_meta = {"upstream_classical_software_tag": "psi4"}

        def backend_tag(self) -> str:
            return "psi4"

        def ao_basis_view(self) -> AOBasisView:
            return _Psi4AOStub()  # type: ignore[return-value]

    ref = _Psi4RefStub()
    out = _schmidt_feedback_reference(ref, context="test")  # type: ignore[arg-type]
    assert out is ref
    S, D, nel = _initial_ao_density_state(ref)  # type: ignore[arg-type]
    assert S.shape == (2, 2)
    assert D.shape == (2, 2)
    assert nel == 2


def _have_pyscf() -> bool:
    try:
        import pyscf  # noqa: F401

        return True
    except ImportError:
        return False


def _as_reference(rhf) -> ClassicalMeanFieldReference:
    return ClassicalMeanFieldReference(
        mf=rhf.mf,
        e_tot=float(rhf.e_tot),
        mo_energy=rhf.mo_energy,
        molecular_system=rhf.molecular_system,
        driver_meta=dict(rhf.driver_meta),
    )


def _quantum_vqe(*, depth: int = 1, maxiter: int = 40) -> QuantumSpec:
    return QuantumSpec.model_validate(
        {
            "algorithm": "vqe",
            "vqe": {"depth": depth, "maxiter": maxiter},
            "pauli": {"use_protocol": False},
        }
    )


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_build_schmidt_h2_single_atom_fragment() -> None:
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="schmidt_build",
        random_seed=0,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
    )
    rhf = pyscf_rhf_from_config(cfg)
    model = build_schmidt_impurity_integrals(
        _as_reference(rhf),
        fragment_atom_indices=[0],
        n_bath_orbitals=1,
        max_impurity_spatial_orbitals=8,
    )
    assert model.n_spatial_orbitals == 2
    assert model.n_fragment_spatial_orbitals == 1
    assert model.n_bath_spatial_orbitals == 1
    assert model.meta.get("schema") == "schmidt_impurity_integrals_v1"


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_pipeline_schmidt_production_with_bath_sidecar_json() -> None:
    root = Path(__file__).resolve().parents[1]
    sidecar = root / "configs" / "schmidt_bath_sidecar_toy.json"
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="schmidt_sidecar",
        random_seed=2,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=_quantum_vqe(maxiter=40),
        embedding=schmidt_embedding_dmet(
            fragment_labels=["frag0"],
            fragment_atom_indices=[0],
            n_bath_spatial=1,
            max_impurity_spatial_orbitals=8,
            attach_fci_reference=False,
            bath_sidecar_json_path=str(sidecar),
        ),
    )
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    out = run_pipeline_sync(cfg, cfg_path=root / "configs" / "example_h2.yaml")
    wf = out.get("embedding_workflow") or {}
    sc = wf.get("schmidt_bath_sidecar_v1")
    assert isinstance(sc, dict)
    assert sc.get("schema") == "schmidt_bath_sidecar_v1"


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_pipeline_schmidt_production_smoke() -> None:
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="schmidt_pipe",
        random_seed=2,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=_quantum_vqe(maxiter=40),
        embedding=schmidt_embedding_dmet(
            fragment_labels=["frag0"],
            fragment_atom_indices=[0],
            n_bath_spatial=1,
            max_impurity_spatial_orbitals=8,
            attach_fci_reference=True,
            fci_reference_max_spatial_orbitals=8,
        ),
    )
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    out = run_pipeline_sync(cfg)
    wf = out.get("embedding_workflow")
    assert wf is not None
    assert wf.get("dmet_hamiltonian_source") == "schmidt_atomic_production"
    hm = out.get("hamiltonian_meta")
    assert isinstance(hm, dict)
    audit = hm.get("schmidt_production_audit")
    assert isinstance(audit, dict)
    assert audit.get("schema") == "schmidt_production_pipeline_v1"
    assert audit.get("fci_impurity_reference") is not None
    ps = out["repro"].get("parity_snapshot", {})
    assert ps.get("dmet_solver_mode") == "schmidt_atomic_production"
    assert isinstance(ps.get("schmidt_embedding_production"), dict)


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_schmidt_density_feedback_two_cycles_audit() -> None:
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="schmidt_fb",
        random_seed=0,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=_quantum_vqe(maxiter=20),
        embedding=schmidt_embedding_dmet(
            fragment_labels=["frag0"],
            fragment_atom_indices=[0],
            n_bath_spatial=1,
            max_impurity_spatial_orbitals=8,
            dmet_max_cycles=2,
            dmet_mixing_alpha=0.4,
            dmet_convergence_tol=1e-9,
            attach_fci_reference=False,
        ),
    )
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    out = run_pipeline_sync(cfg)
    aud = out.get("hamiltonian_meta", {}).get("schmidt_production_audit", {})
    dmet = aud.get("schmidt_dmet_self_consistency")
    assert isinstance(dmet, dict)
    assert dmet.get("schema") == "schmidt_dmet_density_feedback_v1"
    assert int(dmet.get("cycles_executed", 0)) == 2
    sm = out["repro"].get("run_summary", {})
    assert sm.get("schmidt_dmet_max_cycles_yaml") == 2
    assert sm.get("schmidt_dmet_cycles_executed") == 2
    assert "schmidt_dmet_density_feedback" in sm.get("stages_completed", [])


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_pipeline_schmidt_multifragment_h4_smoke() -> None:
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="schmidt_mf",
        random_seed=3,
        molecule=MoleculeSpec(
            symbols=["H", "H", "H", "H"],
            coordinates=[
                [0, 0, 0.0],
                [0, 0, 1.4],
                [0, 0, 2.8],
                [0, 0, 4.2],
            ],
        ),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 4, "n_electrons": 4}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=_quantum_vqe(maxiter=24),
        embedding=schmidt_embedding_dmet(
            fragment_labels=["left", "right"],
            multi_fragment_atom_groups=[[0, 1], [2, 3]],
            multi_primary_fragment_index=0,
            n_bath_spatial=1,
            max_impurity_spatial_orbitals=8,
            dmet_max_cycles=1,
            attach_fci_reference=False,
            run_vqe_on_all_fragments=True,
            per_fragment_vqe_maxiter=12,
        ),
    )
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    out = run_pipeline_sync(cfg)
    wf = out["embedding_workflow"]
    assert "run_schmidt_multifragment_density_cycles" in wf.get(
        "schmidt_dmet_density_feedback_module", ""
    )
    aud = out.get("hamiltonian_meta", {}).get("schmidt_production_audit", {})
    assert aud.get("schmidt_multifragment") is True
    assert aud.get("n_embedding_fragments") == 2
    dmet = aud.get("schmidt_dmet_self_consistency")
    assert dmet.get("schema") == "schmidt_dmet_multifragment_density_feedback_v1"
    assert dmet.get("outer_cycles_executed") == 1
    loop_pub = dmet.get("dmet_self_consistency_loop")
    assert isinstance(loop_pub, dict)
    assert loop_pub.get("sequential_fragment_updates") is True
    assert loop_pub.get("cycles") == 1
    spfv = out.get("schmidt_per_fragment_vqe")
    assert isinstance(spfv, dict)
    assert spfv.get("schema") == "schmidt_per_fragment_vqe_v1"
    assert len(spfv.get("fragments", [])) == 2
    ps = out["repro"].get("parity_snapshot", {})
    assert ps.get("schmidt_multifragment") is True
    summ = ps.get("schmidt_per_fragment_vqe_summary")
    assert isinstance(summ, dict)
    assert summ.get("schema") == "schmidt_per_fragment_vqe_parity_summary_v1"
    assert summ.get("n_fragments") == 2
    assert summ.get("total_nfev", 0) > 0
    sm = out["repro"].get("run_summary", {})
    assert sm.get("schmidt_per_fragment_vqe_in_parity_snapshot") is True
    assert sm.get("schmidt_per_fragment_vqe_n_fragments") == 2
    assert sm.get("schmidt_per_fragment_vqe_total_nfev", 0) > 0
    assert "schmidt_per_fragment_vqe_min_energy_au" in sm
    assert "schmidt_per_fragment_vqe" in sm.get("stages_completed", [])


@pytest.mark.skipif(not _have_pyscf(), reason="PySCF not installed")
def test_pipeline_schmidt_repro_json_serializable() -> None:
    """``repro_json_dumps`` must accept pipeline repro (strict RFC JSON, no ``default=str``)."""
    cfg = ExperimentConfig(
        schema_version="2",
        experiment_id="schmidt_json",
        random_seed=7,
        molecule=MoleculeSpec(
            symbols=["H", "H"], coordinates=[[0, 0, 0], [0, 0, 1.4]], coordinate_unit="bohr"
        ),
        scf=SCFSpec(method="RHF"),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        backend=BackendSpecConfig(provider="statevector"),
        quantum=_quantum_vqe(maxiter=8),
        embedding=schmidt_embedding_dmet(
            fragment_labels=["frag0"],
            fragment_atom_indices=[0],
            n_bath_spatial=1,
            max_impurity_spatial_orbitals=8,
            attach_fci_reference=False,
        ),
    )
    from qchem_stack.orchestration.pipeline import run_pipeline_sync
    from qchem_stack.repro.export import repro_json_dumps

    out = run_pipeline_sync(cfg)
    repro_json_dumps(out["repro"])
