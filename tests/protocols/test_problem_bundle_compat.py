"""``ChemistryProblemBundle`` snapshot from :class:`RestrictedActiveSpaceQuantumProblem`."""

from __future__ import annotations

import pytest

from tests.helpers.paths import configs_path

pytest.importorskip("pyscf")

from qchem_stack.chem.molecular_problem_build import (
    restricted_active_space_quantum_problem_from_config,
)
from qchem_stack.chem.problem_bundle import ChemistryProblemBundle
from qchem_stack.config import load_experiment_config
from tests.fixtures.classical_reference import (
    classical_reference_from_config,
    pyscf_rhf_from_config,
)


def test_bundle_from_ras_problem_roundtrip_public_dump() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    ref = classical_reference_from_config(cfg)
    prob = restricted_active_space_quantum_problem_from_config(cfg, reference=ref)
    b = ChemistryProblemBundle.from_restricted_active_space_problem(prob, reference=ref)
    assert b.reference_energy_hf_au == pytest.approx(float(rhf.e_tot))
    assert b.backend_driver_meta.get("driver_family") == "pyscf"
    assert b.classical_mean_field_snapshot is ref
    pub = b.model_dump_public()
    assert pub["schema"] == "chemistry_problem_bundle_v1"
    assert pub["fermion_space"]["n_spin_orbitals"] == 4


def test_bundle_accepts_classical_reference_directly() -> None:
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    rhf = pyscf_rhf_from_config(cfg)
    ref = classical_reference_from_config(cfg)
    prob = restricted_active_space_quantum_problem_from_config(cfg, reference=ref)
    b = ChemistryProblemBundle.from_restricted_active_space_problem(prob, reference=ref)
    assert b.classical_mean_field_snapshot is ref
    assert b.reference_energy_hf_au == pytest.approx(float(rhf.e_tot))
