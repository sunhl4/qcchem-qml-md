"""Excited-state plugin registry dispatch."""

from __future__ import annotations

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.config import ActiveSpaceSpec, ExperimentConfig, MoleculeSpec, QuantumSpec, SCFSpec
from qchem_stack.contracts.schema_ids import (
    EXCITED_QSE_BUNDLE_V1,
    EXCITED_SCEOM_BUNDLE_V1,
    EXCITED_VQD_BUNDLE_V1,
)
from qchem_stack.quantum.excited_plugins.registry import (
    list_registered_excited_ids,
    register_excited_plugin,
    resolve_excited_plugin_ids,
    run_excited_stages_from_context,
)
from qchem_stack.quantum.excited_plugins.spec import ExcitedRunContext, ExcitedStageOutcome


def _minimal_cfg(**q_kw: object) -> ExperimentConfig:
    return ExperimentConfig(
        schema_version="2",
        experiment_id="t",
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]]),
        scf=SCFSpec(),
        active_space=ActiveSpaceSpec.model_validate(
            {"strategy": "cas", "cas": {"n_orbitals": 2, "n_electrons": 2}}
        ),
        quantum=QuantumSpec.model_validate(dict(q_kw)),  # type: ignore[arg-type]
    )


def _tiny_qh() -> QubitHamiltonian:
    op = QubitOperator(((0, "Z"),), -0.5) + QubitOperator(((1, "Z"),), -0.5)
    return QubitHamiltonian(operator=op, n_qubits=2)


def test_list_registered_excited_ids() -> None:
    assert set(list_registered_excited_ids()) == {"vqd", "qse", "sceom"}


def test_resolve_excited_plugin_ids_from_flags() -> None:
    cfg = _minimal_cfg(
        excited={"vqd": {"after_variational": True}, "qse": {"after_variational": True}}
    )
    assert resolve_excited_plugin_ids(cfg) == ("vqd", "qse")


def test_run_excited_qse_plugin_bundle_schema() -> None:
    cfg = _minimal_cfg(excited={"qse": {"after_variational": True, "subspace_dim": 2}})
    qh = _tiny_qh()
    ctx = ExcitedRunContext(
        cfg=cfg,
        hamiltonian=qh,
        executor=None,
        seed=1,
        ground_angles=np.zeros(4, dtype=float),
        ground_energy=-1.0,
    )
    out: dict[str, object] = {}
    run_excited_stages_from_context(ctx, out=out)
    assert "qse" in out
    bundle = out["qse"]
    assert isinstance(bundle, dict)
    assert bundle["schema"] == EXCITED_QSE_BUNDLE_V1


def test_register_excited_plugin_custom_runner() -> None:
    def _custom(ctx: ExcitedRunContext) -> ExcitedStageOutcome:
        return ExcitedStageOutcome(bundle_key="custom_excited", bundle={"ok": True})

    register_excited_plugin("custom_excited", runner=_custom, overwrite=True)
    cfg = _minimal_cfg()
    ctx = ExcitedRunContext(
        cfg=cfg,
        hamiltonian=_tiny_qh(),
        executor=None,
        seed=0,
        ground_angles=np.zeros(4, dtype=float),
        ground_energy=0.0,
    )
    from qchem_stack.quantum.excited_plugins.registry import run_excited_plugin

    outcome = run_excited_plugin("custom_excited", ctx)
    assert outcome.bundle_key == "custom_excited"
    assert outcome.bundle == {"ok": True}


def test_run_excited_vqd_plugin_bundle_schema() -> None:
    cfg = _minimal_cfg(
        excited={"vqd": {"after_variational": True, "n_states": 2, "cobyla_maxiter": 5}}
    )
    qh = _tiny_qh()
    exe = StatevectorHeaExecutor()
    ctx = ExcitedRunContext(
        cfg=cfg,
        hamiltonian=qh,
        executor=exe,
        seed=1,
        ground_angles=np.zeros(4, dtype=float),
        ground_energy=-1.0,
    )
    out: dict[str, object] = {}
    run_excited_stages_from_context(ctx, out=out)
    assert "vqd" in out
    bundle = out["vqd"]
    assert isinstance(bundle, dict)
    assert bundle["schema"] == EXCITED_VQD_BUNDLE_V1


def test_run_excited_sceom_plugin_bundle_schema() -> None:
    cfg = _minimal_cfg(
        excited={
            "sceom": {"after_variational": True, "subspace_dim": 2, "shots_per_matrix_element": 0}
        }
    )
    qh = _tiny_qh()
    ctx = ExcitedRunContext(
        cfg=cfg,
        hamiltonian=qh,
        executor=None,
        seed=1,
        ground_angles=np.zeros(4, dtype=float),
        ground_energy=-1.0,
    )
    out: dict[str, object] = {}
    run_excited_stages_from_context(ctx, out=out)
    assert "sceom" in out
    bundle = out["sceom"]
    assert isinstance(bundle, dict)
    assert bundle["schema"] == EXCITED_SCEOM_BUNDLE_V1
    assert len(bundle["energies"]) >= 1
