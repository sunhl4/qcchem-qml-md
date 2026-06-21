"""Qulacs backend executor conformance (optional dependency)."""

from __future__ import annotations

import numpy as np
import pytest

qulacs = pytest.importorskip("qulacs")

from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.backends.factory import executor_from_spec, registered_backend_provider_ids
from qchem_stack.backends.qulacs_executor import QulacsHeaExecutor
from qchem_stack.backends.spec import BackendSpec
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.pipeline import run_pipeline_sync
from qchem_stack.quantum.algorithms.vqe import VQE
from tests.helpers.paths import configs_path


@pytest.mark.parametrize("provider", ["statevector", "qulacs"])
def test_backend_hea_expectation_conformance(provider: str) -> None:
    if provider == "qulacs":
        pytest.importorskip("qulacs")
    h = QubitOperator(((0, "Z"), (1, "Z")), 0.15) + QubitOperator((), 0.05)
    angles = np.linspace(0.1, 0.8, 8)
    ref = StatevectorHeaExecutor().expectation_hea(h, 2, angles, 2)
    ex = executor_from_spec(BackendSpec(name="t", provider=provider))  # type: ignore[arg-type]
    got = ex.expectation_hea(h, 2, angles, 2)
    assert got == pytest.approx(ref, rel=1e-5, abs=1e-5)


def test_qulacs_registered_and_vqe_h2_smoke() -> None:
    assert "qulacs" in registered_backend_provider_ids()
    op = QubitOperator(((0, "Z"), (1, "Z")), 0.2) + QubitOperator((), 0.1)
    qh = QubitHamiltonian(operator=op, n_qubits=2, fermion_space=FermionSpace(4, 2))
    exe = executor_from_spec(BackendSpec(name="qulacs", provider="qulacs"))
    assert isinstance(exe, QulacsHeaExecutor)
    r_q = VQE(qh, depth=1, executor=exe).run(maxiter=80, seed=2)
    r_n = VQE(qh, depth=1).run(maxiter=80, seed=2)
    assert r_q.energy == pytest.approx(r_n.energy, rel=1e-4, abs=1e-4)


def test_qulacs_pipeline_h2_smoke() -> None:
    pytest.importorskip("pyscf")
    cfg = load_experiment_config(configs_path("example_h2.yaml"))
    cfg.backend.provider = "qulacs"
    cfg.backend.name = "qulacs_sim"
    cfg.quantum.vqe.maxiter = 60
    out = run_pipeline_sync(cfg)
    assert out.get("energy_after_variational") is not None
