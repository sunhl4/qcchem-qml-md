"""Pin deprecation warnings for APIs scheduled for removal in v0.8.0."""

from __future__ import annotations

import pytest


def test_molecular_hamiltonian_from_classical_reference_deprecated() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.chem.bridges.facade import classical_mean_field_via_solver_bridge
    from qchem_stack.chem.hamiltonian_build import molecular_hamiltonian_from_classical_reference
    from qchem_stack.config import load_experiment_config

    cfg = load_experiment_config("configs/example_h2.yaml")
    ref = classical_mean_field_via_solver_bridge(cfg)
    ncas = int(cfg.active_space.cas.n_orbitals or 2)
    nelec = int(cfg.active_space.cas.n_electrons or 2)
    with (
        pytest.warns(DeprecationWarning, match="molecular_hamiltonian_from_classical_reference"),
        pytest.raises(AttributeError),
    ):
        molecular_hamiltonian_from_classical_reference(ref, ncas, nelec)


def test_integrations_dmet_self_consistent_import_deprecated() -> None:
    import importlib
    import sys

    mod_name = "qchem_stack.integrations.dmet_self_consistent"
    sys.modules.pop(mod_name, None)
    with pytest.warns(DeprecationWarning, match="integrations.dmet_self_consistent"):
        dmet_shim = importlib.import_module(mod_name)

    assert dmet_shim.DMETSelfConsistencyLoop is not None


def test_apply_backend_profile_deprecated() -> None:
    from qchem_stack.backends.profiles import apply_backend_profile
    from qchem_stack.config import load_experiment_config

    cfg = load_experiment_config("configs/example_h2.yaml")
    with pytest.warns(DeprecationWarning, match="apply_backend_profile"):
        apply_backend_profile(cfg, "statevector")
