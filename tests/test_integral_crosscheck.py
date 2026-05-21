from __future__ import annotations

from unittest.mock import MagicMock, patch

import numpy as np

from qchem_stack.chem.bridges.canonical_integral_pack import CanonicalActiveSpaceIntegralPack
from qchem_stack.chem.integration.crosscheck import maybe_attach_integral_crosscheck
from qchem_stack.chem.restricted_integral_operator import (
    RestrictedActiveSpaceIntegralOperatorCompact,
)
from qchem_stack.config import ExperimentConfig


def _minimal_cfg() -> ExperimentConfig:
    return ExperimentConfig.model_validate(
        {
            "schema_version": "2",
            "experiment_id": "xchk",
            "random_seed": 0,
            "molecule": {
                "symbols": ["H", "H"],
                "coordinates": [[0.0, 0.0, 0.0], [0.0, 0.0, 1.4]],
                "coordinate_unit": "bohr",
                "charge": 0,
                "multiplicity": 1,
                "basis": "sto-3g",
            },
            "scf": {"driver": "psi4", "method": "RHF"},
            "active_space": {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
            },
            "backend": {
                "name": "statevector_sim",
                "provider": "statevector",
                "shots_per_circuit": 1,
                "qiskit_mode": "statevector",
                "ionstack_endpoint": None,
                "meta": {},
            },
            "mitigation": {
                "zne": {"enabled": False},
                "pmsv": {"enabled": False},
            },
            "compiler": {"optimization_level": 0},
            "quantum": {
                "algorithm": "vqe",
                "variational": {"ansatz": "uccsd"},
                "pauli": {"use_protocol": False},
                "vqe": {"maxiter": 1},
            },
            "embedding": {"mode": "none"},
            "chemistry_extended": {"post_hf": {"integral_crosscheck": "pyscf_casci"}},
        }
    )


def test_integral_crosscheck_attaches_audit_block() -> None:
    cfg = _minimal_cfg()
    ref = MagicMock()
    ref.backend_tag.return_value = "psi4"
    ref.e_tot = -1.0
    ref.mo_energy = np.array([-0.5, 0.1], dtype=float)
    ref.molecule = MagicMock()
    ref.driver_meta = {}
    compact = RestrictedActiveSpaceIntegralOperatorCompact(
        constant=-1.0,
        h1_active_mo=np.eye(2),
        eri_active_mo_compact=np.zeros((2, 2, 2, 2)),
        n_active_orbitals=2,
        n_active_electrons=2,
        symmetry_meta={},
        storage_schema="mock_v1",
    )
    pack = CanonicalActiveSpaceIntegralPack(compact=compact, provenance={})
    shadow_pack = CanonicalActiveSpaceIntegralPack(compact=compact, provenance={})
    with (
        patch(
            "qchem_stack.chem.integration.crosscheck.CanonicalActiveSpaceIntegralPack.from_classical_reference",
            return_value=shadow_pack,
        ),
        patch(
            "qchem_stack.chem.integration.crosscheck.build_pyscf_rhf_shadow",
            return_value=MagicMock(),
        ),
    ):
        maybe_attach_integral_crosscheck(cfg, ref, primary_pack=pack)
    assert ref.driver_meta.get("integral_crosscheck_casci_v1") is not None
