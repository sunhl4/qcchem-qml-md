"""Multi-fragment DMET integration (uses existing YAML fixtures)."""

from __future__ import annotations

import pytest

from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.embedding_strategies import run_dmet_fragment_solve_if_requested
from tests.helpers.paths import configs_path


def test_dmet_multifragment_shared_hamiltonian_ledger_shape() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    p = configs_path("example_h4_dmet_fragment_exact_small.yaml")
    if not p.is_file():
        pytest.skip("example_h4_dmet_fragment_exact_small.yaml missing")
    cfg = load_experiment_config(p)
    out = run_pipeline_sync(cfg, cfg_path=p)
    led = out.get("dmet_fragment_solve")
    assert isinstance(led, dict)
    assert led.get("multifragment_shared_global_hamiltonian") is True
    assert len(led.get("fragments") or []) >= 2


def test_run_dmet_fragment_solve_skips_non_dmet_mode(h2_config) -> None:
    from openfermion.ops import QubitOperator

    from qchem_stack.chem.fermion import FermionSpace
    from qchem_stack.chem.hamiltonian import QubitHamiltonian

    out: dict = {}
    op = QubitOperator(((0, "Z"),), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=1, fermion_space=FermionSpace(1, 1))
    run_dmet_fragment_solve_if_requested(h2_config, qh, exe=None, out=out)
    assert "dmet_fragment_solve" not in out
