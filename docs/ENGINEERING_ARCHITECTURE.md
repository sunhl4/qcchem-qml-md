# qchem-stack — software engineering architecture

This document anchors **qchem‑stack internals**: layering, HTTP contracts where they touch shipped code, and strict `repro` export posture. Competitive literature and backlog narratives live separately under **`docs/`** (optional reading). Related Chinese taxonomy: [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md)、[工程记忆_Quantinuum对标与数据流技术文档.md](工程记忆_Quantinuum对标与数据流技术文档.md)、[public_parity_matrix.md](public_parity_matrix.md); see also **§14** in [工程记忆_Quantinuum对标与数据流技术文档.md](工程记忆_Quantinuum对标与数据流技术文档.md) ([Quantinuum public howto](https://www.quantinuum.com/)).

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

**Pre-quantum topology (pinned):** YAML validators and `resolve_pre_quantum_path` select the branch; **`chem.pre_quantum_build`** assembles `PreQuantumInput` (canonical pack, Schmidt, projection, plugin); **`chem.bridges.run_build_cache`** memoizes packs per run; **`orchestration.stage_execution.build_pre_quantum_stage`** only wires SCF output, precomputed ingress, profiling, and stage artifacts. Quantum stages consume `PreQuantumInput` only.

Config schema, nested YAML layout, and code/architecture style for maintainers: [`config_校验分层约定.md`](config_校验分层约定.md) (**authoritative**; `embedding` + `quantum` are nested v2 reference sections). Dual-ingress offline bundle contract: [`技术文档_双线路经典输入与统一PreQuantumInput契约.md`](技术文档_双线路经典输入与统一PreQuantumInput契约.md).

## 1.1 Architecture invariant (pinned)

The project is pinned to this invariant:

- **Unified classical interface first**: all classical chemistry software enters through `ChemIntegralSolver` + bridge interchange.
- **Backend-agnostic downstream**: after bridge/interchange objects are formed (`MolecularMeanFieldResult`, `ClassicalMeanFieldReference`, `CanonicalActiveSpaceIntegralPack`), orchestration/quantum/reporting logic must not depend on vendor-native class names.
- **PySCF is an example backend, not a privileged architecture dependency**.
- **Any backend-specific branch must be isolated at adapter/interchange boundaries with explicit capability gates** (`SolverCapabilities`), never by hidden assumptions in algorithm code.
- **Compatibility fields are transitional only**: legacy PySCF-typed convenience slots may remain temporarily for migration, but all new public APIs must use backend-agnostic interchange types first and document deprecation windows.
- **Dual classical ingress is supported**: live solver execution and offline precomputed bundles must converge to the same `PreQuantumInput` handoff before quantum stages.
- **Pre-quantum handoff metadata is provenance-driven**: `PreQuantumInput.as_summary_dict()` exposes stable top-level fields (`source`, `backend_tag`, `integral_source`, `fermion_to_qubit_map`, `hamiltonian_fingerprint`) while preserving full `hamiltonian_meta` for debug. `integral_source` / `integral_openfermion_bridge` must come from explicit inputs or `CanonicalActiveSpaceIntegralPack.provenance` before falling back to backend labels.

**Production milestone (pinned):** end-to-end **numerical** classical chemistry in CI and representative YAMLs targets **`scf.driver=pyscf`** until another backend implements `compute_mean_field` and (when building restricted active-space qubit Hamiltonians) satisfies `SolverCapabilities.supports_restricted_active_space_qubit_hamiltonian` plus interchange tests for `CanonicalActiveSpaceIntegralPack.from_classical_reference`. Additional codes register via `qchem_stack.chem.solvers.registry`. Product narrative and extension checklist (Chinese): [竞争定位与路线图 — §5.1](竞争定位与路线图_对标Quantinuum产品与技术路线.md).

## 1.2 PySCF boundary refactor (maintainer note)

To keep `PySCFDriver` as a compatibility facade (not a monolithic implementation file), PySCF-specific computation helpers are split by responsibility:

- **Driver facade / onboarding / workflow glue**: `qchem_stack.chem.drivers.pyscf_driver`
- **Active-space CASCI integral extraction**: `qchem_stack.chem.integrals.pyscf_active_space`
- **One-electron operator builders (fermion / Pauli)**: `qchem_stack.chem.integrals.pyscf_onebody`
- **Lowdin AO transformed views**: `qchem_stack.chem.integrals.pyscf_lowdin`
- **AO / Lowdin data view dataclasses**: `qchem_stack.chem.systems.pyscf_views`

Maintainer rule:

- New PySCF math-heavy transformations go to `chem.integrals.*` or `chem.systems.*`.
- `PySCFDriver` should only orchestrate, validate inputs, and preserve compatibility entry points.
- Keep public import compatibility for existing integrators (`qchem_stack.chem.drivers.__init__` and legacy `pyscf_driver` exports) during migration windows.

## 2. Public surfaces (stability intent)

- **Stable for integrators:** `run_pipeline_sync`, `run_pipeline_from_config`, `ExperimentConfig`, `load_experiment_config`, `repro_json_dumps` / `repro_dict_for_strict_json`, exception types under `qchem_stack.exceptions`.
- **Structured `repro` / Methods payloads:** meaningful keys (`parity_snapshot`, `run_summary`, preview sidecars when enabled, etc.) are documented in **`docs/` technical notes**. There is **no** longer a single centralized frozenset for every `parity_snapshot` key in-tree; after adding or renaming fields, extend **orchestration** (`qchem_stack.orchestration.pipeline`), **export scripts** (`scripts/export_parity_criteria_table.py`, `scripts/check_parity_export_sample.py`), and **focused tests**. Config-only parity-style exports MUST keep **`PARITY_EXPORT_V3_STABLE_KEYS`** in `qchem_stack.protocols.product_contract` in sync. **VQD deflation semantics:** `技术文档_VQD紧缩激发与跨栈对照.md`.
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

- Jobs **`lint`** then **`test`**: **`lint`** runs **`ruff check`** + **`ruff format --check`** on `src/qchem_stack`, `tests`, `scripts`, `examples` (Ubuntu, Python **3.12** only); **`test`** is the pytest/smoke/API matrix (**3.10–3.12**) with **`needs: lint`**. **`docusaurus`** has **`needs: lint`** too.
- `pytest tests` (**`test` job**); CI also exercises marker subsets, `examples/run_all_smoke.py`, and additional smoke scripts — see `.github/workflows/ci.yml`.
- **pip** wheels are cached in Actions (`setup-python` + `cache-dependency-path: pyproject.toml`).
- Optional local hook: **`.pre-commit-config.yaml`** at the repository root (`ruff` + **`ruff-format`** hooks; after `pip install -e ".[dev]"`: `pre-commit install`; `pre-commit run --all-files`).
- Optional extras (PySCF, Qiskit, pytket) exercised in **`test`** matrix and smoke scripts.

## 6. Versioning

- Package version: `pyproject.toml` `[project].version` and runtime `qchem_stack.__version__` (from `importlib.metadata`, fallback `0.1.0` if not installed as a wheel).
- Config field `ExperimentConfig.schema_version` is the experiment **contract** version, independent of the library semver.

## 7. Extension points (vendor-neutral)

1. **Fragment solver** — `FragmentSolverProtocol` + `DMETContext` (replace stub with CCSD / VQE impurity).
2. **Bath update** — `DMETSelfConsistencyLoop.run_with_hooks` / `run_with_sequential_bath_updates`.
3. **Backend** — `BackendSpec` + `executor_from_spec` (swap statevector / Aer / hardware).
4. **Compiler bundle** — `CompilerPassBundle` + TKET bridge for compile metrics.
5. **Strict repro** — extend `repro/export.py` if you add non-JSON types into `repro` deliberately.

## 8. Observability (`run_context`, `pipeline_profile`)

- **`repro["run_context"]`** — `schema: run_context_v1`, `trace_id` (UUID or propagated), optional `client_request_id`. Pass `run_context=` into `run_pipeline_sync` / `run_pipeline_from_config`, or build via `RunContext.from_headers(...)` (`traceparent` → trace id, then `X-Trace-ID`, then new UUID; `X-Request-ID` → `client_request_id`).
- **`repro["pipeline_profile"]`** — `schema: pipeline_profile_v1`, `stages` (per-segment `duration_ms` between successive `mark` calls), `total_wall_ms`. Final segment **`finalize_repro`** covers parity snapshot / run-summary attachment overhead before the profile dict is written. Summaries also appear in `run_summary` (`pipeline_total_wall_ms`, `pipeline_slowest_stage`, etc.).

## 9. HTTP API (optional extra)

Chinese contract tables (`schema`, payloads, SQLite semantics): [技术文档_HTTP_API与SQLite作业队列及可观测性契约.md](技术文档_HTTP_API与SQLite作业队列及可观测性契约.md). **Implementations** live under `src/qchem_stack/api/app.py`.

- Install: `pip install "qchem-stack[api]"`.
- App: `qchem_stack.api.app:app` (FastAPI). Run: `uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000`.
- **`GET /health`** / **`GET /health/ready`** — liveness / SQLite ping (**503** on failure).
- **`GET /v1/meta/product-surface`** — `schema: product_surface_v1` — concise route pointers for consoles.
- **`GET /v1/meta/parity-gaps`** — `schema: capability_gap_export_v1` — `qchem_stack.protocols.product_contract.product_gap_categories()` (+ `gap_anchor_index_v1` when surfaced via capability bundle).
- **`GET /v1/meta/capability-surface`** — `schema: capability_surface_v2` — `capability_map`, `gaps`, `gap_anchor_index_v1`, `mitigation_execution_model`, `open_stack_differentiators`, `operator_pool_registry_export_v1`, `algorithm_registry_export_v1`, `variational_registry_export_v1`, `uccsd_mapping_support_matrix_v1`, `qchem_stack_version`. Regression: `tests/test_api_runs.py::test_capability_surface_matches_product_contract`.
- **`POST /v1/meta/workflow-preview`** — `schema: workflow_preview_v1` — YAML‑only checklist + **`computable_graph_v2`**; implementation **`qchem_stack.integrations.workflow_preview.workflow_preview_payload`** ([CONTRIBUTING § Product contracts](../CONTRIBUTING.md#product-contracts-and-workflow-preview-stable-imports)). Optional repro mirrors: `tests/test_workflow_preview_repro_alignment.py` when YAML enables rich preview.
- **`POST /v1/meta/computables-preview`** — `schema: computables_preview_v1` — computables list + `computable_abstract` v2 (no chemistry run).
- **`GET /v1/meta/ml-md-bridge`** / **`POST /v1/meta/qmef-validate`** / **`POST /v1/meta/ml-md-trainer-stub-fit`** — MD/ML façade (`tests/test_api_ml_md_bridge.py`).
- **`GET /v1/meta/queue-stats`** — `schema: queue_stats_v1`.
- **`GET`/`POST /v1/runs`**, **`GET /v1/runs/{id}/status|summary|events|repro`** — SQLite job semantics as in the linked Chinese HTTP doc (**409** on `/repro` until **DONE**). Trace headers echoed on enqueue.
- **Security:** localhost bind + edge auth before network exposure.

Source of truth: [`src/qchem_stack/api/app.py`](../src/qchem_stack/api/app.py).

## 10. SQLite job kinds (`jobs` store)

- **`job_kind`** column: `pauli_protocol` (pickled `PauliAveragingProtocol`, default) or **`full_pipeline`** (UTF-8 JSON payload: `config_yaml`, optional `run_context`).
- **Enqueue:** `qchem_stack.jobs.pipeline_jobs.enqueue_full_pipeline_run` (optional ``meta_extra`` merged into JSON ``meta``, e.g. ``experiment_id``).
- **Worker:** `qchem-jobs-worker --db …` dispatches via `jobs/worker_dispatch.dispatch_job` (Pauli vs full pipeline).
- **Listing / metrics:** `SqliteJobStore.list_jobs(..., offset=..., experiment_id=..., api_workspace_label=..., api_project_slug=...)` — meta filters share SQL + fallback in §9. Persisted **`timeline_json`** (enqueue seed + `append_timeline` on run/complete/fail/retry). **`count_by_status()`** for queue depth. **`get_job_public_summary`** for lightweight polling without loading the `result` BLOB.

---

*Epistemic boundary:* numerical DMET with full literature correlation-potential fitting plus proprietary optimizers is **not** claimed; the stack emphasizes **auditable orchestration**, explicit capability surfaces, and clean boundaries.
