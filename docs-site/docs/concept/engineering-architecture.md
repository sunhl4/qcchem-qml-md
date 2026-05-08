# qchem-stack — software engineering architecture

This document complements the InQuanto **parity** and chemistry narrative docs. It fixes the **internal layering** and **integration contracts** you need for a maintainable product (not a one-off benchmark script).

## 1. Layer model

| Layer | Packages / modules | Responsibility |
|--------|-------------------|----------------|
| **Domain config** | `qchem_stack.config` | Pydantic `ExperimentConfig` — single source of truth for YAML, validation, cost guards. |
| **Chemistry drivers / adapters** | `qchem_stack.chem.*` (`chem.solvers`, **`chem.bridges`**) | `ChemIntegralSolver` registry + **interchange façade** (`classical_mean_field_via_solver_bridge` → `MolecularMeanFieldResult`); Hamiltonian builders, Schmidt / DMET *shapes*. |
| **Quantum algorithms** | `qchem_stack.quantum.*` | VQE, ADAPT, excited-state drivers — no YAML parsing. |
| **Backends & protocol** | `qchem_stack.backends.*`, `qchem_stack.protocols.*` | Executor abstraction, Pauli averaging, resource rows. |
| **Orchestration** | `qchem_stack.orchestration` | `run_pipeline_sync` / `run_pipeline_from_config` — **wires** layers; logging at INFO. |
| **Integrations** | `qchem_stack.integrations` | TKET/qnexus/Qermit *analogs*, gap-closure reference bundles, Schmidt↔DMET loop glue. |
| **Jobs / cloud analogs** | `qchem_stack.jobs` | SQLite worker, Nexus-shaped ledgers — async boundary. |
| **Repro export** | `qchem_stack.repro` | Strict JSON for `repro` blobs (no silent `default=str`). |
| **Errors** | `qchem_stack.exceptions` | Typed base errors for ops and API gateways. |

**Rule of thumb:** algorithms and drivers never import orchestration. Orchestration imports everything below.

## 1.1 Pinned architecture invariant

This repository is pinned to the following invariant:

- Unified classical interface first: every classical chemistry backend enters via `ChemIntegralSolver` and bridge interchanges.
- Backend-agnostic downstream: once `MolecularMeanFieldResult` / `ClassicalMeanFieldReference` / `CanonicalActiveSpaceIntegralPack` are formed, orchestration and quantum layers must not care which classical software produced them.
- PySCF is one backend implementation example, not a privileged architectural dependency.
- Backend-specific behavior must remain explicit at adapter/interchange boundaries behind `SolverCapabilities` gates.
- Compatibility fields are transitional only: temporary PySCF-typed compatibility slots can exist during migration, but new public APIs must expose backend-agnostic interchange types first and mark legacy slots for removal.

## 2. Public surfaces (stability intent)

- **Stable for integrators:** `run_pipeline_sync`, `run_pipeline_from_config`, `ExperimentConfig`, `load_experiment_config`, `repro_json_dumps` / `repro_dict_for_strict_json`, exception types under `qchem_stack.exceptions`.
- **Stable for parity / Methods:** keys under `out["repro"]`, especially `parity_snapshot` and `run_summary` (see existing Chinese technical docs in `docs/`). The authoritative **whitelist** of `parity_snapshot` top-level keys is `qchem_stack.protocols.inquanto_contract.PARITY_SNAPSHOT_DOCUMENTED_KEYS` (see `技术文档_DMET与parity_snapshot开放契约.md` §3b).
- **Intentionally experimental:** specific keys inside `protocol_counts`, optional integrator stubs — version in export schema where applicable.

## 3. Error taxonomy

| Type | When |
|------|------|
| `ConfigurationError` | Invalid YAML file or top-level mapping (from `load_experiment_config`). Pydantic `ValidationError` still used for schema validation when building models directly. |
| `EmbeddingError` / `SchmidtProductionError` | Fragment / bath / cap violations in Schmidt production. |
| `PipelineError` | Orchestration preconditions (e.g. Schmidt path requires RHF in current implementation). |
| `ReproExportError` | Strict JSON export: non-finite floats, cycles, unsupported types. |

Gateway services should map these to HTTP/status codes and structured logs without string-matching tracebacks.

## 4. Reproducibility & enterprise export

- Do **not** persist `json.dumps(repro, default=str)` in production: it masks bugs.
- Use `qchem_stack.repro.export.repro_json_dumps(out["repro"])` before writing to object storage or Kafka.
- Hamiltonian / job payloads may include numpy internally; the **repro** block is designed to be JSON-native after pipeline completion.

## 5. CI & quality gates

- `ruff check src tests`
- `pytest`
- Optional extras (PySCF, Qiskit, pytket) exercised in CI matrix and smoke scripts.

## 6. Versioning

- Package version: `pyproject.toml` `[project].version` and runtime `qchem_stack.__version__` (from `importlib.metadata`, fallback `0.1.0` if not installed as a wheel).
- Config field `ExperimentConfig.schema_version` is the experiment **contract** version, independent of the library semver.

## 7. Extension points (competitor-shaped, vendor-neutral)

1. **Fragment solver** — `FragmentSolverProtocol` + `DMETContext` (replace stub with CCSD / VQE impurity).
2. **Bath update** — `DMETSelfConsistencyLoop.run_with_hooks` / `run_with_sequential_bath_updates`.
3. **Backend** — `BackendSpec` + `executor_from_spec` (swap statevector / Aer / hardware).
4. **Compiler bundle** — `CompilerPassBundle` + TKET bridge for compile metrics.
5. **Strict repro** — extend `repro/export.py` if you add non-JSON types into `repro` deliberately.

## 8. Observability (`run_context`, `pipeline_profile`)

- **`repro["run_context"]`** — `schema: run_context_v1`, `trace_id` (UUID or propagated), optional `client_request_id`. Pass `run_context=` into `run_pipeline_sync` / `run_pipeline_from_config`, or build via `RunContext.from_headers(...)` (`traceparent` → trace id, then `X-Trace-ID`, then new UUID; `X-Request-ID` → `client_request_id`).
- **`repro["pipeline_profile"]`** — `schema: pipeline_profile_v1`, `stages` (per-segment `duration_ms` between successive `mark` calls), `total_wall_ms`. Final segment **`finalize_repro`** covers parity snapshot / run-summary attachment overhead before the profile dict is written. Summaries also appear in `run_summary` (`pipeline_total_wall_ms`, `pipeline_slowest_stage`, etc.).

## 9. HTTP API (optional extra)

Chinese contract tables (endpoints, `schema`, `meta`, observability): [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](/reference/http-api-sqlite-jobs). Maintainer decisions + checklist: **§9** in the same page (legacy HTTP memory doc merged).

- Install: `pip install "qchem-stack[api]"`.
- App: `qchem_stack.api.app:app` (FastAPI). Run: `uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000`.
- **`GET /health`** — liveness JSON `{"status":"ok"}` (no SQLite access).
- **`GET /health/ready`** — tries default job DB parent mkdir + `SELECT 1` on SQLite; **503** if path unusable.
- **`GET /v1/meta/parity-gaps`** — `schema: inquanto_gap_export_v1`: package version + `gaps` from `inquanto_gap_categories()` (dashboard / CI against [inquanto_public_parity_matrix.md](/parity/public-matrix)).
- **`GET /v1/meta/product-analog`** — `schema: product_analog_v1`: one-shot “what we emulate” vs InQuanto/Nexus *public* narratives (routes pointer list; no closed-source claims).
- **`POST /v1/meta/workflow-preview`** — `schema: workflow_preview_v1`: five **protocol stages** (`instantiate`→`evaluate`) with config hints + **`computable_graph_v2`** (`semantic_dataflow_v1`; optional YAML **`quantum.computable_extra_edges`** / **`quantum.computable_remove_edges`**) + `roots` + `computable_abstract` — YAML only; core logic in `integrations/inquanto_workflow_preview.py`.
- **`GET /v1/meta/capability-surface`** — `schema: capability_surface_v1`: version + full **`inquanto_object_map`** + **`inquanto_gap_categories`** + **`mitigation_execution_model`** + **`open_stack_differentiators`** (`open_stack_differentiators_v1`) + **`operator_pool_registry_export_v1`** (same schema as parity export; ADAPT/IQEB pool ids and aliases); regression: `tests/test_api_runs.py::test_capability_surface_matches_inquanto_contract`.
- **`POST /v1/meta/computables-preview`** — `schema: computables_preview_v1`: InQuanto-**Computable**-style list + **`computable_abstract` v2** from YAML only (no chemistry run); mirrors `scripts/export_parity_criteria_table` abstract block.
- **`GET /v1/meta/ml-md-bridge`** — `schema: ml_md_bridge_surface_v1`: QMEF schema hints + exporter / stub-trainer pointers (`tests/test_api_ml_md_bridge.py`).
- **`POST /v1/meta/qmef-validate`** — `schema: qmef_validate_v1`: `{ "qmef": … }` as **`QMEFDataset`** JSON (no QC).
- **`POST /v1/meta/ml-md-trainer-stub-fit`** — `schema: ml_md_trainer_stub_fit_v1`: in-memory **`StubTorchMLIPTrainer.fit`** only (no server-side checkpoints).
- **`GET /v1/meta/queue-stats`** — `schema: queue_stats_v1`: `counts` per `JobStatus` for the chosen DB (Nexus workspace ops analog).
- **`GET /v1/runs`** — `schema: job_list_v1`, includes echo **`limit`** / **`offset`**. Filters: **`experiment_id`**, **`api_workspace_label`** (POST `workspace_label`), **`api_project_slug`** (POST `project_slug`). Meta filters use `json_extract` when available; on older SQLite without JSON1, falls back to scanning up to 5000 newest rows (then filter + slice — document for large queues).
- **`POST /v1/runs`** — JSON body: `experiment_yaml` (string), `sync` (bool), optional `job_db_path`, optional **`workspace_label`** → **`meta.api_workspace_label`**, optional **`project_slug`** → **`meta.api_project_slug`**. Headers: `traceparent` / `X-Trace-ID` / `X-Request-ID` populate `run_context`. Invalid YAML → **400**; invalid config → **422** (Pydantic error list), including for async enqueue (fail-fast before `QUEUED`). Sync mode returns **`full_pipeline_job_result_v1`**; **`QChemStackError`** inside the sync pipeline → **422** with string `detail`. Async returns **202** with **`schema: run_enqueue_response_v1`**, `job_id`, **`experiment_id`** (echo), `trace_id`, `job_db`. Store **`meta`** includes `trace_id`, **`experiment_id`**, optional **`nexus_analog_project_label`** when YAML enables `nexus_analog` with a label, and optional **`api_workspace_label`** / **`api_project_slug`**.
- **`GET /v1/runs/{job_id}/status`** — `schema: job_status_v1`: light poll payload (`created` / `updated` / `status` / `meta` / `retry_count` / truncated `error`); no full `result` blob.
- **`GET /v1/runs/{job_id}/summary`** — `schema: run_product_summary_v1`: **console slim** view — key energies, `run_summary` excerpt (≤40 fields), `api_labels` (`api_workspace_label`, `api_project_slug`, `nexus_analog_project_label` from `meta`), `sidecars_present`, `parity_snapshot_keys` when `DONE`; **`partial: true`** while queued/running/failed (InQuanto-style result panel without pulling full `repro`).
- **`GET /v1/runs/{job_id}/events`** — `schema: job_events_v1`; **`note`** is `sqlite_timeline_json_v1` when the job row stores **`timeline_json`** (milestones: `submitted`, `running`, **`pipeline_stage`** + `stage` key during async **`run_full_pipeline_job`**, `completed`, `failed`, `retry_scheduled`), else coarse **`sqlite_coarse_timeline_v1`** fallback for legacy rows. Response **events** mirror stored JSON keys (incl. `stage` for pipeline).
- **`GET /v1/runs/{job_id}/repro`** — `schema: run_repro_only_v1`: **`repro`** blob only when **`status=DONE`**; **409** while `QUEUED` / `RUNNING` / `FAILED` (Methods-oriented download).
- **`GET /v1/runs/{job_id}`** — query `job_db_path` must match enqueue. Returns `SqliteJobStore.result`: always includes **`job_kind`** and optional **`meta`**; `DONE` merges the stored result payload as before. Full-pipeline **DONE** payloads include parity sidecars when present: **`nexus_analog_ledger`**, **`mitigation_graph_report`**, **`mitigation_dag_execution`**, **`nexus_cloud_repro`**, **`tensornet_protocol_stub`**, **`qpe_demo_track`** (same as sync pipeline).
- **Security:** bind to localhost; add auth at the edge for production. Successful **POST `/v1/runs`** (sync **200** or async **202**) echoes **`X-Trace-ID`** and, when provided, **`X-Request-ID`** on the HTTP response for gateway correlation.

## 10. SQLite job kinds (`jobs` store)

- **`job_kind`** column: `pauli_protocol` (pickled `PauliAveragingProtocol`, default) or **`full_pipeline`** (UTF-8 JSON payload: `config_yaml`, optional `run_context`).
- **Enqueue:** `qchem_stack.jobs.pipeline_jobs.enqueue_full_pipeline_run` (optional ``meta_extra`` merged into JSON ``meta``, e.g. ``experiment_id``).
- **Worker:** `qchem-jobs-worker --db …` dispatches via `jobs/worker_dispatch.dispatch_job` (Pauli vs full pipeline).
- **Listing / metrics:** `SqliteJobStore.list_jobs(..., offset=..., experiment_id=..., api_workspace_label=..., api_project_slug=...)` — meta filters share SQL + fallback in §9. Persisted **`timeline_json`** (enqueue seed + `append_timeline` on run/complete/fail/retry). **`count_by_status()`** for queue depth. **`get_job_public_summary`** for lightweight polling without loading the `result` BLOB.

---

*Epistemic boundary:* numerical DMET with fitted correlation potentials and closed commercial optimizers is **not** claimed here; this stack targets **auditable workflow parity** (L1) and clean software boundaries.
