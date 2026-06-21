"""P4 non-backend gap closure: SCEOM symmetry, ADAPT grad_tol, Pauli shadows, fragment SPI."""

from __future__ import annotations

import pytest

from tests.helpers.paths import configs_path


def test_sceom_symmetry_filtered_partial_generators() -> None:
    from openfermion.ops import QubitOperator

    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.quantum.algorithms.sceom import resolve_sceom_s_generators

    qh = QubitHamiltonian(operator=QubitOperator("Z0 Z1", 0.5), n_qubits=4)
    gens, label = resolve_sceom_s_generators(
        strategy="symmetry_filtered_partial",
        hamiltonian=qh,
        subspace_dim=3,
    )
    assert label == "symmetry_filtered_partial"
    assert gens is not None and len(gens) >= 1


def test_adapt_grad_tol_in_run_summary() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg = load_experiment_config(configs_path("example_h2_adapt_singles_pool.yaml"))
    cfg.quantum.adapt.grad_tol = 0.05
    out = run_pipeline_sync(cfg, cfg_path=configs_path("example_h2_adapt_singles_pool.yaml"))
    rs = out["repro"]["run_summary"]
    assert rs.get("adapt_grad_tol_yaml") == pytest.approx(0.05)
    am = out.get("adapt_meta") or {}
    assert am.get("grad_tol_used") == pytest.approx(0.05)
    assert rs.get("adapt_grad_tol_used") == pytest.approx(0.05)


def test_pauli_protocol_classical_shadows_main_path() -> None:
    pytest.importorskip("pyscf")
    from qchem_stack.config import load_experiment_config
    from qchem_stack.orchestration.pipeline import run_pipeline_sync

    cfg = load_experiment_config(configs_path("example_h2_classical_shadows_stub.yaml"))
    cfg.mitigation.stubs.classical_shadows = True
    cfg.quantum.pauli.use_protocol = True
    out = run_pipeline_sync(cfg, cfg_path=configs_path("example_h2_classical_shadows_stub.yaml"))
    pc = out.get("protocol_counts") or {}
    assert pc.get("classical_shadows_runtime") == "classical_shadows_hamiltonian_expectation"
    assert "classical_shadows_expectation" in pc
    rs = out["repro"]["run_summary"]
    assert "protocol_classical_shadows_expectation" in rs


def test_fragment_solver_registry_builtin() -> None:
    from qchem_stack.chem.embedding.fragment_solvers.registry import (
        list_fragment_solver_ids,
        resolve_fragment_solver,
    )

    assert "vqe_default" in list_fragment_solver_ids()
    solver = resolve_fragment_solver("vqe_default", executor=None, vqe_depth=1, vqe_maxiter=10)
    assert hasattr(solver, "solve")
