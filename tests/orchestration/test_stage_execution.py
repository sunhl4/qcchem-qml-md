"""Unit tests for ``orchestration.stage_execution`` (mocked, no PySCF)."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

from qchem_stack.chem.solvers.base import SolverCapabilities
from qchem_stack.config import ExperimentConfig
from qchem_stack.exceptions import PipelineError
from qchem_stack.orchestration.run_context import PipelineStageTimer
from qchem_stack.orchestration.stage_execution import (
    PreQuantumStageContext,
    ScfStageContext,
    _require_cas_active_counts,
    build_pre_quantum_stage,
    run_scf_stage,
)
from tests.helpers.h2_yaml import h2_yaml_dict


def _timer() -> PipelineStageTimer:
    return PipelineStageTimer()


def _logger() -> logging.Logger:
    return logging.getLogger("test.stage_execution")


_PRECOMPUTED_SCF = {
    "driver": "precomputed",
    "method": "RHF",
    "precomputed": {"bundle_path": "configs/precomputed_classical_reference_h2.json"},
}


def test_require_cas_active_counts_raises() -> None:
    cfg = ExperimentConfig.model_validate(h2_yaml_dict())
    cfg.active_space.cas.n_orbitals = None
    with pytest.raises(PipelineError, match="n_orbitals and n_electrons"):
        _require_cas_active_counts(cfg)


def test_run_scf_stage_precomputed_skips_refinement() -> None:
    cfg = ExperimentConfig.model_validate(h2_yaml_dict(scf=_PRECOMPUTED_SCF))
    original_id = cfg.experiment_id
    rhf = MagicMock()
    rhf.e_tot = -1.0
    rhf.nuclear_repulsion_au.return_value = 0.1
    rhf.driver_meta = {"energy_accounting_model": "mf_e_tot_direct"}

    refine = MagicMock(side_effect=AssertionError("refine should not run in precomputed mode"))
    context = ScfStageContext(
        is_precomputed_driver_fn=lambda c: c.scf.driver == "precomputed",
        solver_capabilities_fn=lambda c: SolverCapabilities(backend_id="precomputed"),
        run_scf_fn=lambda c: rhf,
        refine_active_space_fn=refine,
        embedding_input_payload_fn=lambda c, ref: None,
    )

    artifacts = run_scf_stage(
        cfg,
        profile=_timer(),
        emit=lambda _m: None,
        logger=_logger(),
        context=context,
    )
    assert artifacts.precomputed_mode is True
    assert artifacts.cfg.experiment_id == original_id
    refine.assert_not_called()


def test_run_scf_stage_validates_caps(monkeypatch: pytest.MonkeyPatch) -> None:
    cfg = ExperimentConfig.model_validate(h2_yaml_dict())
    caps = SolverCapabilities(
        backend_id="mock",
        supports_molecular_scf=False,
    )

    def _raise_validate(_cfg, *, caps: SolverCapabilities) -> None:
        if not caps.supports_molecular_scf:
            raise PipelineError("capability gate failed")

    monkeypatch.setattr(
        "qchem_stack.orchestration.stage_execution.validate_experiment_for_run",
        _raise_validate,
    )
    context = ScfStageContext(
        is_precomputed_driver_fn=lambda c: False,
        solver_capabilities_fn=lambda c: caps,
        run_scf_fn=lambda c: MagicMock(),
        refine_active_space_fn=lambda c, ref: c,
        embedding_input_payload_fn=lambda c, ref: None,
    )

    with pytest.raises(PipelineError, match="capability gate failed"):
        run_scf_stage(
            cfg,
            profile=_timer(),
            emit=lambda _m: None,
            logger=_logger(),
            context=context,
        )


def test_build_pre_quantum_stage_delegates_context() -> None:
    cfg = ExperimentConfig.model_validate(h2_yaml_dict())
    rhf = MagicMock()
    pre_q = MagicMock()
    pre_q.qubit_hamiltonian.n_qubits = 4
    pre_q.qubit_hamiltonian.meta = {"integral_source": "test"}

    hamiltonian_fn = MagicMock(return_value=(pre_q, {"schmidt": True}))
    context = PreQuantumStageContext(
        is_precomputed_driver_fn=lambda c: False,
        precomputed_pre_quantum_input_fn=MagicMock(),
        hamiltonian_with_context_fn=hamiltonian_fn,
    )

    artifacts = build_pre_quantum_stage(
        cfg,
        rhf,
        cfg_path=None,
        profile=_timer(),
        emit=lambda _m: None,
        logger=_logger(),
        context=context,
    )
    hamiltonian_fn.assert_called_once_with(cfg, rhf, None)
    assert artifacts.schmidt_ctx == {"schmidt": True}
    assert artifacts.qh.n_qubits == 4


def test_build_pre_quantum_stage_precomputed_branch() -> None:
    cfg = ExperimentConfig.model_validate(h2_yaml_dict(scf=_PRECOMPUTED_SCF))
    rhf = MagicMock()
    pre_q = MagicMock()
    pre_q.qubit_hamiltonian.n_qubits = 2
    pre_q.qubit_hamiltonian.meta = {}

    precomputed_fn = MagicMock(return_value=pre_q)
    hamiltonian_fn = MagicMock(side_effect=AssertionError("hamiltonian path should not run"))
    context = PreQuantumStageContext(
        is_precomputed_driver_fn=lambda c: True,
        precomputed_pre_quantum_input_fn=precomputed_fn,
        hamiltonian_with_context_fn=hamiltonian_fn,
    )

    artifacts = build_pre_quantum_stage(
        cfg,
        rhf,
        cfg_path=None,
        profile=_timer(),
        emit=lambda _m: None,
        logger=_logger(),
        context=context,
    )
    precomputed_fn.assert_called_once()
    assert artifacts.schmidt_ctx is None
    assert artifacts.pre_quantum_input is pre_q
