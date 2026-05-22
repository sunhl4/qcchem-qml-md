"""Excited-state plugin registry dispatch."""

from __future__ import annotations

import numpy as np
import pytest
from openfermion.ops import QubitOperator
from pydantic import ValidationError

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.fermion import FermionSpace
from qchem_stack.chem.hamiltonian import QubitHamiltonian
from qchem_stack.chem.pre_quantum_input import PreQuantumInput
from qchem_stack.chem.system import MolecularSystem
from qchem_stack.config import ActiveSpaceSpec, ExperimentConfig, MoleculeSpec, QuantumSpec, SCFSpec
from qchem_stack.contracts.schema_ids import (
    EXCITED_QSE_BUNDLE_V1,
    EXCITED_SCEOM_BUNDLE_V1,
    EXCITED_VQD_BUNDLE_V1,
)
from qchem_stack.exceptions import PipelineError
from qchem_stack.quantum.excited_plugins.registry import (
    excited_registry_export,
    get_excited_plugin_record,
    list_registered_excited_ids,
    register_excited_plugin,
    resolve_excited_plugin_ids,
    run_excited_plugin,
    run_excited_stages_from_context,
    unregister_excited_plugin,
)
from qchem_stack.quantum.excited_plugins.spec import ExcitedRunContext, ExcitedStageOutcome
from qchem_stack.quantum.variational_branch import build_uccsd_variational_model


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


def _tiny_pre_quantum_input(*, n_qubits: int) -> PreQuantumInput:
    op = QubitOperator(tuple((i, "Z") for i in range(max(1, n_qubits))), 1.0)
    qh = QubitHamiltonian(operator=op, n_qubits=n_qubits)
    ref = ClassicalMeanFieldReference(
        mf={"backend": "unit-test"},
        e_tot=0.0,
        mo_energy=np.asarray([0.0], dtype=float),
        molecular_system=MolecularSystem(
            symbols=["H"],
            coordinates_bohr=np.asarray([[0.0, 0.0, 0.0]], dtype=float),
            charge=0,
            multiplicity=1,
            basis="sto-3g",
        ),
        driver_meta={"upstream_classical_software_tag": "unit-test"},
    )
    return PreQuantumInput(
        classical_reference=ref,
        qubit_hamiltonian=qh,
        canonical_active_space_integral_pack=None,
        meta={"source": "unit-test"},
    )


def test_list_registered_excited_ids() -> None:
    assert set(list_registered_excited_ids()) == {"vqd", "qse", "sceom"}


def test_excited_registry_export_builtin_metadata() -> None:
    export = excited_registry_export()
    assert set(export.keys()) >= {"vqd", "qse", "sceom"}
    vqd = export["vqd"]
    assert vqd["bundle_schema"] == EXCITED_VQD_BUNDLE_V1
    assert "builtins.run_vqd_excited" in vqd["implementation"]


def test_get_excited_plugin_record_builtin() -> None:
    rec = get_excited_plugin_record("qse")
    assert rec is not None
    assert rec.bundle_schema == EXCITED_QSE_BUNDLE_V1


def test_excited_context_prefers_pre_quantum_input_hamiltonian() -> None:
    qh_fallback = _tiny_qh()
    pqi = _tiny_pre_quantum_input(n_qubits=3)
    ctx = ExcitedRunContext(
        cfg=_minimal_cfg(),
        hamiltonian=qh_fallback,
        executor=None,
        seed=0,
        ground_angles=np.zeros(4, dtype=float),
        ground_energy=0.0,
        pre_quantum_input=pqi,
    )
    assert ctx.resolved_hamiltonian().n_qubits == 3


def test_run_excited_plugin_unknown_raises_pipeline_error() -> None:
    ctx = ExcitedRunContext(
        cfg=_minimal_cfg(),
        hamiltonian=_tiny_qh(),
        executor=None,
        seed=0,
        ground_angles=np.zeros(4, dtype=float),
        ground_energy=0.0,
    )
    with pytest.raises(PipelineError, match="Unknown excited plugin"):
        run_excited_plugin("not_registered", ctx)


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


def test_unregister_excited_plugin_custom_only() -> None:
    plugin_id = "___test_unregister_custom___"

    def _custom(ctx: ExcitedRunContext) -> ExcitedStageOutcome:
        return ExcitedStageOutcome(bundle_key=plugin_id, bundle={"ok": True})

    register_excited_plugin(plugin_id, runner=_custom, overwrite=True)
    unregister_excited_plugin(plugin_id)
    with pytest.raises(KeyError):
        unregister_excited_plugin(plugin_id)


def test_unregister_excited_plugin_rejects_builtin() -> None:
    with pytest.raises(ValueError, match="cannot unregister built-in"):
        unregister_excited_plugin("vqd")


def test_register_excited_plugin_duplicate_raises_pipeline_error() -> None:
    plugin_id = "___test_dup_once___"

    def _custom(ctx: ExcitedRunContext) -> ExcitedStageOutcome:
        return ExcitedStageOutcome(bundle_key=plugin_id, bundle={"ok": True})

    register_excited_plugin(plugin_id, runner=_custom, overwrite=True)
    with pytest.raises(PipelineError, match="already registered"):
        register_excited_plugin(plugin_id, runner=_custom, overwrite=False)


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


def _h2_like_qh() -> QubitHamiltonian:
    op = QubitOperator(((0, "Z"),), -0.5) + QubitOperator(((1, "Z"),), -0.5)
    return QubitHamiltonian(
        operator=op,
        n_qubits=4,
        fermion_space=FermionSpace(n_spin_orbitals=4, n_electrons=2),
        meta={"fermion_to_qubit_map": "jordan_wigner"},
    )


def _uccsd_excited_cfg(**excited_kw: object) -> ExperimentConfig:
    return ExperimentConfig(
        schema_version="2",
        experiment_id="t",
        molecule=MoleculeSpec(symbols=["H", "H"], coordinates=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.74]]),
        scf=SCFSpec(),
        active_space=ActiveSpaceSpec.model_validate(
            {
                "strategy": "cas",
                "cas": {"n_orbitals": 2, "n_electrons": 2},
                "mapping": {"fermion_qubit": "jordan_wigner"},
            }
        ),
        quantum=QuantumSpec.model_validate(
            {
                "variational": {"ansatz": "uccsd"},
                "pauli": {"use_protocol": False},
                "excited": excited_kw,
            }
        ),
    )


def test_excited_registry_export_uccsd_capabilities() -> None:
    export = excited_registry_export()
    assert export["qse"]["capabilities"].get("supports_uccsd_prepare_state") is True
    assert export["sceom"]["capabilities"].get("supports_uccsd_prepare_state") is True


def test_run_excited_qse_uccsd_plugin_bundle_schema() -> None:
    cfg = _uccsd_excited_cfg(
        qse={"after_variational": True, "subspace_dim": 2, "shot_mode": "exact"}
    )
    qh = _h2_like_qh()
    exe = StatevectorHeaExecutor()
    model = build_uccsd_variational_model(qh, exe, trotter_steps=None)
    ctx = ExcitedRunContext(
        cfg=cfg,
        hamiltonian=qh,
        executor=exe,
        seed=1,
        ground_angles=np.zeros(model.n_params, dtype=float),
        ground_energy=-1.0,
    )
    out: dict[str, object] = {}
    run_excited_stages_from_context(ctx, out=out)
    bundle = out["qse"]
    assert isinstance(bundle, dict)
    assert bundle["schema"] == EXCITED_QSE_BUNDLE_V1
    assert bundle["meta"]["variational_ansatz"] == "uccsd"
    assert bundle["meta"]["basis_reference"] == "uccsd_fermionic_singles"
    assert len(bundle["excitation_energies"]) >= 1


def test_run_excited_sceom_uccsd_plugin_bundle_schema() -> None:
    cfg = _uccsd_excited_cfg(
        sceom={"after_variational": True, "subspace_dim": 2, "shots_per_matrix_element": 0}
    )
    qh = _h2_like_qh()
    exe = StatevectorHeaExecutor()
    model = build_uccsd_variational_model(qh, exe, trotter_steps=None)
    ctx = ExcitedRunContext(
        cfg=cfg,
        hamiltonian=qh,
        executor=exe,
        seed=1,
        ground_angles=np.zeros(model.n_params, dtype=float),
        ground_energy=-1.0,
    )
    out: dict[str, object] = {}
    run_excited_stages_from_context(ctx, out=out)
    bundle = out["sceom"]
    assert isinstance(bundle, dict)
    assert bundle["schema"] == EXCITED_SCEOM_BUNDLE_V1
    assert bundle["meta"]["variational_ansatz"] == "uccsd"
    assert len(bundle["energies"]) >= 1


def test_uccsd_qse_pauli_transitions_rejected_at_config() -> None:
    with pytest.raises(ValidationError, match="pauli_transitions"):
        _uccsd_excited_cfg(
            qse={
                "after_variational": True,
                "subspace_dim": 2,
                "shot_mode": "pauli_transitions",
            }
        )
