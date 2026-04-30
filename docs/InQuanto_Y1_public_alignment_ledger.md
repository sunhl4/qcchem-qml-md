# InQuanto 公开面 Y1 对标台账（非云、非硬件）

**作用**：执行「一年计划」时的**维护台账**（锚定日期、季度 OKR、度量、文档索引）。**不**替代 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 与 [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md)。

**终局口径（与年度计划一致）**

- **L1+**：除刻意 `n/a` 外，矩阵每行有 gap 锚点 / caveat / 证据链（模块 + 机读键 + 测试或脚本）；残余 `partial` 须有 SLA 或收束为 `yes`。
- **L3（可选）**：2–4 个固定基准 YAML，能量/方差在文档阈值内可复现（**非**闭源 wheel 等价）。
- **排除**：真 Nexus/`qnexus`/HQC/OAuth/配额；硬件校准、原生门集专优、拓扑；Qermit/cuTensorNet **商业二进制**等价。

---

## 1. 钉扎与月度 diff

| 字段 | 值 / 动作 |
|------|-----------|
| Quantinuum 公开站 | `https://docs.quantinuum.com/inquanto/` |
| 本次台账起始钉扎 | 2026-04-28（与 [L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md) 一致） |
| 月度 | 维护人记录当月公开站**是否改版**；若改版 → 更新矩阵/差距表 §5，不自动记为功能回归 |
| **W2 进度（激发态 `run_summary`）** | 已完成：`vqd_three_protocol_present`、`qse_shot_mode`、`qse_shot_noise_model`（条件）、`sceom_*` 写入 `repro.run_summary`；`out["qse"].meta` 含 `qse_shot_mode`；验收见 [工程记忆 §3.1](工程记忆_Quantinuum对标与数据流技术文档.md) 与 `tests/test_orchestration_pipeline.py` |
| **IQEB / projection L1** | `quantum.algorithm=iqeb` + `configs/example_h2_iqeb.yaml`；`embedding.mode=projection` + `configs/example_h2_projection_trace.yaml`；CI：`smoke_pipeline.py --iqeb` / `--projection-trace`；`PARITY_SNAPSHOT_DOCUMENTED_KEYS` 含 `iqeb_max_rounds`、`projection_embedding_open_trace` |
| **非云「超越」机读钉扎** | `GET /v1/meta/capability-surface` → **`open_stack_differentiators`**（`open_stack_differentiators_v1`）；矩阵 [§0](inquanto_public_parity_matrix.md) 与 [竞争定位 §3 卖点 6](竞争定位与路线图_对标Quantinuum产品与技术路线.md) |

---

## 2. 季度 OKR（滚动）

### Q1（月 1–3）：L1 + 算法 export + 嵌入叙事

| 周区间 | 核心交付 | 验收 |
|--------|----------|------|
| W1–W4 | 台账 + `gaps`/`object_map` 与 `GET /v1/meta/capability-surface` 同源；export 黄金样例 | `test_capability_surface_matches_inquanto_contract`；`scripts/check_parity_export_sample.py` |
| W5–W8 | Schmidt / DMET / projection：`run_summary`、export `--results`；矩阵 §3 | `tests/test_schmidt_embedding_production.py` 等 |
| W9–W12 | Protocol resource + computable 表面；矩阵 §1 Computable | workflow-preview API 单测；export 图字段 |

### Q2（月 4–6）：缓解 + TKET 编译路径

- PMSV/ZNE 机读与 [mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md) 对 errmit 小节。
- `qermit_analog` / `mitigation_dag_execution` 场景扩充（叙事 + JSON，非商业运行时）。
- `CompilerSpec` + TKET 技术文档与矩阵 `compiler_pass_bundle` 同步。

### Q3（月 7–9）：张量网 + 经典化学深度 + L3 套件

- TN：小体系交叉检与 `parity_snapshot` 键；见 [L3_benchmark_suite_roadmap.md](L3_benchmark_suite_roadmap.md)。
- 经典化学：driver/AVAS/CASSCF **形状**（接口 + 文档）；诚实 PySCF 边界。

### Q4（月 10–12）：QPE/容错叙事 + 残余清零 + 年度签off

- QPE 与 [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) P2；`qpe_qec_demo` 与主线 pipeline 配置；`run_summary`/export 全链。
- [Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md) 填满或升下年项。

---

## 3. 度量（每月末更新）

在下方复制一行并填写：

| 月份 | yes 行数（估算） | partial | n/a | 无 gap 解释的 partial（目标 0） | 备注 |
|------|------------------|---------|-----|----------------------------------|------|
| Y1-M01 | | | | | |

*说明：行数统计以 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) 主表为准，主观分类需与 `inquanto_gap_categories` 一致。*

---

## 3.5 节点级 backlog（295 manifest 节点）

**与矩阵的关系**：parity 矩阵按 **能力 / 模块行** 收敛；[`inquanto-node-backlog.generated.json`](inquanto-node-backlog.generated.json) 按 **InQuanto 公开 IA 节点（manifest 叶 + 类叶）** 展开，字段含附录 C 同构的 **验收项、平台维度、`differentiator_focus`**。二者通过 `qchem_module` 与 `parity_doc_hint` 弱关联。

**再生成**（仓库根 `qchem_qml_md/docs-site/`）：

```bash
npm run report:inquanto-backlog
npm run check:node-backlog
```

**按 wave 筛选（机读）**：用 `jq` 对 JSON 过滤，例如 **W0（云叙事 + meta）** — `differentiator_focus` 含 `cloud_tenant`：

```bash
jq '.nodes[] | select(.differentiator_focus | index("cloud_tenant")) | .breadcrumb | join("/")' docs/inquanto-node-backlog.generated.json
```

**W1（P2 shipped 非类叶）** 示例：

```bash
jq '.nodes[] | select(.pillar=="P2" and .status=="shipped" and .is_class_leaf==false) | .appendix_c_node_index' docs/inquanto-node-backlog.generated.json
```

**人读索引表**：[inquanto-node-backlog.generated.md](inquanto-node-backlog.generated.md)。**深度拆解**仍读架构报告 [appendix-C-deep-node-architecture.generated.md](architecture-report-quantinuum-inquanto-web/appendix-C-deep-node-architecture.generated.md)。

---

## 4. 每日节奏（全年）

周一：公开文档锚点 + 矩阵当周行；周二：repro/export 契约；周三：实现；周四：单测 + fixture；周五：文档双改 + `pytest` + `scripts/check_parity_export_sample.py`。

---

## 5. 相关路径

- **295 节点机读 backlog**：[`inquanto-node-backlog.generated.json`](inquanto-node-backlog.generated.json) · [Schema](inquanto-node-backlog.schema.json)
- **InQuanto B→J 逐项闭合计划（L1 序列表 + DoD）**：[InQuanto_B_J_逐项闭合计划.md](InQuanto_B_J_逐项闭合计划.md)
- **公开手册 How-to（功能参考）**：[InQuanto_manual_howto_与_qchem_stack_映射.md](InQuanto_manual_howto_与_qchem_stack_映射.md)（锚 [How to use InQuanto](https://docs.quantinuum.com/inquanto/manual/howto.html)）
- 架构边界：[架构_InQuanto闭源能力闭合与可复现边界.md](架构_InQuanto闭源能力闭合与可复现边界.md)
- 竞争策略：[竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md)
- 签字清单：[L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md)
