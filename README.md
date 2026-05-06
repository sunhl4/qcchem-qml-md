# qchem-stack

Open orchestration layer aligned with an InQuanto-style pipeline: **chemistry input → downfolding → quantum core → protocol state machine → jobs → ML fusion → MD force-field dataset**.

## Documentation map (all engineering docs)

**Single index** (Chinese canonical, paths, merge log, reading order): [docs/技术文档_软件工程文档总索引.md](docs/技术文档_软件工程文档总索引.md).

## Boundaries and public parity

This project is an **independent open-source** stack: it does **not** copy Quantinuum closed-source products. Capabilities are traced to **public** InQuanto / TKET / Nexus **documentation and papers** only.

- **Documentation site (VitePress; `/product/` landing + pillar guides + optional public-doc benchmark map)**: [`docs-site/`](docs-site/) — `npm install && npm run docs:dev` (**preview opens in your default browser** at `http://localhost:5173/`; not an embedded IDE panel). Production build: `npm run docs:build`. After copying docs from `docs/`, run `npm run fix-links` if paths drift.

- **InQuanto public docs site — multi-volume report + appendices A/B/C + 295-node JSON backlog** (IA / Diátaxis / Nexus boundary analysis; **appendix-C ~21.7k lines**; machine backlog [`docs/inquanto-node-backlog.generated.json`](docs/inquanto-node-backlog.generated.json)): [`docs/architecture-report-quantinuum-inquanto-web/INDEX.md`](docs/architecture-report-quantinuum-inquanto-web/INDEX.md) — **stays in repo** to inform `docs-site` UX; not copied into the VitePress tree. Regenerate: `cd docs-site && npm run report:inquanto-appendix && npm run report:inquanto-backlog`; gate: `npm run check:mirror && npm run check:node-backlog`.

- **Competitive positioning vs InQuanto and Tangelo (product + technical routes, P0–P3 roadmap)**: [docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md](docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md) — what we **do** compete on (open orchestration, reproducibility, multi-backend, MD/ML, workflow discipline) and what we **do not** (Nexus, H-series lock-in, InQuanto binary parity).
- **InQuanto public “How to use” → this repo (topic map)**：[docs/InQuanto_manual_howto_与_qchem_stack_映射.md](docs/InQuanto_manual_howto_与_qchem_stack_映射.md) — aligns [Quantinuum howto](https://docs.quantinuum.com/inquanto/manual/howto.html) sections (workflows, chemistry prep, computables/protocols, expert use) to **open, auditable** paths (`pipeline`, `protocols`, `chem`, optional TKET bridge); **not** closed-wheel parity.
- **Parity matrix (public API vs `qchem_stack`)**: [docs/inquanto_public_parity_matrix.md](docs/inquanto_public_parity_matrix.md).
- **Software architecture (layering, typed errors, strict `repro` JSON export)**: [docs/ENGINEERING_ARCHITECTURE.md](docs/ENGINEERING_ARCHITECTURE.md).
- **Engineering memory (竞品数据流、判据表、激发态差距、A/B/C 路线图)**: [docs/工程记忆_Quantinuum对标与数据流技术文档.md](docs/工程记忆_Quantinuum对标与数据流技术文档.md).
- **Detailed technical doc (`CircuitIR`, TKET bridge, job contract)**: [docs/技术文档_CircuitIR与TKET桥接及作业契约.md](docs/技术文档_CircuitIR与TKET桥接及作业契约.md).
- **Qiskit 设备 / Aer 比特串直方图 → Pauli 协议能量**（`get_counts` 路径，与 InQuanto 公开故事对齐的 shot 真链）: [docs/技术文档_设备比特串与Qiskit采样路径.md](docs/技术文档_设备比特串与Qiskit采样路径.md)。
- **与 InQuanto 能力差距 + 分阶段计划**（差什么、不做什么、P0–P2）：[docs/与InQuanto能力差距与实施计划.md](docs/与InQuanto能力差距与实施计划.md)（`repro`、export **v2**、**§1 总表**与 [parity 矩阵](docs/inquanto_public_parity_matrix.md) 随代码维护同步）。  
- **路线图 P2（研究深度 · WBS · 闸门）**：[docs/P2_详细实施计划.md](docs/P2_详细实施计划.md)；文档站可读镜像：`docs-site` 路由 **`/concept/p2-detailed-plan`**（英文摘要 **`/en/concept/p2-detailed-plan`**）。维护角色占位：[docs/MAINTAINERS.md](docs/MAINTAINERS.md)。  
- **原「不排期」项落代码说明**（Nexus 类比、Qermit 图+运行时、张量网 stub+引擎、PBC/k 点/ddCOSMO 等，**非** 商业云/闭源同构）：[docs/不排期项_转排期与实现说明.md](docs/不排期项_转排期与实现说明.md)。
- **Competitor research notes** (same workspace root): `../PandM/materials/learning/quantum-chem/literature/Quantinuum_量子计算化学竞品研究总索引.md`.
- **Launch/retrieve (Nexus 类比，本地 SQLite)**: [docs/launch_retrieve_nexus_analog.md](docs/launch_retrieve_nexus_analog.md)（`JobHandle.protocol_hash` 与 `PauliAveragingProtocol.launch` / `retrieve`）。

## InQuanto public stack vs this repo (工程复现入口)

Public Quantinuum docs describe a chemistry orchestration **layer** (PySCF, algorithms, `Protocols`, TKET, cloud jobs). This repo maps those **names** to **directories**—without claiming binary parity to closed-source InQuanto.

| InQuanto (public) | `qchem_stack` |
|-------------------|---------------|
| PySCF / drivers / active space | `qchem_stack/chem/` (e.g. `chem/drivers/`, `chem/hamiltonian.py`)；**fermion→qubit**：`active_space.fermion_qubit_mapping`（`jordan_wigner` / `bravyi_kitaev` / `symmetry_conserving_bravyi_kitaev`）；扩展：`chemistry_extended` 上 **ddCOSMO**、**PBC**（`pbc_kpoint_mesh` → RHF@Γ 或 **KRHF** + 选 k 的 CASCI）、名称映射 `chem/inquanto_driver_surface.py` |
| `Algorithm*`, VQE / ADAPT / **IQEB** / VQD / QSE / SCEOM | `qchem_stack/quantum/`, `quantum/qse_transition.py`；**IQEB**：`quantum.algorithm=iqeb`，`configs/example_h2_iqeb.yaml` |
| `Protocol` 五阶段、资源表 `dataframe_circuit_shot` | `qchem_stack/protocols/`, `backends/spec.py`；`protocols/computable.py` 薄层（非一等 `Computable` 图） |
| Passes / TKET-style metrics (optional) | `backends/compile_passes.py`; optional `pip install qchem-stack[pytket]` then `backends/pytket_bridge.py` |
| PMSV / ZNE / SPAM；Qermit **风格** 图+执行 | `qchem_stack/mitigation/`（含 `qermit_analog` DAG 报告、`qermit_runtime` 线性执行迹 → `mitigation_dag_execution`；**非** Qermit 商业运行时） |
| `CuTensorNetProtocol` **类比** | `qchem_stack/tensornet/`（`cutensornet_protocol_stub` + `opt_einsum` / cupy / **cuquantum 检测** 等；**非** `inquanto-cutensornet`） |
| 计价 (HQC **类比**) + 作业 + 可选云侧车 | `jobs/cost`, `jobs/nexus_analog`, **可选** `jobs/nexus_cloud`（`http`/`mock`）；异步仍见 [launch/retrieve](docs/launch_retrieve_nexus_analog.md)（SQLite + `NexusAnalogSpec` 与同步计价一致） |
| Parity 表、判据与资源双轨说明 | [docs/inquanto_public_parity_matrix.md](docs/inquanto_public_parity_matrix.md), [工程记忆](docs/工程记忆_Quantinuum对标与数据流技术文档.md), [技术文档](docs/技术文档_CircuitIR与TKET桥接及作业契约.md) |
| 对 InQuanto / Tangelo 的**竞争定位与 P0–P3 路线** | [docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md](docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md) |

## End-to-end orchestration (YAML)

After `pip install -e ".[dev]"` (includes PySCF):

```python
from pathlib import Path
from qchem_stack.orchestration.pipeline import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2.yaml", job_db=Path("jobs.sqlite"))
# out contains scf_energy, energy_after_variational, energy_pauli_protocol, resource_summary, repro, job_result
```

For an InQuanto-style **Methods sidecar** (computable abstract v2 + `hamiltonian_meta` fingerprint), use `WorkflowCoordinator` (`qchem_stack.orchestration.WorkflowCoordinator`): it wraps `run_pipeline_from_config` and sets `out["methods_sidecar"]`. A packaged **tutorial-shaped** chain (ROHF, DMET labels, ADAPT, PMSV, compiler pass lists) lives at `configs/tutorial_inquanto_chain_h2.yaml`.

CI runs `python scripts/smoke_pipeline.py` then `python scripts/smoke_pipeline.py --excited-only` (`configs/example_h2_excited_smoke.yaml`, VQD without Pauli protocol), **`--iqeb`** (H2 IQEB), **`--projection-trace`** (projection L1 YAML), and marker subsets **`pytest -m l1_excited`** / **`pytest -m l1_md_ml`**. Locally, `python scripts/smoke_pipeline.py --excited` runs both packaged YAMLs in one go.

P1 **backend / mapping conformance** (needs PySCF; Qiskit optional): `pytest tests/test_backend_conformance.py`.

### Optional HTTP API (`fastapi`)

With `pip install -e ".[dev]"` or `pip install -e ".[api]"`, run:

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

`GET /health` is a cheap liveness check; **`GET /health/ready`** pings the default SQLite job path. **`GET /v1/meta/parity-gaps`** is the gap list; **`GET /v1/meta/queue-stats`** counts jobs by status; **`POST /v1/meta/computables-preview`** returns InQuanto-style **Computable** items + **`computable_abstract` v2** from YAML alone (no chemistry run). **`GET /v1/runs`** lists jobs (`experiment_id` / **`api_workspace_label`** filters, **`offset`** / **`limit`**). **`GET /v1/runs/{id}/repro`** returns only **`repro` when DONE** (**409** while queued). **`GET /v1/runs/{id}/status`** and **`/events`** are lightweight polls. **`POST /v1/runs`** accepts YAML (`experiment_yaml`, `sync`, optional `job_db_path`, optional **`workspace_label`** → meta); async **202** + **`run_enqueue_response_v1`**; sync **`full_pipeline_job_result_v1`**. POST responses echo **`X-Trace-ID`** / **`X-Request-ID`**. Invalid YAML/config → **400** / **422**. Drain with `qchem-jobs-worker` / **`qchem-pipeline-worker`**. See [docs/ENGINEERING_ARCHITECTURE.md](docs/ENGINEERING_ARCHITECTURE.md) §8–9.

## Install

```bash
cd qchem_qml_md
pip install -e ".[dev]"
```

PySCF, Qiskit, and **pytket** (TKET bridge for resource stats) are optional extras: `pip install -e ".[all]"` includes all declared extras, or `pip install -e ".[pytket]"` alone.

## Quick start

```python
from qchem_stack.config import load_experiment_config
from qchem_stack.chem.drivers.pyscf_driver import PySCFDriver
from qchem_stack.chem.hamiltonian import molecular_hamiltonian_from_pyscf

cfg = load_experiment_config("configs/example_h2.yaml")
drv = PySCFDriver.from_config(cfg)
result = drv.run_rhf()
h = molecular_hamiltonian_from_pyscf(result, n_active_orbitals=2, n_active_electrons=2)
```

### Simulators (Qiskit / IonStack)

- **YAML**: set `backend.provider` to `statevector`, `qiskit`, or `ionstack`; optional `backend.target_energy_stderr` tightens `recommended_shots_per_circuit`; use `backend_spec_from_config(cfg)` when building a `BackendSpec`.
- **Qiskit**: `pip install qchem-stack[quantum]`; optional `qiskit_mode: estimator` uses primitives fallback.
- **IonStack**: inject `backend.meta["expectation_fn"]` or set `ionstack_endpoint: mock` with `meta.mock_energy` for tests; replace with your REST/gRPC client inside `IonStackHeaExecutor`.
- **VQE + YAML backend**: `from qchem_stack.quantum.runtime import vqe_from_experiment_config` (kept out of `quantum` package `__init__` to avoid import cycles).
- **Pauli grouping + shot budget**: `build_measurement_plan`, `recommended_shots_per_circuit`, `energy_estimate_with_uncertainty`; `PauliAveragingProtocol` builds one logical circuit per commuting group and reports `energy_stderr` / `total_shots_budget`. Set `quantum.run_sampled_pauli_protocol: true` for **grouped Monte Carlo** energy on the HEA statevector (`backends/pauli_shot_sim.py`). Set `quantum.run_qiskit_shots_pauli_protocol: true` (and `backend.provider: qiskit` + `pip install .[quantum]`) for **Qiskit `get_counts` bitstrings** per group on Aer or a real `Backend` (`backends/qiskit_pauli_shots.py`; mutually exclusive with `run_sampled_pauli_protocol`). **Semantics** (default both off): expectation from the executor; `energy_stderr` is a **classical conservative bound**—not the SE of shot recombination unless `run_sampled` or `run_qiskit_shots` is on.
- **Parity criteria export**: `python scripts/export_parity_criteria_table.py configs/example_h2.yaml [--results run.json]`; with `--results`, adds flat energy keys (`*_from_run`), `run_summary` mirrors (`n_pauli_terms_mirror_run_summary`, etc.).
- **QSE / SCEOM / VQD (excited)**: `quantum/qse_transition.py` (Pauli transition schedule); `run_sceom_nested_commutator_from_hea` in `quantum/algorithms/sceom.py`; VQD `run(..., shots_objective=, shots_overlap=, shots_weight=)` populates `meta["vqd_channels"][*]["three_protocol"]`.
- **YAML VQD**: under `quantum:` set `vqd_after_variational: true` and optional `vqd_shots_objective` / `vqd_shots_overlap` / `vqd_shots_weight`; pipeline adds `out["vqd"]`.
- **YAML QSE / SCEOM**: `qse_after_variational` / `sceom_after_variational` with `qse_shot_mode` (`exact`, `gaussian_h`, `pauli_transitions`) and shot budgets; pipeline adds `out["qse"]` / `out["sceom"]`.
- **Pipeline VQD** reuses the variational ground state (`ground_angles` / `ground_energy`); `out["excited_resource_summary"]` aggregates YAML shot hints and QSE schedule meta for export scripts.
- **`resource_summary`**: always includes `pauli_averaging_protocol_ran` when the Pauli stage runs; if any excited stage ran, adds `excited_stages`, `excited_shots_upper_bound`, and `sum_shots_total_with_excited_upper_bound` (protocol `sum_shots` plus excited bound). If `use_pauli_protocol: false` but QSE/SCEOM/VQD ran, a minimal `resource_summary` is still emitted for the excited block.
- **`repro.run_summary`**: after every sync run, stage list (`stages_completed`), `scf_energy`, `energy_pauli_protocol` (if Pauli stage ran), VQE (`vqe_maxiter_yaml`, `vqe_nfev`) or ADAPT (`adapt_max_iter_yaml`, `adapt_total_gradient_evals`, `adapt_steps_recorded`, `adapt_excitation_layers`), plus `n_pauli_terms` / `n_pauli_groups` / `n_circuits` / `n_qubits`, **`protocol_total_shots_budget` / `protocol_n_measurement_circuits` / `protocol_shots_per_circuit_effective` / `protocol_energy_stderr`** from `protocol_counts`, and after `run_pipeline_from_config(..., job_db=...)`, **`async_job_id`**, **`protocol_hash_prefix`**, and **`job_async_*`** from the SQLite worker result. May also surface **`nexus_analog_hqc_units`**, **`mitigation_graph_report_present`**, **`mitigation_dag_execution_present`**, **`nexus_cloud_repro`**. **`repro.parity_snapshot`** (config-only, at run start) also records `use_pauli_protocol`, `vqe_depth` / `vqe_maxiter` / `adapt_max_iter`, sampled/histogram YAML flags, `backend_provider`, `zne_enabled`, **`mitigation_zne_scales`**, `chemistry_extended`（含 PBC/k 网字段）, `nexus_analog` / **`nexus_cloud`**, `tensornet_*` 开关, and excited-state YAML plus `vqd_penalty_weight`.
- **`run_pipeline_from_config`** reuses the `QubitHamiltonian` from the in-process sync pass (no second PySCF → qubit-operator build for the SQLite job lane).
- **Jobs**: `JobStatus`, `process_job_with_retry`, SQLite columns `retry_count` / `error_message` / `protocol_hash` (migration on open).

### `PauliAveragingProtocol` / `protocol_counts` semantics (vs InQuanto `run` → `evaluate`)

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

- `qchem_stack/chem` — molecular spec, PySCF driver (incl. optional PBC + k-mesh, ddCOSMO), embedding hooks, qubit Hamiltonian (`active_space.fermion_qubit_mapping`: JW or BK), InQuanto-name alias table
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
