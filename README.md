# qchem-stack

Open orchestration for quantum-chemistry workloads: **chemistry definition → embeddings / DMET‑shaped workflows → quantum core → protocol state machine → jobs → reproducible `repro` export → ML / MD bridge**.

**Product maintenance:** [CONTRIBUTING.md](CONTRIBUTING.md) · [docs/ENGINEERING_ARCHITECTURE.md](docs/ENGINEERING_ARCHITECTURE.md). Competitive research narratives are referenced below as **historical docs** — they inform UX and backlog but are **not** runtime dependencies.

## Documentation map

**Roadmap vs external literature（按需阅读）**：[竞争定位](docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md) · [工程记忆](docs/工程记忆_Quantinuum对标与数据流技术文档.md) · [差距与实施计划](docs/public_parity_matrix.md)。**方法与矩阵草稿**：[parity](docs/public_parity_matrix.md)。

**Epistemic boundary:** this repo is **independent open-source**. It does not claim binary parity with any vendor closed‑source bundle; narrative docs may cite public papers and manuals for terminology only.

- **Documentation site (Docusaurus; product guides, tutorials, parity, reference)**: [`docusaurus-site/`](docusaurus-site/) — `cd docusaurus-site && npm install && npm start` (local dev, default `http://localhost:3000/`). Production build: `npm run build`. CI runs this build on every PR. See [`docusaurus-site/README.md`](docusaurus-site/README.md).

- **Engineering architecture & long-form contracts** (repo `docs/*.md`, not fully copied into Docusaurus): [`docs/ENGINEERING_ARCHITECTURE.md`](docs/ENGINEERING_ARCHITECTURE.md). Use this for layering, HTTP touchpoints, and strict `repro` posture.

- **Competitive positioning vs Vendor platform and Tangelo (product + technical routes, P0–P3 roadmap)**: [docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md](docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md) — what we **do** compete on (open orchestration, reproducibility, multi-backend, MD/ML, workflow discipline) and what we **do not** (Nexus, H-series lock-in, Vendor platform binary parity).
- **Vendor platform public “How to use” → this repo (topic map)**：[工程记忆 §14](docs/工程记忆_Quantinuum对标与数据流技术文档.md) — aligns [Quantinuum howto](https://www.quantinuum.com/) sections to **open, auditable** paths; **not** closed-wheel parity.
- **Parity matrix (public API vs `qchem_stack`)**: [docs/public_parity_matrix.md](docs/public_parity_matrix.md).
- **Software architecture (layering, typed errors, strict `repro` JSON export)**: [docs/ENGINEERING_ARCHITECTURE.md](docs/ENGINEERING_ARCHITECTURE.md).
- **Engineering memory (物化链、判据、激发态差距、开放栈 §13)**: [docs/工程记忆_Quantinuum对标与数据流技术文档.md](docs/工程记忆_Quantinuum对标与数据流技术文档.md).
- **Detailed technical doc (`CircuitIR`, TKET bridge, job contract)**: [docs/技术文档_CircuitIR与TKET桥接及作业契约.md](docs/技术文档_CircuitIR与TKET桥接及作业契约.md).
- **Qiskit 设备 / Aer 比特串直方图 → Pauli 协议能量**（`get_counts` 路径，与 Vendor platform 公开故事对齐的 shot 真链）: [docs/技术文档_设备比特串与Qiskit采样路径.md](docs/技术文档_设备比特串与Qiskit采样路径.md)。
- **能力差距与路线图附录**（§1 总表、维护约定）：[docs/public_parity_matrix.md](docs/public_parity_matrix.md)。Docusaurus 节选：[gap implementation plan](docusaurus-site/docs/parity/gap-implementation-plan.md)（站内路由 `/parity/gap-implementation-plan`）；正文仍以仓库 `docs/` 母稿为准。  
- **Competitor research notes** (same workspace root): `../PandM/materials/learning/quantum-chem/literature/Quantinuum_量子计算化学竞品研究总索引.md`.
- **Launch/retrieve (Nexus 类比，本地 SQLite)**: [docs/launch_retrieve_nexus_analog.md](docs/launch_retrieve_nexus_analog.md)（`JobHandle.protocol_hash` 与 `PauliAveragingProtocol.launch` / `retrieve`）。

## Capability map (`qchem_stack`)

High‑level textbook / tutorial narratives often mention “drivers → algorithms → protocols → compilers → jobs”. This codebase maps those **concepts** to **modules**:

| Capability area | `qchem_stack` |
|-----------------|---------------|
| Classical chemistry / drivers / active space | `chem/`（`ChemIntegralSolver` registry → **`ClassicalMeanFieldReference`**）；默认端到端 **`scf.driver=pyscf`**；其它求解器 **`chem/solvers/registry.py`**。**Fermion→qubit**：`active_space.fermion_qubit_mapping`。**扩展**：**ddCOSMO**、**PBC**（详见 `ExperimentConfig.chemistry_extended`）。 |
| Variational / excited‑state algorithms | `quantum/`（VQE / ADAPT / IQEB / VQD / QSE / SCEOM 等；示例 YAML 见 `configs/`）。 |
| Protocol lifecycle + measurement plans | `protocols/` + `backends/spec.py`; `protocols/computable.py` exposes preview helpers consumed by integrations. |
| Compiler metrics (optional TKET bridge) | `backends/compile_passes.py`; extra `pip install qchem-stack[pytket]`. |
| Mitigation (analog stacks) | `mitigation/`（PMSV、ZNE、Qermit‑**style** DAG 报告与线性 trace；非商业运行时）。 |
| Tensor‑network‑style stubs | `tensornet/`（研究与契约占位，可按 YAML 选型）。 |
| Jobs + reproducibility | `jobs/`（SQLite、economics analog、`nexus_cloud` 可选侧车）；参阅 [launch/retrieve](docs/launch_retrieve_nexus_analog.md)。 |
| Public methods / roadmap tables | [`docs/public_parity_matrix.md`](docs/public_parity_matrix.md) 等与竞争定位文档（历史对照，非运行时依赖）。 |

## End-to-end orchestration (YAML)

After `pip install -e ".[dev]"` (includes PySCF):

```python
from pathlib import Path
from qchem_stack.orchestration.pipeline import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml", job_db=Path("jobs.sqlite"))
# out contains scf_energy, energy_after_variational, energy_pauli_protocol, resource_summary, repro, job_result
```

For **Methods‑style exports** (`computable_abstract_v2`, `hamiltonian_meta`), use `WorkflowCoordinator` (`qchem_stack.orchestration.WorkflowCoordinator`): it wraps `run_pipeline_from_config` and sets `out["methods_sidecar"]`. A packaged tutorial chain lives at `configs/tutorial_chain_h2.yaml` (YAML id is historical—the pipeline is vanilla `qchem_stack`).

CI runs `python scripts/smoke_pipeline.py` then `python scripts/smoke_pipeline.py --excited-only` (`configs/example_h2_excited_smoke.yaml`, VQD without Pauli protocol), **`--iqeb`** (H2 IQEB), **`--projection-trace`** (projection L1 YAML), and marker subsets **`pytest -m l1_excited`** / **`pytest -m l1_md_ml`**. Locally, `python scripts/smoke_pipeline.py --excited` runs both packaged YAMLs in one go. Optional **L3** numerical gate: `QCHEM_RUN_L3=1 pytest -m l3` (see `tests/test_l3_benchmark_smoke.py`, `integrations/l3_algorithm_benchmark.py`).

### Optional HTTP API (`fastapi`)

With local pinned venv runner, run:

```bash
./scripts/venv-run uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

`GET /health` — liveness. **`GET /health/ready`** — default SQLite usable. **`GET /v1/meta/product-surface`** — pointer bundle for dashboards. **`GET /v1/meta/parity-gaps`** — **`capability_gap_export_v1`** (product gaps from `qchem_stack.protocols.product_contract`). **`GET /v1/meta/capability-surface`** — **`capability_surface_v2`** (**`capability_map`**, **`gaps`**, **`gap_anchor_index_v1`**, mitigation + differentiators bundles, registries incl. **`operator_pool_registry_export_v1`** / **`algorithm_registry_export_v1`** / **`variational_registry_export_v1`**, **`uccsd_mapping_support_matrix_v1`**). **`POST /v1/meta/workflow-preview`** / **`POST /v1/meta/computables-preview`** — YAML‑only previews (no chemistry). **`GET /v1/meta/queue-stats`**, **`GET`/`POST /v1/runs`**, polls + slim **`GET /v1/runs/{id}/summary`**, **`GET /v1/runs/{id}/repro`** (**409** until **DONE**). Trace headers echo on POST. See [`src/qchem_stack/api/app.py`](src/qchem_stack/api/app.py) and [ENGINEERING_ARCHITECTURE §9](docs/ENGINEERING_ARCHITECTURE.md).

## Install

```bash
cd qchem_qml_md
pip install -e ".[dev]"
```

Local development commands use [`scripts/venv-run`](scripts/venv-run): it prepends the directory of the chosen interpreter to `PATH` and runs your command. **`QCHEM_STACK_PYTHON`** selects the interpreter when set; otherwise the default in `scripts/venv-run` applies (repo maintainers set this to their `conda base` or `.venv` Python).

PySCF, Qiskit, and **pytket** (TKET bridge for resource stats) are optional extras: `pip install -e ".[all]"` includes all declared extras, or `pip install -e ".[pytket]"` alone.

## Lint and tests (CI parity)

```bash
./scripts/venv-run ruff check src/qchem_stack tests scripts examples
./scripts/venv-run ruff format --check src/qchem_stack tests scripts examples
./scripts/venv-run pytest tests -q --tb=short
```

Smoke scripts and marker subsets mirror [.github/workflows/ci.yml](.github/workflows/ci.yml) (**`lint`** job runs Ruff; **`test`** is the Python matrix and smoke steps). See [CONTRIBUTING.md](CONTRIBUTING.md) for merge gates, optional markers, and optional **pre-commit** (the `pre-commit` CLI ships with **`pip install -e ".[dev]"`**; same Ruff paths as CI).

## Quick start

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.chem.bridges.mean_field_reference import ClassicalMeanFieldReference
from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_classical_reference

cfg = load_experiment_config("configs/example_h2.yaml")
drv = PySCFDriver.from_config(cfg)
result = drv.run_rhf()
ref = ClassicalMeanFieldReference(
    mf=result.mf,
    e_tot=float(result.e_tot),
    mo_energy=result.mo_energy,
    molecular_system=result.molecular_system,
    driver_meta=dict(result.driver_meta),
)
h = molecular_hamiltonian_from_classical_reference(
    ref,
    n_active_orbitals=2,
    n_active_electrons=2,
)
# Optional JW knobs from YAML ``active_space``: ``prefer_restricted_spatial_fermion_for_jordan_wigner``,
# ``jordan_wigner_coeff_atol`` (pass-through kwargs on ``molecular_hamiltonian_from_classical_reference``).
```

**Unified classical mean field** (any `scf.driver` registered in `chem/solvers`): `classical_mean_field_via_solver_bridge(cfg)` in `qchem_stack.chem.bridges.facade` returns `MolecularMeanFieldResult` with canonical `driver_meta` headers — same interchange shape the pipeline uses after SCF.

### Simulators (Qiskit / IonStack)

- **YAML**: set `backend.provider` to `statevector`, `qiskit`, or `ionstack`; optional `backend.target_energy_stderr` tightens `recommended_shots_per_circuit`; use `backend_spec_from_config(cfg)` when building a `BackendSpec`.
- **Qiskit**: `pip install qchem-stack[quantum]`; optional `qiskit_mode: estimator` uses primitives fallback.
- **IonStack**: inject `backend.meta["expectation_fn"]` or set `ionstack_endpoint: mock` with `meta.mock_energy` for tests; replace with your REST/gRPC client inside `IonStackHeaExecutor`.
- **VQE + YAML backend**: `from qchem_stack.quantum.runtime import vqe_from_experiment_config` (kept out of `quantum` package `__init__` to avoid import cycles).
- **Pauli grouping + shot budget**: `build_measurement_plan`, `recommended_shots_per_circuit`, `energy_estimate_with_uncertainty`; `PauliAveragingProtocol` builds one logical circuit per commuting group and reports `energy_stderr` / `total_shots_budget`. Set `quantum.run_sampled_pauli_protocol: true` for **grouped Monte Carlo** energy on the HEA statevector (`backends/pauli_shot_sim.py`). Set `quantum.run_qiskit_shots_pauli_protocol: true` (and `backend.provider: qiskit` + `pip install .[quantum]`) for **Qiskit `get_counts` bitstrings** per group on Aer or a real `Backend` (`backends/qiskit_pauli_shots.py`; mutually exclusive with `run_sampled_pauli_protocol`). **Semantics** (default both off): expectation from the executor; `energy_stderr` is a **classical conservative bound**—not the SE of shot recombination unless `run_sampled` or `run_qiskit_shots` is on.
- **Parity / criteria export**: `python scripts/export_parity_criteria_table.py configs/example_h2.yaml [--results run.json]`; config-only exports must satisfy **`PARITY_EXPORT_V3_STABLE_KEYS`** in [`qchem_stack.protocols.product_contract`](src/qchem_stack/protocols/product_contract.py); `scripts/check_parity_export_sample.py` enforces them on sampled configs.
- **QSE / SCEOM / VQD (excited)**: `quantum/qse_transition.py` (Pauli transition schedule); `run_sceom_nested_commutator_from_hea` in `quantum/algorithms/sceom.py`; VQD `run(..., shots_objective=, shots_overlap=, shots_weight=)` populates `meta["vqd_channels"][*]["three_protocol"]`.
- **YAML VQD**: under `quantum:` set `vqd_after_variational: true` and optional `vqd_shots_objective` / `vqd_shots_overlap` / `vqd_shots_weight`; pipeline adds `out["vqd"]`.
- **YAML QSE / SCEOM**: `qse_after_variational` / `sceom_after_variational` with `qse_shot_mode` (`exact`, `gaussian_h`, `pauli_transitions`) and shot budgets; pipeline adds `out["qse"]` / `out["sceom"]`.
- **Pipeline VQD** reuses the variational ground state (`ground_angles` / `ground_energy`); `out["excited_resource_summary"]` aggregates YAML shot hints and QSE schedule meta for export scripts.
- **`resource_summary`**: always includes `pauli_averaging_protocol_ran` when the Pauli stage runs; if any excited stage ran, adds `excited_stages`, `excited_shots_upper_bound`, and `sum_shots_total_with_excited_upper_bound` (protocol `sum_shots` plus excited bound). If `use_pauli_protocol: false` but QSE/SCEOM/VQD ran, a minimal `resource_summary` is still emitted for the excited block.
- **`repro.run_summary`**: after every sync run, stage list (`stages_completed`), `scf_energy`, `energy_pauli_protocol` (if Pauli stage ran), VQE (`vqe_maxiter_yaml`, `vqe_nfev`) or ADAPT (`adapt_max_iter_yaml`, `adapt_total_gradient_evals`, `adapt_steps_recorded`, `adapt_excitation_layers`), plus `n_pauli_terms` / `n_pauli_groups` / `n_circuits` / `n_qubits`, **`protocol_total_shots_budget` / `protocol_n_measurement_circuits` / `protocol_shots_per_circuit_effective` / `protocol_energy_stderr`** from `protocol_counts`, and after `run_pipeline_from_config(..., job_db=...)`, **`async_job_id`**, **`protocol_hash_prefix`**, and **`job_async_*`** from the SQLite worker result. May also surface **`nexus_analog_hqc_units`**, **`mitigation_graph_report_present`**, **`mitigation_dag_execution_present`**, **`nexus_cloud_repro`**. **`repro.parity_snapshot`** (config-only, at run start) also records `use_pauli_protocol`, `vqe_depth` / `vqe_maxiter` / `adapt_max_iter`, sampled/histogram YAML flags, `backend_provider`, `zne_enabled`, **`mitigation_zne_scales`**, `chemistry_extended`（含 PBC/k 网字段）, `nexus_analog` / **`nexus_cloud`**, `tensornet_*` 开关, and excited-state YAML plus `vqd_penalty_weight`.
- **`run_pipeline_from_config`** reuses the `QubitHamiltonian` from the in-process sync pass (no second PySCF → qubit-operator build for the SQLite job lane).
- **Jobs**: `JobStatus`, `process_job_with_retry`, SQLite columns `retry_count` / `error_message` / `protocol_hash` (migration on open).

### `PauliAveragingProtocol` / `protocol_counts` semantics

- **`expectation_source`**: `executor_exact_or_device_mean` (default) uses an exact or backend mean energy; `grouped_shot_simulation_statevector` when `run_sampled_pauli_protocol: true` (see `backends/pauli_shot_sim.py`); `qiskit_shot_counts_get_counts` when `run_qiskit_shots_pauli_protocol: true` (see `backends/qiskit_pauli_shots.py`).
- **`energy_stderr_model`**: `conservative_sum_bound_equal_shots` for the default path, `sample_stderr_independent_groups_approx` when `run_sampled` is on, or `empirical_shot_variance_independent_groups_approx` for the Qiskit bitstring path.
- **`pmsv_report`** (if `mitigation.pmsv_enabled`): stabilizer list, `retention_rate`, `pmsv_stderr_scale`, optional `kept_shots_simulated` — for Methods, not a replacement for readout tomography.
- **ZNE** (if `mitigation.zne_enabled`): YAML **`mitigation.zne_scales`** is passed to `PauliAveragingProtocol` as `zne_scales`; `protocol_counts` can include `zne_energies` from the stub `zne_scale_energy`.
- **Outputs**: `resource_rows` and duplicate **`pauli_measurement_ledger`** (per-measurement-circuit table for export); with excited stages, **`resource_summary.excited_shot_accounting`** breaks VQD/QSE/SCEOM shot upper bounds by channel.
- **Embedding / parity**: `embedding.*` in YAML is copied into `repro.parity_snapshot` (`embedding_mode`, `n_scf_cycles_embedding`, `classical_reference_method`, `embedding_fragment_labels`). See `configs/example_h2_embedding_parity.yaml`.
- **Sampled path smoke**: `python scripts/smoke_pipeline.py --sampled` uses `configs/example_h2_sampled.yaml`.
- **Qiskit shots (optional, needs Qiskit + Aer)**: `python scripts/smoke_pipeline.py --qiskit-shots` uses `configs/example_h2_qiskit_shots.yaml` (adds a few seconds for Aer transpile+shots).
- **QPE “dual track” (same repo)**: `python scripts/run_qpe_track_demo.py` (no PySCF); config marker `configs/qpe_dual_track_demo.yaml`.

## Layout

- `qchem_stack/chem` — molecular spec, **bridges**, PySCF driver (optional PBC + k‑mesh, ddCOSMO), embedding, qubit Hamiltonian (`active_space.fermion_qubit_mapping`)
- `qchem_stack/quantum` — ansätze, VQE / ADAPT / IQEB / VQD / QSE
- `qchem_stack/protocols` — five-stage protocol, shot dataframe, `computable` helpers, job pickle surface
- `qchem_stack/mitigation` — PMSV, SPAM, ZNE, `qermit_analog` (DAG report), `qermit_runtime` (linear trace)
- `qchem_stack/tensornet` — CuTensorNet *protocol* stub and optional `opt_einsum` / cupy / cuquantum import checks (`quantum.tensornet_expectation_stub`, `tensornet_contraction_engine`)
- `qchem_stack/backends` — `BackendSpec` (`provider`: `statevector` | `qiskit` | `ionstack`), `executor_from_spec`, Qiskit / IonStack hooks, pass bundles, resource metrics
- `qchem_stack/jobs` — SQLite job store, `nexus_analog` cost rows, optional `nexus_cloud` sidecar
- `qchem_stack/ml` — cache, surrogate, active learning, `MLPolicy`
- `qchem_stack/md_bridge` — `QMEFDataset`, trainer protocol, NequIP/MACE hooks
- `qchem_stack/qpe_qec_demo` — QPE variants + adapter stub toward fault-tolerant demos
- `qchem_stack/orchestration` — YAML-driven PySCF → VQE/ADAPT → `PauliAveragingProtocol` → optional SQLite jobs

## License

Apache-2.0
