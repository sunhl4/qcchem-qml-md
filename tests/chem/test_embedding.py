"""Embedding subsystem tests: projection, ONIOM, Schmidt, deprecations.

Consolidates:
- test_projection_embedding_l1.py
- test_oniom_qm_mm_demo.py
- test_h4_schmidt_multifragment_yaml.py
- test_embedding_legacy_deprecations.py
"""

from __future__ import annotations

import numpy as np
import pytest

from qchem_stack.chem.embedding.projection import ProjectionEmbeddingConfig


class TestProjectionEmbedding:
    """L1 phase D (序 17): Projection embedding config surface."""

    def test_projection_embedding_config_defaults(self) -> None:
        p = ProjectionEmbeddingConfig()
        assert p.low_level == "HF"
        assert p.high_level == "CAS"
        assert p.threshold == 1e-8


class TestONIOMEmbedding:
    """ONIOM two-layer demo: classical MM term in energy_components_v1."""

    @pytest.mark.pyscf
    def test_example_oniom_qm_mm_demo_energy_components_mm_term(self) -> None:
        pytest.importorskip("pyscf")
        from qchem_stack.config import load_experiment_config
        from qchem_stack.orchestration.pipeline import run_pipeline_sync
        from tests.helpers.paths import configs_path

        cfg_path = configs_path("example_oniom_qm_mm_demo.yaml")
        cfg = load_experiment_config(cfg_path)
        assert cfg.embedding.oniom_layers_v1
        out = run_pipeline_sync(cfg, cfg_path=cfg_path)
        ec = out.get("energy_components")
        assert isinstance(ec, dict)
        assert ec.get("schema") == "energy_components_v1"
        mm = ec.get("classical_mm_energy_au")
        assert mm is not None and float(mm) > 0.0
        assert ec.get("oniom_mm_atom_indices") == [2, 3]
        assert ec.get("oniom_qm_atom_indices") == [0, 1]


class TestSchmidtMultifragment:
    """YAML-driven H4 Schmidt multifragment pipeline smoke."""

    @pytest.mark.pyscf
    @pytest.mark.slow
    def test_h4_schmidt_multifragment_yaml_pipeline(self) -> None:
        pytest.importorskip("pyscf")
        from qchem_stack.config import load_experiment_config
        from qchem_stack.config._experiment_validation import validate_pre_quantum_contract
        from qchem_stack.orchestration.pipeline import run_pipeline_sync
        from tests.helpers.paths import configs_path

        p = configs_path("example_h4_schmidt_multifragment.yaml")
        cfg = load_experiment_config(p)
        validate_pre_quantum_contract(cfg)
        out = run_pipeline_sync(cfg, cfg_path=p)
        assert out["pre_quantum_input"]["source"] == "schmidt_atomic_production"
        assert out["pre_quantum_input"]["hamiltonian_branch"] == "schmidt_atomic_production"
        assert out["pre_quantum_input"]["post_variational_embedding_audit_only"] is True
        ps = out["repro"]["parity_snapshot"]
        assert ps.get("schmidt_multifragment") is True
        assert ps.get("pre_quantum_handoff_v1", {}).get("source") == "schmidt_atomic_production"
        spfv = out.get("schmidt_per_fragment_vqe") or {}
        assert spfv.get("schema") == "schmidt_per_fragment_vqe_v1"
        assert len(spfv.get("fragments") or []) == 2


class TestEmbeddingDeprecations:
    """Embedding legacy API deprecation contracts."""

    @pytest.mark.pyscf
    def test_mulliken_mo_populations_on_atoms_via_ao_basis_view(self) -> None:
        pytest.importorskip("pyscf")
        from pyscf import gto, scf

        from qchem_stack.chem.bridges.ao_basis_view import PySCFAOBasisView
        from qchem_stack.chem.embedding.ao_fragment import mulliken_mo_populations_on_atoms

        mol = gto.M(atom="H 0 0 0; H 0 0 1.4", basis="sto-3g")
        mf = scf.RHF(mol)
        mf.kernel()
        mo = np.asarray(mf.mo_coeff, dtype=float)
        ao = PySCFAOBasisView(_mf=mf)
        weights = mulliken_mo_populations_on_atoms(ao, mo, atom_indices=[0, 1])
        assert weights.shape == (mo.shape[1],)
