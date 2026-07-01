# Pipeline stage ownership

Maps each `run_pipeline_sync` stage to output keys and owning modules. Use this when adding fields to avoid duplicate writers.

## Stage → top-level `out` keys

| Stage | Primary module | Writes to `out` (top-level) |
|-------|----------------|------------------------------|
| scf | `orchestration/stage_execution.py` (`run_scf_stage`) | (via scf_stage fields merged in runner) `energy_components`, `classical_benchmarks`, `embedding_input_system`, RDM sidecars |
| pre_quantum | `orchestration/stage_execution.py` (`build_pre_quantum_stage`) | `pre_quantum_input`, `hamiltonian_meta`, `pre_quantum_build_cache` |
| repro (inline) | `orchestration/repro_metadata.py` | `repro` (initial parity snapshot, config hash) |
| variational | `quantum/variational_plugins/registry.py` | `energy_after_variational`, `angles`, algorithm meta, `algorithm_report` |
| embedding_workflow | `orchestration/embedding_workflow_stage.py` | `embedding_workflow`, optional Schmidt/DMET payloads |
| excited | `orchestration/excited_stages.py` | `vqd`, `qse`, `sceom`, `excited_resource_summary` |
| protocol_finalize | `orchestration/protocol_finalize_stage.py` | `energy_pauli_protocol`, `protocol_counts`, `resource_summary`, job fields |

Assembly after variational: `orchestration/pipeline_assembly.py` (`assemble_pipeline_result_dict`, `patch_repro_parity_snapshot`).

## `repro` sub-blocks

| Sub-block | Canonical writer | Notes |
|-----------|------------------|-------|
| `repro.run_summary` | `orchestration/repro_summary.py` (`attach_run_summary`) | **Only** canonical writer. Called from `protocol_finalize_run.py` and `pipeline.run_pipeline_from_config` (job path). |
| `repro.parity_snapshot` (initial) | `orchestration/repro_metadata.py` + `repro_snapshot.py` | At run start / after pre-quantum |
| `repro.parity_snapshot` (finalize) | `orchestration/parity_finalize.py` (`finalize_open_stack_parity_snapshot`) | Open-stack integration keys only; does **not** replace `run_summary` |
| `repro.pipeline_profile` | `orchestration/run_context.py` (`PipelineStageTimer`) | Via protocol finalize |
| `repro.run_context` | `orchestration/pipeline_sync_runner.py` | When `run_context` passed |

## Event emission

| Concern | Module |
|---------|--------|
| Stage lifecycle (`started` / `completed` / `failed`) | `orchestration/stage_registry.py` (`StageLifecycle`) |
| `emit_stage_event` hooks | `orchestration/pipeline_event_hooks.py` |
| Global bus + default log subscriber | `orchestration/pipeline_events.py` (`get_event_bus`) |
| JSON log lines | `orchestration/run_context.py` |

On stage failure, `pipeline_sync_runner._run_pipeline_stages` emits `stage.<name>.failed` and
`pipeline.failed`, records `repro.run_summary.stage_failed` / `error_type` / `error_message`
when `ctx.repro` exists, then raises `PipelineError`.

## Registry-driven execution

Stage order and runners: `qchem_stack.orchestration.stage_registry.PIPELINE_STAGE_SPECS` (`StageSpec.run` + optional `post_run`). Loop: `pipeline_sync_runner._run_pipeline_stages`. Context: `pipeline_sync_context.PipelineSyncContext`. Stage bodies: `pipeline_stage_runners.py`.

`pre_quantum` uses `post_run=bind_post_pre_quantum_ctx` to attach repro metadata and backend handles before variational.

## Orchestration entrypoints

| Function | File |
|----------|------|
| `run_pipeline_sync` | `pipeline.py` → `pipeline_sync_runner.py` |
| `run_pipeline_from_config` | `pipeline.py` |
| `run_protocol_and_finalize_stage` | `protocol_finalize_stage.py` → `protocol_finalize_run.py` |
