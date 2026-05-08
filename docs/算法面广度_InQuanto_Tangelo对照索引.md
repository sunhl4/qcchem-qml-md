# 算法面广度：与 InQuanto / Tangelo **公开叙事**的对照索引（L1 / 开源栈）

本文是**工程路由表**，不是闭源产品 L0 等价声明。同源机读材料：`docs/inquanto_public_parity_matrix.md` §2、**`GET /v1/meta/capability-surface`**（内嵌 **`operator_pool_registry_export_v1`**）、`scripts/export_parity_criteria_table.py`、parity 导出中的同 schema。

## 1. 栈内落点（模块化）

| 能力类 | 模块 / 入口 |
|--------|-------------|
| 变分主链（VQE / HEA / JW-UCCSD） | `quantum/algorithms/vqe.py`, `uccsd_vqe.py`, `variational_plugins/builtins.py` |
| ADAPT / Tetris-ADAPT | `quantum/algorithms/adapt.py`，池：`quantum/operator_pool_registry.py`，YAML `quantum.adapt_pool_id` |
| IQEB | `quantum/algorithms/iqeb.py`，YAML `quantum.iqeb_pool_id` |
| VQD / QSE / SCEOM | `quantum/algorithms/excited.py`, `quantum/qse_transition.py`, `quantum/algorithms/sceom.py`，契约：`excited_*_bundle_v1`、`excited_protocol_contract_v1` |
| QPE demo / Bayesian stub | `quantum/algorithms/qpe.py`, `qpe_qec_demo/pipeline_track.py` |
| VQS / McLachlan 玩具侧车 | `quantum/algorithms/vqs.py`, `vqs_pipeline_track.py` |
| YAML 插件工厂 | `quantum.algorithm_factory`，`variational_plugins/registry.py` |
| 可检证导出 / Methods | `scripts/export_parity_criteria_table.py`，`methods_resource_unified_v1` |

## 2. 相对「竞品工具箱」的**长板**（开源可辩护）

- **全流程 JSON 契约 + 回归**：同一 YAML → 管线 → `repro.run_summary` / parity export → HTTP `workflow-preview`（见 `integrations/inquanto_workflow_preview.py`）。
- **算符池可版本化 id**：例如 `fermionic_uccsd`、`fermionic_uccsd_singles`、`fermionic_uccsd_doubles_only`、`iqeb_qubit_excitation`、`toy_pair_xx`；YAML 还可写 **`pool_id_aliases`** 中的别名 `qubit_excitation` → `iqeb_qubit_excitation`、`uccsd_jw` → `fermionic_uccsd`（详见 `operator_pool_registry_export_v1`）。
- **多后端与 Pauli 路径分类**：statevector / Qiskit shots / sampled MC 等 — 需在技术文档写明每种路径的语义边界。

## 3. 相对 InQuanto / Tangelo **仍常为 partial** 的方向（坦诚）

- 闭源侧的**全套化学激发 taxonomy**与默认合成/regrouping 策略；
- BK/SCBK 上包装的 UCCSD 电路语义（见 `docs/技术文档_UCCSD_JW与BK_SCBK电路边界.md`）；
- 产品级动力学 / FT-QPE（当前 QPE/VQS 为侧车 + 契约，非主编排等价）。

## 4. 深度门禁（可选）

- 设置 **`QCHEM_RUN_L3=1`**：`pytest -m l3`，对 **`integrations.l3_algorithm_benchmark.L3_PYTEST_YAMLS`** 管线回归（默认 **6** 条：ADAPT singles/doubles、`uccsd_jw` **别名**、IQEB fermionic doubles、`qubit_excitation` **别名**、excited-smoke）；也可用 `scripts/l3_algorithm_benchmark_report.py`（默认 **`DEFAULT_BENCHMARK_YAMLS`**）导出 **`algorithm_benchmark_bundle_v1`**（能量、`nfev`、耗时等）做论文/对标表；`--merged` 附带 **`merged_experiment_benchmark_v1`**（总量 + **`by_quantum_algorithm_yaml`** 分组）。
- Roadmap：`docs/execution/day91_next_phase_plan_2026Q3.md` Week 5–6。

## 5. 本仓「广 / 深」收口声明（2026Q3）

- **广（registry + 可跑 YAML + 机读导出）**：算符池 canonical id、**别名**、ADAPT/IQEB 切片池、L3 代表配置、parity 抽样与 `operator_pool_registry_export_v1`（**含 `GET /v1/meta/capability-surface`** 内嵌）已对齐；再扩面应走明确 backlog / gap id，而非未文档化的静默实现。
- **深（可选 L3）**：`algorithm_benchmark_bundle_v1` 与 **`merged_experiment_benchmark_v1`**（含 **`by_quantum_algorithm_yaml`**）定义可重复能量/耗时基线；更细的 SLA 仍以矩阵 **`partial`** 与专项文档为准。
- **刻意不列入「待收口」**：竞品 **全套激发 taxonomy**、**BK(SCBK) 上等价 UCCSD 电路包装**、**商业级动力学与 FT-QPE** — 保持 §3 与 `inquanto_public_parity_matrix.md` 的 **`partial`** 口径，以免与 L0 宣称混淆。
