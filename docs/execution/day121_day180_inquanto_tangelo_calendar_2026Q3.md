# Day121–Day180 执行日历：InQuanto / Tangelo 再对照与收口（2026Q3）

角色：在 [`day91_day120_daily_breakdown_2026Q3.md`](day91_day120_daily_breakdown_2026Q3.md)（P2 深化周节奏）之外，增加一条 **60 天连续**的「公开契约矩阵 × Tangelo 教程语义 × 机读 HTTP/export」对照链，避免叙事与 `inquanto_contract` / `capability_surface` 漂移。

## 起算与边界

- **建议起算**：**Day121 = Day120 月度封板次日**（负责人在 [`day121_kickoff_inquanto_tangelo_reconciliation_2026Q3.md`](day121_kickoff_inquanto_tangelo_reconciliation_2026Q3.md) 填入 ISO `PLAN_START_DATE`）。
- **真源三连**：[`docs/inquanto_public_parity_matrix.md`](../inquanto_public_parity_matrix.md)、[`docs/算法面广度_InQuanto_Tangelo对照索引.md`](../算法面广度_InQuanto_Tangelo对照索引.md)、`GET /v1/meta/capability-surface`（[`src/qchem_stack/api/app.py`](../../src/qchem_stack/api/app.py) `capability_surface`）。
- **L1/L0**：只做 **L1** 可检证对齐与诚实 `partial`；**不**宣称闭源 L0、云 IAM、Qermit/cuTensorNet 商业等价。

## 周闸门（每周五或该周最后工作日）

1. `pytest`（当周相关子集）+ `python scripts/check_parity_export_sample.py`
2. `ruff check` + `ruff format --check`（若当周改 Python）
3. 对照：`inquanto_gap_categories()`、`tangelo_public_mapping_alias_surface_v1()`、矩阵对应章节 — **无「文档有、机读无」静默漂移**

## 逐日日历（Day121–Day180）

| Day | 主题 | InQuanto / Tangelo 锚点 | 主要输入 | 当日最小产出 | 验收要点 |
|-----|------|-------------------------|----------|--------------|----------|
| 121 | Kickoff：对照范围冻结 | 矩阵 §0；广度索引 §5 | 矩阵、索引、gap JSON | [`day121_kickoff_…`](day121_kickoff_inquanto_tangelo_reconciliation_2026Q3.md) 填 `PLAN_START_DATE` + 范围表 | 目标与排除项书面化 |
| 122 | 协议五阶段证据链 | 矩阵 §1 五阶段行 | `workflow-preview`、pipeline | 执行页：代码路径 ↔ 矩阵句 | 每条 claim 有路径 |
| 123 | 采样 / Qiskit Pauli 路径 | §1 `run_sampled` / shots | 技术文档、tests | 边界说明更新或执行记录 | caveat 与测试一致 |
| 124 | Runs API / Nexus 类比 | §1 作业网关行 | `app.py`、`launch_retrieve_nexus_analog` | 对照表一行（文档或执行页） | 不夸大 Nexus 等价 |
| 125 | Computable 预览 | §1 Computable 行 | `computables-preview`、export | gap id / 状态复核 | 与 `composable_computable` 一致 |
| 126 | `parity-gaps` vs 矩阵 | §0 同源声明 | `parity_gaps`、`inquanto_gap_categories` | 抽样 diff 记录 | 分类字段齐全 |
| 127 | **Week1 闸门** | — | 全集 | 周小结：完成/遗留 | 遗留进 Day128 |
| 128 | 算法注册表地图 | §2 + [`algorithms` API](https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html) | `algorithm_registry_export_v1` | 映射表（类/模块） | 无未注册对外名 |
| 129 | VQE / UCCSD 行 | §2 | `vqe.py`、`uccsd_vqe.py` | 证据指针更新 | 与 export 一致 |
| 130 | ADAPT + 池 | §2 + 广度 §2–3 | `adapt.py`、`operator_pool_registry` | _pool id ↔ 矩阵一句 | 别名在 export |
| 131 | IQEB + 别名 | 同上 | `iqeb.py`、YAML 示例 | 同上 | `pool_id_aliases` 覆盖 |
| 132 | 激发态 VQD/QSE/SCEOM | §2 excited | `excited.py`、tests | 一行对照：契约键 | `excited_*_bundle_v1` |
| 133 | QPE / VQS 侧车 | §2 / 广度 §3 | `qpe`、`vqs`、demo YAML | `partial` 口径复核 | 非主编排写明 |
| 134 | **Week2 闸门** | — | — | 周小结 | — |
| 135 | Tangelo 映射表走读 | `tangelo_public_mapping_alias_surface_v1` | `fermion_mapping_registry.py` | 执行页：JW/BK/SCBK | 与白名单一致 |
| 136 | 费米子映射测试 | Tangelo 配方 / OpenFermion | `test_fermion_qubit_mapping.py` | 缺口清单或新用例草案 | pytest 定位清晰 |
| 137 | BK/SCBK UCCSD 边界 | 广度 §3；技术文档 UCCSD | `技术文档_UCCSD_JW与BK_SCBK电路边界.md` | 复核结论 | `partial` 不升格 |
| 138 | JKMN/HCB 披露 | 广度 §3；capability | mapping surface JSON | 披露句与代码一致 | 无静默「可跑」暗示 |
| 139 | `capability_surface` 键全集 | §0 机读汇总 | `test_capability_surface_*` | 回归运行记录 | 键集合锁定 |
| 140 | HTTP / OpenAPI 漂移扫描 | §1 HTTP 叙事 | `app.py`、OpenAPI（若有） | 差异列表 | 以代码为准归档 |
| 141 | **Week3 闸门** | — | — | 周小结 | — |
| 142 | `operator_pool_registry_export_v1` | 广度 §2 | export、parity | 字段抽样对照 | schema 稳定 |
| 143 | L3 代表 YAML | `L3_PYTEST_YAMLS` | `test_l3_benchmark_smoke.py` | 与矩阵「算法 partial」对齐说明 | 可选门禁文档化 |
| 144 | parity export 金样路径 | `PARITY_EXPORT_V2_STABLE_KEYS` | golden fixture、脚本 | 变更流程一句话进 CONTRIBUTING | 新人可跟 |
| 145 | `methods_resource_unified` | Methods 导出 | `test_methods_resource_unified_export.py` | 键或注释对齐矩阵 | 无不一致 |
| 146 | `check_parity_export_sample` 覆盖 | 抽样 configs | 脚本内列表 | 新增行需对应 gap/矩阵 | 脚本与文档互链 |
| 147 | `variational_registry_export_v1` | 变分插件 | `variational_plugins/registry.py` | 对照 breadth 索引表 | 文档有模块指针 |
| 148 | **Week4 闸门** | — | — | 周小结 | — |
| 149 | `inquanto_gap_categories`  schema | 差距计划附录 | `inquanto_contract.py` | 字段级快照或测试锚点 | 重命名可发现 |
| 150 | 矩阵 §3 化学行抽样 | PySCF / driver | `parity_matrix`、`drivers` | 3–5 行「证据路径」 | partial 有锚点 |
| 151 | 矩阵 §4（若有）/ 嵌入 | DMET/Schmidt | `dmet.py`、`schmidt_production` | 对照执行记录 | 与 gap 一致 |
| 152 | 孤儿 gap id 扫描 | 矩阵表格 | grep `gap`、JSON | 列表：文档有而代码无 | 清零或登记 |
| 153 | `parity_snapshot` 注册键 | `PARITY_SNAPSHOT_DOCUMENTED_KEYS` | contract | 与矩阵「导出」行交叉 | 白名单完整 |
| 154 | docs-site / docs 双站 | 关键入口 | VitePress、docusaurus | 互链断链修复清单 | 用户路径不断 |
| 155 | **Week5 闸门** | — | — | 周小结 | — |
| 156 | `computable_graph_v2` | workflow-preview | `inquanto_workflow_preview.py` | 边编辑语义复核 | YAML 与图一致 |
| 157 | `computables_rich` 可选 | §1 | repro 对齐测试 | 执行记录 | 与 gap 状态一致 |
| 158 | `GET …/summary` slim | 产品类比 | `slim_product_summary` | UX 字段 vs 矩阵 | partial 标明 |
| 159 | Mitigation 机读块 | §1 Qermit 行 | `mitigation_execution_model_public` | DAG/迹与文档一句 | 顺序不变量 |
| 160 | Qermit 映射文档 | `mitigation_PMSV_ZNE_Qermit_mapping.md` | tests | 更新或「无变更」记录 | 与 capability 同源 |
| 161 | `test_api_runs.py` 覆盖面 | HTTP 契约 | FastAPI tests | 新增路由需登记矩阵 | smoke 通过 |
| 162 | **Week6 闸门** | — | — | 周小结 | — |
| 163 | AVAS/CASSCF `partial` | P2 W3 | driver、矩阵行 | 边界段落复核 | 无 L0 措辞 |
| 164 | 经典接口统一叙事 | `ChemIntegralSolver` | 统一接口 md | 与矩阵化学行一致 | 追溯 bridges |
| 165 | 分解 / plugin 契约 | Phase B | `decomposition_plugin` | Tangelo「分解」叙事对齐 | export 可检证 |
| 166 | cuTensorNet / tensornet stub | 矩阵 §1 | stub modules | 诚实 n/a 复核 | 无误导 |
| 167 | MD/ML 行 | 矩阵、QMEF | `md_bridge` tests | 长板一句有据 | optional markers |
| 168 | 竞争定位 § 卖点 | `竞争定位与路线图_…` | 矩阵 §0 | 三条叙事 ↔ 机读键 | 不自相矛盾 |
| 169 | **Week7 闸门** | — | — | 周小结 | — |
| 170 | 三路径 onboarding | docs-site | `onboarding-three-paths` | 缺口列表 | 新用户可导航 |
| 171 | examples 索引 | `examples/` | README | 与矩阵 demo 行互链 | 路径可运行或标明 |
| 172 | EN 参考 stub 完整性 | `docs-site/docs/en` | http-api、parity EN | 关键 stub 有指针 | 不全空白 |
| 173 | ENGINEERING §9 HTTP | 中英 | `ENGINEERING_ARCHITECTURE` | 与 `app.py` 一致 | 已对齐则记录「跳过」 |
| 174 | L3 报告脚本文档 | `l3_algorithm_benchmark_report.py` | 广度 §4 | 使用示例一行 | 与 CI optional 一致 |
| 175 | 矩阵 §0 季度刷新 | 公开矩阵 | 全文 diff 意图 | 变更摘要 | 版本感 |
| 176 | **Week8 闸门 + 预总闸** | — | — | 问题清单 | 进 Day177 |
| 177 | 总闸：pytest 全量预检 | — | CI 等价 | 失败分类 | 阻塞登记 |
| 178 | 总闸：修复批次 A | — | — | PR/提交记录 | 红转绿或 skip |
| 179 | 总闸：parity + ruff | — | scripts | 全绿记录 | 可附 CI |
| 180 | **Day180 封板** | 矩阵+索引+本日历 | 执行页汇总 | [`day180_signoff_inquanto_tangelo_2026Q3.md`](day180_signoff_inquanto_tangelo_2026Q3.md)（创建并勾选） | 下一周期入口 |

## 封板产物（Day180）

- 更新后的 [`docs/inquanto_public_parity_matrix.md`](../inquanto_public_parity_matrix.md)「执行状态」行（指向本日历与 Day180 签字页）。
- [`docs/算法面广度_InQuanto_Tangelo对照索引.md`](../算法面广度_InQuanto_Tangelo对照索引.md) §5 若有收口声明变更则同步。
- `docs/execution/README.md` 收录 Day121–Day180 关键日志链接。

## 非目标（保持）

- 不实现 JKMN/HCB **可执行**映射（独立项目）。
- 不修改 `parity_export_schema_version` / `PARITY_EXPORT_V2_STABLE_KEYS` 除非走单独 ADR 与金样再生。
