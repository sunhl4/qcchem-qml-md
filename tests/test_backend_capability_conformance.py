from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.embedding.projection_hamiltonian import (
    molecular_hamiltonian_fragment_mulliken_projection,
)
from qchem_stack.chem.embedding.schmidt_dmet_self_consistent import (
    run_schmidt_density_feedback_cycles,
)
from qchem_stack.chem.embedding.schmidt_production import (
    SchmidtProductionError,
    build_schmidt_impurity_integrals,
)
from qchem_stack.chem.integrals.exporter_protocol import ActiveSpaceIntegralExporter
from qchem_stack.chem.integrals.exporter_registry import (
    get_active_space_integral_exporter,
    list_active_space_integral_exporters,
    register_active_space_integral_exporter,
)
from qchem_stack.chem.integrals.pyscf_active_space_exporter import PySCFActiveSpaceIntegralExporter
from qchem_stack.chem.kernels.rdm_corrections import run_pyscf_nevpt2_casci_correction
from qchem_stack.chem.solvers import create_solver, register_mock_external_solver
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import load_experiment_config
from qchem_stack.exceptions import EmbeddingError, PipelineError, PreQuantumCapabilityError
from qchem_stack.orchestration.pipeline import run_pipeline_sync


def test_builtin_backend_capability_matrix_smoke() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    cfg.scf.driver = "psi4"
    psi4 = create_solver(cfg).capabilities
    assert psi4.supports_restricted_active_space_qubit_hamiltonian
    assert psi4.supports_projection_fragment_mulliken_hamiltonian
    assert psi4.supports_schmidt_atomic_hamiltonian
    assert psi4.supports_embedding_input_ao_lowdin
    assert psi4.supports_casscf_orbital_audit
    assert psi4.supports_avas_active_space_projection
    assert psi4.supports_rdm_correction_hooks
    assert psi4.supports_rdm_nevpt2_casci
    assert psi4.supports_get_integrals
    assert not psi4.supports_pbc_k_mesh

    pytest.importorskip("pyscf")
    cfg.scf.driver = "pyscf"
    pyscf = create_solver(cfg).capabilities
    assert pyscf.supports_restricted_active_space_qubit_hamiltonian
    assert pyscf.supports_projection_fragment_mulliken_hamiltonian
    assert pyscf.supports_schmidt_atomic_hamiltonian
    assert pyscf.supports_embedding_input_ao_lowdin
    assert pyscf.supports_casscf_orbital_audit
    assert pyscf.supports_avas_active_space_projection
    assert pyscf.supports_rdm_correction_hooks
    assert pyscf.supports_rdm_nevpt2_casci
    assert pyscf.supports_get_integrals
    assert pyscf.supports_pbc_k_mesh

    cfg.scf.driver = "precomputed"
    cfg.scf.precomputed.bundle_path = str(
        root / "configs" / "precomputed_classical_reference_h2.json"
    )
    pre = create_solver(cfg).capabilities
    assert pre.backend_id == "precomputed"
    assert not pre.supports_restricted_active_space_qubit_hamiltonian
    assert "restricted_active_space_qubit_hamiltonian" in pre.capability_notes


def test_canonical_pack_requires_backend_builder() -> None:
    ref = ClassicalMeanFieldReference(
        mf=object(),
        e_tot=0.0,
        mo_energy=np.zeros(1, dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H"],
            coordinates_bohr=np.zeros((1, 3), dtype=float),
            basis="sto-3g",
        ),
        driver_meta={"upstream_classical_software_tag": "unknown_backend"},
    )
    with pytest.raises(PreQuantumCapabilityError, match="No ActiveSpaceIntegralExporter"):
        CanonicalActiveSpaceIntegralPack.from_classical_reference(
            ref,
            n_active_orbitals=1,
            n_active_electrons=0,
        )


def test_rdm_correction_gate_requires_backend_capability() -> None:
    root = Path(__file__).resolve().parents[1]
    p = root / "configs" / "example_decomposition_plugin_toy.yaml"
    cfg = load_experiment_config(p)
    register_mock_external_solver()
    cfg.scf.driver = "mock_external"
    cfg.chemistry_extended.post_hf.rdm_correction_method = "stub_nevpt2"
    with pytest.raises(
        PipelineError, match="rdm_correction_method requires backend RDM extraction support"
    ):
        run_pipeline_sync(cfg, cfg_path=p)


def test_projection_and_schmidt_builders_require_ao_basis_view() -> None:
    ref = ClassicalMeanFieldReference(
        mf=object(),
        e_tot=0.0,
        mo_energy=np.zeros(1, dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H"],
            coordinates_bohr=np.zeros((1, 3), dtype=float),
            basis="sto-3g",
        ),
        driver_meta={"upstream_classical_software_tag": "mock_external"},
    )
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h4_projection_mulliken.yaml")
    with pytest.raises(EmbeddingError, match="requires a mean-field reference with AO basis view"):
        molecular_hamiltonian_fragment_mulliken_projection(ref, cfg)
    with pytest.raises(
        SchmidtProductionError, match="requires a mean-field reference with AO basis view"
    ):
        build_schmidt_impurity_integrals(
            ref,
            fragment_atom_indices=[0],
            n_bath_orbitals=1,
            max_impurity_spatial_orbitals=2,
        )
    with pytest.raises(
        SchmidtProductionError, match="requires a mean-field reference with AO basis view"
    ):
        run_schmidt_density_feedback_cycles(
            ref,
            fragment_atom_indices=[0],
            n_bath_orbitals=1,
            max_impurity_spatial_orbitals=2,
            max_cycles=1,
            mixing_alpha=0.3,
            convergence_tol=1e-4,
        )
    rep = run_pyscf_nevpt2_casci_correction(ref, n_active_orbitals=1, n_active_electrons=0)
    assert rep.get("status") == "failed"
    assert "backend_not_supported" in str((rep.get("pyscf_nevpt2") or {}).get("reason"))


def _mock_external_reference_with_ao_stub(*, n_atom: int = 2) -> ClassicalMeanFieldReference:
    from qchem_stack.chem.bridges.ao_basis_view import AOBasisView

    class _MockAOStub:
        backend_tag = "mock_external"

        def __init__(self, n_atoms: int) -> None:
            self._n_atom = n_atoms

        @property
        def n_atom(self) -> int:
            return self._n_atom

        @property
        def nao(self) -> int:
            return self._n_atom

        def aoslice_by_atom(self) -> list[tuple[int, int]]:
            return [(i, i + 1) for i in range(self._n_atom)]

        def overlap_ao(self) -> np.ndarray:
            return np.eye(self.nao, dtype=float)

        def hcore_ao(self) -> np.ndarray:
            return np.eye(self.nao, dtype=float)

        def fock_ao(self, *, density_ao: np.ndarray | None = None) -> np.ndarray:
            return np.eye(self.nao, dtype=float)

        def mo_coeff_ao(self) -> np.ndarray:
            return np.eye(self.nao, dtype=float)

        def make_rdm1_ao(self) -> np.ndarray:
            return np.eye(self.nao, dtype=float)

        def energy_nuc_au(self) -> float:
            return 0.0

        def reference_class_name(self) -> str:
            return "RHF"

        def raw_handle(self) -> object:
            return object()

    class MockExternalReference(ClassicalMeanFieldReference):
        def __init__(self, *, n_atoms: int) -> None:
            super().__init__(
                mf=object(),
                e_tot=0.0,
                mo_energy=np.zeros(n_atoms, dtype=float),
                molecular_system=MolecularSystem(
                    symbols=["H"] * n_atoms,
                    coordinates_bohr=np.zeros((n_atoms, 3), dtype=float),
                    basis="sto-3g",
                ),
                driver_meta={"upstream_classical_software_tag": "mock_external"},
            )
            self._ao_stub = _MockAOStub(n_atoms)

        def ao_basis_view(self) -> AOBasisView:
            return self._ao_stub  # type: ignore[return-value]

    return MockExternalReference(n_atoms=n_atom)


def test_schmidt_and_projection_pass_ao_basis_view_gate_for_mock_backend() -> None:
    ref = _mock_external_reference_with_ao_stub()
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h4_projection_mulliken.yaml")

    with pytest.raises(Exception) as schmidt_exc:
        build_schmidt_impurity_integrals(
            ref,
            fragment_atom_indices=[0],
            n_bath_orbitals=1,
            max_impurity_spatial_orbitals=4,
        )
    assert "supports backend pyscf or psi4" not in str(schmidt_exc.value)
    assert "requires a mean-field reference with AO basis view" not in str(schmidt_exc.value)

    with pytest.raises(Exception) as proj_exc:
        molecular_hamiltonian_fragment_mulliken_projection(ref, cfg)
    assert "requires backend pyscf or psi4" not in str(proj_exc.value)
    assert "requires a mean-field reference with AO basis view" not in str(proj_exc.value)


def test_patch_experiment_active_space_resolution_applies_psi4_driver_meta() -> None:
    from qchem_stack.chem.active_space.backend_hooks import patch_experiment_active_space_resolution
    from qchem_stack.chem.active_space.resolution import RESOLVED_ACTIVE_SPACE_META_KEY

    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    ref = ClassicalMeanFieldReference(
        mf=object(),
        e_tot=0.0,
        mo_energy=np.zeros(1, dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H", "H"],
            coordinates_bohr=np.zeros((2, 3), dtype=float),
            basis="sto-3g",
        ),
        driver_meta={
            "upstream_classical_software_tag": "psi4",
            RESOLVED_ACTIVE_SPACE_META_KEY: {
                "n_active_orbitals": 1,
                "n_active_electrons": 2,
            },
        },
    )
    patched = patch_experiment_active_space_resolution(cfg, ref)
    assert int(patched.active_space.cas.n_orbitals) == 1
    assert int(patched.active_space.cas.n_electrons) == 2


def test_schmidt_pre_quantum_uses_capability_and_ao_basis_view_not_backend_whitelist() -> None:
    from qchem_stack.chem.pre_quantum_schmidt import schmidt_hamiltonian_and_context
    from qchem_stack.chem.solvers.base import SolverCapabilities

    ref = ClassicalMeanFieldReference(
        mf=object(),
        e_tot=0.0,
        mo_energy=np.zeros(1, dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H"],
            coordinates_bohr=np.zeros((1, 3), dtype=float),
            basis="sto-3g",
        ),
        driver_meta={"upstream_classical_software_tag": "mock_external"},
    )
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h4_schmidt_multifragment.yaml")
    caps = SolverCapabilities(
        backend_id="mock_external",
        supports_schmidt_atomic_hamiltonian=True,
    )
    with pytest.raises(SchmidtProductionError, match="AO basis view"):
        schmidt_hamiltonian_and_context(cfg, ref, backend_caps=caps)


def test_pyscf_active_space_exporter_requires_pyscf_backend_tag() -> None:
    ref = ClassicalMeanFieldReference(
        mf=object(),
        e_tot=0.0,
        mo_energy=np.zeros(1, dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H"],
            coordinates_bohr=np.zeros((1, 3), dtype=float),
            basis="sto-3g",
        ),
        driver_meta={"upstream_classical_software_tag": "psi4"},
    )
    with pytest.raises(ValueError, match="expected backend_tag='pyscf'"):
        PySCFActiveSpaceIntegralExporter().build_canonical_pack(
            ref,
            n_active_orbitals=1,
            n_active_electrons=0,
        )


def test_exporter_registry_lists_and_accepts_custom_backend() -> None:
    class _DummyExporter(ActiveSpaceIntegralExporter):
        backend_tag = "dummy"

        def build_canonical_pack(self, reference, *, n_active_orbitals, n_active_electrons):
            raise NotImplementedError

    known = list_active_space_integral_exporters()
    assert "pyscf" in known
    assert "psi4" in known
    register_active_space_integral_exporter("dummy", _DummyExporter())
    known2 = list_active_space_integral_exporters()
    assert "dummy" in known2


def test_exporter_registry_requires_explicit_override() -> None:
    class _ExporterA(ActiveSpaceIntegralExporter):
        backend_tag = "tmp_override"

        def build_canonical_pack(self, reference, *, n_active_orbitals, n_active_electrons):
            raise NotImplementedError

    class _ExporterB(ActiveSpaceIntegralExporter):
        backend_tag = "tmp_override"

        def build_canonical_pack(self, reference, *, n_active_orbitals, n_active_electrons):
            raise NotImplementedError

    register_active_space_integral_exporter("tmp_override", _ExporterA(), allow_override=True)
    with pytest.raises(ValueError, match="already registered"):
        register_active_space_integral_exporter("tmp_override", _ExporterB())
    register_active_space_integral_exporter("tmp_override", _ExporterB(), allow_override=True)
    assert isinstance(get_active_space_integral_exporter("tmp_override"), _ExporterB)
