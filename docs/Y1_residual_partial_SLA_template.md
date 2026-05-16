# Y1 残余 `partial` 与 SLA 模板（Q4 / 年度签off）

**用途**：矩阵或差距表中仍为 `partial` 且**本年内未收束为 yes** 的项，必须有一行 SLA，避免「口头对齐」。筛选候选时可用机读 backlog：`jq '.nodes[] | select(.status=="partial")'` 见 `docs/public_parity_matrix.md（机读 gaps 以 product_contract 为准）`。

**负责人**：流程角色见 [MAINTAINERS.md](MAINTAINERS.md)；表格内可留空或填职能角色。

| gap.id 或矩阵节 | 残余能力摘要 | 目标状态（yes / 仍 partial） | 目标季度 | 负责人 | 依赖（PySCF / GPU / …） |
|------------------|--------------|------------------------------|----------|--------|-------------------------|
| `ucc_chem_ansatz` | 化学 UCC 池与闭源默认非逐条对齐 | partial + JW UCCSD/Trotter YAML | Y1-Q4 | 见 MAINTAINERS | |
| `tensornet` | TN 化学尺度收缩 | **n/a**（开放栈 stub；不宣称 `vendor-cutensornet`） | Y2-Q2 | 见 MAINTAINERS | 见矩阵 §1 |
| `drivers_cosmo_pbc` | 全 driver 表面 / 多 k / 溶剂边界 | partial_kmesh | Y1-Q4 | 见 MAINTAINERS | PySCF 版本；变更 `PYSCF_MIN_VERSION_RECOMMENDED` 时同步矩阵 §3；回归见 `tests/test_pyscf_driver_meta_contract.py`、`tests/test_tier2_optional_integrations_frontier.py`（PBC/ddCOSMO 相关断言） |
| `composable_computable` | 与闭源 Computable 融合顺序 | rich_optional（workflow-preview） | Y1-Q4 | 见 MAINTAINERS | |
| `integrations_closure_layer` | 产品默认闭包 | reference_v1 | 长期 | 见 MAINTAINERS | 仅 L1 |
| `dmet_scf_loop` | 化学意义上完整 DMET bath / 闭源 bath 拟合 | partial + 文档钩子 | Y2-Q1 | 见 MAINTAINERS | 用户钩子 + Schmidt 生产路径 |
| `qermit_graph`（ZNE×Qiskit） | `circuit_scale_fold` 与 `run_qiskit_shots_pauli_protocol` 合一 | partial + **`zne_qiskit_unification_v1`** 机读块 | Y1-Q4 | 见 MAINTAINERS | 见 `mitigation_PMSV_ZNE_Qermit_mapping.md` |
| `AlgorithmBayesianQPE` / Phayes | 非 Phayes 产品深度 | partial + stub 键 | 长期 | 见 MAINTAINERS | 公开站 diff 复核 |
| **矩阵 §2 `AlgorithmAdaptVQE`** | pool / 日程与 Vendor platform/Tangelo 公开「化学激发池」非逐条对齐 | partial + 文档对照节（parity §2 下「ADAPT 与公开 pool」） | Y2-Q1 | 见 MAINTAINERS | `tutorial_chain_h2.yaml`；`adapt.py` |
| **矩阵 §2 `AlgorithmIQEB`** | IQEB 可选路径；内层 VQE 深度 | partial + 既有 export 键 | Y1-Q4 | 见 MAINTAINERS | `example_h2_iqeb.yaml` |
| **矩阵 §2 `AlgorithmVQD`** | 三通道报告 vs 闭源多目标叙事 | partial + `l1_excited` CI | Y1-Q4 | 见 MAINTAINERS | PySCF；`test_qse_sceom_vqd_extended.py` |
| **矩阵 §2 `AlgorithmQSE` / `AlgorithmSCEOM`** | shot 语义与矩阵元噪声 | partial + `l1_excited` CI | Y1-Q4 | 见 MAINTAINERS | PySCF |
| **矩阵 §2 `Algorithm*QPE`** | 演示轨 + Methods 合一（浅层） | partial；**深度资源估计** → [P2_详细实施计划.md](P2_详细实施计划.md) P2-W1 | Y2-Q1 | 见 MAINTAINERS | `example_h2_qpe_track.yaml`、`example_h2_qpe_track_parity_integrations.yaml`（pytket） |
| **`http_submit_poll_workspace`** | 本地 FastAPI 类比 vs Nexus UX | partial + caveat 固定 | Y1-Q4 | 见 MAINTAINERS | `test_api_runs.py` |
| **`compiler_pass_bundle`** | 默认 `CompilerSpec`+CircuitIR；**非**默认全链 TKET | partial + 矩阵 §4「默认 / 可选 pytket」叙事 | Y1-Q4 | 见 MAINTAINERS | 可选 `pytket`；`test_pytket_bridge.py` |
| **`computables_rich` 入 repro** | `parity_integrations.include_computables_rich_in_repro` | partial；golden 可选 | Y2-Q1 | 见 MAINTAINERS | `test_workflow_preview_repro_alignment.py` |
| **矩阵 §3 分解插件** | `embedding.mode: plugin` 玩具 demo 与教程互链 | partial + 文档索引 | Y1-Q4 | 见 MAINTAINERS | `example_decomposition_plugin_toy.yaml`；[case-study-h2-family](../docusaurus-site/docs/tutorial/case-study-h2-family.md) |
| **`ninety_day_checklist`** | D1–D90 台账 vs Cursor 计划 | **模板已填满**；缓冲周见 [`P2_buffer_week_playbook.md`](P2_buffer_week_playbook.md) | Y2-Q1 | 见 MAINTAINERS | [`P2_ninety_day_execution_checklist.md`](P2_ninety_day_execution_checklist.md)；`tests/test_api_runs.py`、`scripts/check_parity_export_sample.py`（取代已移除的 parity matrix anchor 专属用例） |

**签off 规则**

- **云/硬件**：不进入本表（刻意不对齐）。
- **闭源不可检证**：允许长期 `partial`，但须每季度复核公开文档是否新增可检证项。

**年度结束时**：未达标行 → 复制至下年路线图或降级为文档级 `n/a` 并说明原因。

**实施索引**（P1 全量核对后）：队列来源见 [P1_completion_audit.md](P1_completion_audit.md) §5。
