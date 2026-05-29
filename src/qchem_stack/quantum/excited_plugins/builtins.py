"""Built-in excited-state plug-ins (VQD / QSE / SCEOM)."""

from __future__ import annotations

import numpy as np

from qchem_stack.config.quantum_helpers import (
    excited_qse_plugin_params,
    excited_sceom_plugin_params,
    excited_vqd_plugin_params,
    resolve_pauli_grouping,
    resolve_uccsd_trotter_steps,
    resolve_variational_ansatz,
    resolve_vqe_depth,
)
from qchem_stack.contracts.schema_ids import (
    EXCITED_QSE_BUNDLE_V1,
    EXCITED_SCEOM_BUNDLE_V1,
    EXCITED_VQD_BUNDLE_V1,
)
from qchem_stack.protocols.product_contract import validate_qse_protocol_for_config
from qchem_stack.quantum.algorithms.excited import QSE, VQD
from qchem_stack.quantum.excited_plugins.spec import ExcitedRunContext, ExcitedStageOutcome
from qchem_stack.quantum.variational_branch import build_uccsd_variational_model


def _uccsd_prepare_state(ctx: ExcitedRunContext):
    if ctx.executor is None:
        raise ValueError("UCCSD excited plugins require HamiltonianExpectationExecutor")
    model = build_uccsd_variational_model(
        ctx.resolved_hamiltonian(),
        ctx.executor,
        trotter_steps=resolve_uccsd_trotter_steps(ctx.cfg),
    )
    return model.prepare_state


def run_vqd_excited(ctx: ExcitedRunContext) -> ExcitedStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    if ctx.executor is None:
        raise ValueError("VQD excited plugin requires HamiltonianExpectationExecutor")
    exe = ctx.executor
    vqd_kw = excited_vqd_plugin_params(cfg)
    prepare_state = None
    n_vp: int | None = None
    param_bounds: list[tuple[float, float]] | None = None
    if resolve_variational_ansatz(cfg) == "uccsd":
        model = build_uccsd_variational_model(
            qh,
            exe,
            trotter_steps=resolve_uccsd_trotter_steps(cfg),
        )
        prepare_state = model.prepare_state
        n_vp = model.n_params
        param_bounds = model.param_bounds
    vqd = VQD(
        qh,
        n_states=int(vqd_kw["n_states"]),
        depth=resolve_vqe_depth(cfg),
        penalty_weight=float(vqd_kw["penalty_weight"]),
        penalty_weights=vqd_kw["penalty_weights"],
        overlap_exponent=float(vqd_kw["overlap_exponent"]),
        cobyla_maxiter=int(vqd_kw["cobyla_maxiter"]),
        optimizer_method=str(vqd_kw["optimizer_method"]),
        prepare_state=prepare_state,
        n_var_parameters=n_vp,
        parameter_bounds=param_bounds,
        init_strategy=str(vqd_kw["init_strategy"]),
        init_noise_scale=float(vqd_kw["init_noise_scale"]),
        max_overlap_warn=vqd_kw["max_overlap_warn"],
        overlap_mode=str(vqd_kw["overlap_mode"]),
        optimizer_mode=str(vqd_kw["optimizer_mode"]),
        executor=exe,
    )
    vqd_res = vqd.run(
        seed=ctx.seed,
        pauli_grouping=resolve_pauli_grouping(cfg),
        ground_angles=np.asarray(ctx.ground_angles, dtype=float),
        ground_energy=float(ctx.ground_energy),
        shots_objective=vqd_kw["shots_objective"],
        shots_overlap=vqd_kw["shots_overlap"],
        shots_weight=vqd_kw["shots_weight"],
    )
    return ExcitedStageOutcome(
        bundle_key="vqd",
        bundle={
            "schema": EXCITED_VQD_BUNDLE_V1,
            "energies": vqd_res.energies,
            "meta": vqd_res.meta,
        },
    )


def run_qse_excited(ctx: ExcitedRunContext) -> ExcitedStageOutcome:
    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    qse_kw = excited_qse_plugin_params(cfg)
    angles = np.asarray(ctx.ground_angles, dtype=float)
    depth = resolve_vqe_depth(cfg)
    qse = QSE(qh, subspace_dim=int(qse_kw["subspace_dim"]))
    kb = qse_kw["max_basis"]
    shot_mode = str(qse_kw["shot_mode"])
    use_uccsd = resolve_variational_ansatz(cfg) == "uccsd"
    validate_qse_protocol_for_config(
        cfg, ansatz="uccsd" if use_uccsd else "hea", shot_mode=shot_mode
    )
    expansion_pool = str(qse_kw["expansion_pool"])
    if use_uccsd:
        prepare_state = _uccsd_prepare_state(ctx)
        if shot_mode == "exact":
            qse_res = qse.run_from_uccsd_basis(
                angles, prepare_state, max_basis=kb, expansion_pool=expansion_pool
            )
        elif shot_mode == "gaussian_h":
            qse_res = qse.run_from_uccsd_basis_shot_noise(
                angles,
                prepare_state,
                max_basis=kb,
                shots_per_matrix_element=int(qse_kw["shots_per_matrix_element"]),
                seed=ctx.seed,
                expansion_pool=expansion_pool,
            )
        elif shot_mode == "pauli_transitions_qiskit":
            qse_res = qse.run_from_uccsd_basis_pauli_transitions_qiskit(
                angles,
                prepare_state,
                max_basis=kb,
                shots_per_ij_term=int(qse_kw["shots_per_ij_term"]),
                expansion_pool=expansion_pool,
            )
        else:
            qse_res = qse.run_from_uccsd_basis_pauli_transitions(
                angles,
                prepare_state,
                max_basis=kb,
                shots_per_ij_term=int(qse_kw["shots_per_ij_term"]),
                seed=ctx.seed,
                expansion_pool=expansion_pool,
            )
    elif shot_mode == "exact":
        qse_res = qse.run_from_vqe_hea_basis(angles, depth, max_basis=kb)
    elif shot_mode == "gaussian_h":
        qse_res = qse.run_from_vqe_hea_basis_shot_noise(
            angles,
            depth,
            max_basis=kb,
            shots_per_matrix_element=int(qse_kw["shots_per_matrix_element"]),
            seed=ctx.seed,
        )
    else:
        qse_res = qse.run_from_vqe_hea_basis_pauli_transitions(
            angles,
            depth,
            max_basis=kb,
            shots_per_ij_term=int(qse_kw["shots_per_ij_term"]),
            seed=ctx.seed,
        )
    qse_meta = dict(qse_res.meta)
    qse_meta["qse_shot_mode"] = shot_mode
    if use_uccsd:
        qse_meta["variational_ansatz"] = "uccsd"
    return ExcitedStageOutcome(
        bundle_key="qse",
        bundle={
            "schema": EXCITED_QSE_BUNDLE_V1,
            "excitation_energies": qse_res.excitation_energies,
            "meta": qse_meta,
        },
    )


def run_sceom_excited(ctx: ExcitedRunContext) -> ExcitedStageOutcome:
    from qchem_stack.protocols.computables.base import EvaluationContext
    from qchem_stack.protocols.computables.sceom_matrix import SCEOMMatrixComputable
    from qchem_stack.quantum.algorithms.sceom import resolve_sceom_s_generators

    cfg = ctx.cfg
    qh = ctx.resolved_hamiltonian()
    sceom_kw = excited_sceom_plugin_params(cfg)
    gens, _ = resolve_sceom_s_generators(
        strategy=str(sceom_kw["generator_strategy"]),
        hamiltonian=qh,
        subspace_dim=int(sceom_kw["subspace_dim"]),
    )
    angles = np.asarray(ctx.ground_angles, dtype=float)
    prepare_state = None
    if resolve_variational_ansatz(cfg) == "uccsd":
        prepare_state = _uccsd_prepare_state(ctx)
    comp = SCEOMMatrixComputable(
        name="sceom",
        hamiltonian=qh,
        subspace_dim=int(sceom_kw["subspace_dim"]),
        generator_strategy=str(sceom_kw["generator_strategy"]),
        shots_per_matrix_element=int(sceom_kw["shots_per_matrix_element"]),
        self_consistent_rounds=int(sceom_kw["self_consistent_rounds"]),
        shots_backend=str(sceom_kw["shots_backend"]),
        s_generators=gens,
        prepare_state=prepare_state,
        hea_depth=resolve_vqe_depth(cfg),
    )
    comp_out = comp.evaluate(
        EvaluationContext(
            angles=angles,
            rng=np.random.default_rng(ctx.seed),
            extra={"hea_depth": resolve_vqe_depth(cfg), "s_generators": gens},
        )
    )
    sceom_meta = dict(comp_out.meta)
    sceom_meta["generator_strategy_yaml"] = sceom_kw["generator_strategy"]
    if prepare_state is not None:
        sceom_meta["variational_ansatz"] = "uccsd"
    comp_value = comp_out.value
    excitation_energies = (
        list(comp_value.get("excitation_energies") or []) if isinstance(comp_value, dict) else []
    )
    sceom_res = type("_SceomOut", (), {})()
    sceom_res.energies = excitation_energies
    sceom_res.meta = sceom_meta
    return ExcitedStageOutcome(
        bundle_key="sceom",
        bundle={
            "schema": EXCITED_SCEOM_BUNDLE_V1,
            "energies": sceom_res.energies,
            "meta": sceom_meta,
        },
    )


BUILTIN_EXCITED_RUNNERS: dict[str, object] = {
    "vqd": run_vqd_excited,
    "qse": run_qse_excited,
    "sceom": run_sceom_excited,
}
