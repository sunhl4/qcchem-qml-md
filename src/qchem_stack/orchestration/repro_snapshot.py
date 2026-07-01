from __future__ import annotations

from typing import TYPE_CHECKING

from qchem_stack.config import ExperimentConfig, compiler_bundle_signature_from_config
from qchem_stack.config.active_space_helpers import (
    resolve_fermion_qubit_mapping,
    resolve_n_electrons,
    resolve_n_orbitals,
)
from qchem_stack.config.embedding_enums import (
    DmetHamiltonianSource,
    EmbeddingMode,
    ProjectionQuantumHamiltonian,
)
from qchem_stack.config.embedding_helpers import nonempty_fragment_labels
from qchem_stack.config.embedding_specs import EmbeddingDmet, EmbeddingProjection
from qchem_stack.config.mitigation_helpers import mitigation_repro_core_fields
from qchem_stack.config.quantum_helpers import (
    classify_pauli_expectation_path_for_config,
    quantum_repro_core_fields,
    quantum_repro_sidecar_fields,
)
from qchem_stack.contracts.schema_ids import (
    DMET_OPEN_ARCHITECTURE_V1,
    PROJECTION_EMBEDDING_OPEN_TRACE_V1,
)

if TYPE_CHECKING:
    from qchem_stack.chem.hamiltonian import QubitHamiltonian


def append_open_stack_parity_fields(snap: dict[str, object], cfg: ExperimentConfig) -> None:
    """Designed open-stack parity block (public-contract L1)."""
    pis = cfg.parity_integrations
    snap["parity_integrations"] = pis.model_dump(mode="json")
    if not pis.enabled:
        return

    from qchem_stack.integrations.tket_fullchain import describe_tket_closure_layer

    snap["open_stack_contract_schema"] = "parity_open_stack_contract_v1"
    snap["open_stack_design_intent"] = (
        "Engineered open paths where vendor code is closed: keep the same workflow *stages* and "
        "auditable artifacts described in public vendor documentation. Implementations use peer-reviewed "
        "building blocks or explicit user hooks (DMET bath updates, UCC regrouping, TN topology)."
    )
    snap["tket_closure_layer_descriptor"] = describe_tket_closure_layer()

    if pis.qnexus_probe:
        from qchem_stack.integrations.nexus_optional import probe_qnexus_installation

        snap["qnexus_probe"] = probe_qnexus_installation()
    if pis.open_qermit_reference:
        from qchem_stack.integrations.qermit_reference import qermit_capability_matrix

        snap["open_qermit_capability_matrix"] = qermit_capability_matrix()
    if pis.tensornet_closure_reference:
        from qchem_stack.integrations.tensornet_closure import tensornet_closure_strategy

        snap["tensornet_closure_reference"] = tensornet_closure_strategy()
    if pis.uccsd_excitation_reference:
        from qchem_stack.chem.kernels.spin_ucc import count_uccsd_excitations

        n_so = 2 * resolve_n_orbitals(cfg.active_space)
        ne = resolve_n_electrons(cfg.active_space)
        snap["uccsd_reference_closed_shell"] = {
            "n_spin_orbitals": n_so,
            "n_electrons_spin": ne,
            "excitation_counts": count_uccsd_excitations(n_so, ne),
            "module": "qchem_stack.chem.kernels.spin_ucc",
            "caveat": "Spatial active space → spin orbitals assumes closed-shell counting; "
            "open-shell or symmetry blocking needs an explicit user mapping.",
        }

    if cfg.embedding.mode == EmbeddingMode.DMET and isinstance(cfg.embedding, EmbeddingDmet):
        dmet = cfg.embedding.dmet
        snap["dmet_open_loop_architecture"] = {
            "schema": DMET_OPEN_ARCHITECTURE_V1,
            "self_consistency_loop_class": (
                "qchem_stack.chem.embedding.dmet_self_consistent.DMETSelfConsistencyLoop"
            ),
            "one_shot_driver_class": (
                "qchem_stack.chem.embedding.dmet_self_consistent.OneShotEmbeddingDriver"
            ),
            "fragment_solver_hook": "qchem_stack.chem.embedding.dmet.FragmentSolverProtocol",
            "scf_cycles_yaml": cfg.embedding.n_scf_cycles_embedding,
            "fragment_labels": list(dmet.fragment_labels),
            "dmet_hamiltonian_source": dmet.hamiltonian_source,
            "classical_reference_method": cfg.embedding.classical_reference_method,
            "workflow_note": (
                "Commercial stacks embed bath construction + global correlation updates; "
                "this repository implements the orchestration contract and records stub or "
                "whole_active_system impurity VQE (see embedding.dmet.hamiltonian_source). "
                "Plug bath-aware build_fragment_hamiltonian + DMETSelfConsistencyLoop for full DMET."
            ),
        }

    if cfg.embedding.mode == EmbeddingMode.PROJECTION and isinstance(
        cfg.embedding, EmbeddingProjection
    ):
        proj = cfg.embedding.projection
        trace: dict[str, object] = {
            "schema": PROJECTION_EMBEDDING_OPEN_TRACE_V1,
            "low_level": proj.low_level,
            "high_level": proj.high_level,
            "threshold": float(proj.threshold),
            "projection_quantum_hamiltonian": proj.quantum_hamiltonian,
            "module": "qchem_stack.chem.embedding.projection",
        }
        if proj.quantum_hamiltonian == ProjectionQuantumHamiltonian.FRAGMENT_MULLIKEN_MO:
            trace["projection_hamiltonian_source"] = "fragment_mulliken_mo_v1"
            trace["projection_module"] = "qchem_stack.chem.embedding.projection_hamiltonian"
            fq = resolve_fermion_qubit_mapping(cfg.active_space)
            trace["fermion_qubit_mapping"] = fq
            trace["caveat"] = (
                "Variational Hamiltonian is built from RHF MOs, Mulliken-ranked fragment orbitals, "
                f"PySCF CASCI active integrals, and fermion→qubit mapping "
                f"{fq!r} (see projection_hamiltonian)."
            )
            trace["epistemic_bound"] = (
                "Not full many-body projection embedding of the environment; not bit-wise parity "
                "with closed vendor PySCF projection drivers."
            )
        else:
            trace["projection_hamiltonian_source"] = "global_active_space"
            fq = resolve_fermion_qubit_mapping(cfg.active_space)
            trace["fermion_qubit_mapping"] = fq
            trace["caveat"] = (
                "Variational stage uses the global ActiveSpaceSpec qubit Hamiltonian "
                f"(mapping {fq!r}; same as embedding.mode:none "
                "for the qubit operator). This block records projection workflow metadata only."
            )
            trace["epistemic_bound"] = (
                "Open-stack L1 trace - not numerical parity with proprietary projection stacks."
            )
        snap["projection_embedding_open_trace"] = trace

    if pis.gap_closure_reference_bundle:
        from qchem_stack.integrations.gap_closure_bundle import build_open_gap_closure_reference

        snap["open_gap_closure_reference"] = build_open_gap_closure_reference(cfg)


def repro_quantum_snapshot(cfg: ExperimentConfig, qh: QubitHamiltonian | None) -> dict[str, object]:
    """Falsifiability/parity fields aligned with Methods tables."""
    snap: dict[str, object] = {
        **quantum_repro_core_fields(cfg),
        **quantum_repro_sidecar_fields(cfg),
        **mitigation_repro_core_fields(cfg),
        "fermion_qubit_mapping": resolve_fermion_qubit_mapping(cfg.active_space),
        "pauli_protocol_expectation_path": classify_pauli_expectation_path_for_config(cfg),
        "shots_per_circuit": cfg.backend.shots_per_circuit,
        "target_energy_stderr": cfg.backend.target_energy_stderr,
        "backend_provider": cfg.backend.provider,
        "compiler_native_twoq": cfg.compiler.native_twoq,
        "compiler_optimization_level": cfg.compiler.optimization_level,
        "compiler_preoptimize_passes": list(cfg.compiler.preoptimize_passes),
        "compiler_passes_yaml": list(cfg.compiler.compiler_passes),
        "compiler_bundle_signature": compiler_bundle_signature_from_config(cfg),
    }
    if qh is not None and qh.meta:
        snap["hamiltonian_meta"] = dict(qh.meta)
    emb = cfg.embedding
    snap["embedding_mode"] = emb.mode
    if emb.n_scf_cycles_embedding is not None:
        snap["n_scf_cycles_embedding"] = emb.n_scf_cycles_embedding
    if emb.classical_reference_method:
        snap["classical_reference_method"] = emb.classical_reference_method
    if isinstance(emb, EmbeddingDmet):
        dmet = emb.dmet
        schmidt = dmet.schmidt
        frag_labels = nonempty_fragment_labels(emb)
        if frag_labels:
            snap["embedding_fragment_labels"] = frag_labels
        if dmet.hamiltonian_source == DmetHamiltonianSource.SCHMIDT_ATOMIC_PRODUCTION:
            snap["schmidt_dmet_max_cycles"] = int(schmidt.dmet_max_cycles)
            snap["schmidt_dmet_mixing_alpha"] = float(schmidt.dmet_mixing_alpha)
            if schmidt.multi_fragment_atom_groups:
                snap["schmidt_multifragment"] = True
                snap["schmidt_multifragment_n"] = len(schmidt.multi_fragment_atom_groups)
    snap["chemistry_extended"] = cfg.chemistry_extended.model_dump(mode="json")
    snap["nexus_analog"] = cfg.nexus_analog.model_dump(mode="json")
    snap["nexus_cloud"] = cfg.nexus_cloud.model_dump(mode="json")
    from qchem_stack.chem.embedding.hamiltonian_semantics import pre_quantum_hamiltonian_semantics

    snap.update(pre_quantum_hamiltonian_semantics(cfg))
    append_open_stack_parity_fields(snap, cfg)
    return snap
