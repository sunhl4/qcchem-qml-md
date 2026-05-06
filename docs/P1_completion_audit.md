# P1 全量核对报告（先审计、后排期实现）

**钉扎日期**：2026-05-07（审计生成时仓库状态）。**范围**：竞争定位 §6「P1 开源工作流超越」四行 + 差距文档 §3「P1 中程」三条 + [L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md) 主表与 H1/I1 + 与 P1 叙事强相关的 parity 主表（§1–§3）及 [InQuanto_B_J_逐项闭合计划.md](InQuanto_B_J_逐项闭合计划.md) 交叉引用。**不含**：路线图 P2/P3 实现（见 [P2_详细实施计划.md](P2_详细实施计划.md)）、真 Nexus/H 系、L0 闭源等价。

---

## §0 方法与状态枚举

| 状态 | 含义 |
|------|------|
| **done** | 竞争定位 / L1 / 差距文档所述验收口径在开放栈内已满足，且有 **pytest 或脚本或 YAML** 可复跑。 |
| **partial+caveat** | 能力存在且机读键齐全，但与 InQuanto 公开产品形态或深度**非 1:1**；矩阵与 gap 已写 caveat 或 `n/a`。 |
| **n/a** | 刻意不对齐或非公开可检证范围（云、专有硬件、商业二进制等）。 |
| **doc_only_gap** | 叙事/矩阵已闭合，但缺少**专用**单测或 export 黄金样例；建议补测而非改算法。 |

**证据写法**：每条给出 `src/...` 或 `configs/...` 或 `tests/...` 或 `scripts/...` 的仓库相对路径。无单测则标 **证据缺口**。

---

## §1 竞争定位 §6「P1 开源工作流超越」四行对照

| # | 竞争目标 | 工程动作摘要 | 主要证据 | 验收口径是否满足 | 缺口 | 建议 |
|---|----------|--------------|----------|------------------|------|------|
| P1-1 | 吸收 InQuanto 的对象模型纪律 | workflow/computable graph；YAML 与 API 共用；`workflow-preview` 与 `repro` 对齐 | [`src/qchem_stack/protocols/computable.py`](../src/qchem_stack/protocols/computable.py)；[`integrations/inquanto_workflow_preview.py`](../src/qchem_stack/integrations/inquanto_workflow_preview.py)；[`api/app.py`](../src/qchem_stack/api/app.py)；[`tests/test_workflow_preview_repro_alignment.py`](../tests/test_workflow_preview_repro_alignment.py) | **partial+caveat**：薄层 DAG + preview 已对齐；非闭源 `Computable` 产品类 | 与差距表「无独立 Computable 产品类」一致 | **保持 P1 签字**；深度对象模型 → **P2** 或长期 SLA |
| P1-2 | 吸收 Tangelo 多算法与多后端广度 | ansatz/solver/mapping registry；JW/BK/SCBK；conformance | [`chem/hamiltonian.py`](../src/qchem_stack/chem/hamiltonian.py)、[`quantum/algorithm_registry.py`](../src/qchem_stack/quantum/algorithm_registry.py)、[`chem/fermion_mapping_registry.py`](../src/qchem_stack/chem/fermion_mapping_registry.py)；[`tests/test_backend_conformance.py`](../tests/test_backend_conformance.py)；样例 [`configs/example_h2_uccsd.yaml`](../configs/example_h2_uccsd.yaml)、[`configs/example_h2_uccsd_trotter.yaml`](../configs/example_h2_uccsd_trotter.yaml) | **partial+caveat**：三映射 + 多 provider schema 稳定；BK/SCBK 上 UCCSD Trotter 矩阵 **n/a** | 化学池广度、BK Trotter | **P1 已可发表**；池扩展 → **P2-W5** |
| P1-3 | embedding-first 主线 | DMETContext、projection、fragment；`repro` 全量 | [`chem/embedding/`](../src/qchem_stack/chem/embedding/)；[`orchestration/pipeline.py`](../src/qchem_stack/orchestration/pipeline.py)；[技术文档_DMET与parity_snapshot开放契约.md](技术文档_DMET与parity_snapshot开放契约.md)；[`configs/example_h2_projection_trace.yaml`](../configs/example_h2_projection_trace.yaml)、[`configs/example_h4_dmet_fragment_exact_small.yaml`](../configs/example_h4_dmet_fragment_exact_small.yaml)、[`configs/example_oniom_toy.yaml`](../configs/example_oniom_toy.yaml)、侧车键见 L1 表 | **partial+caveat**：小体系 trace 与 Schmidt 生产已闭合；全文献 DMET bath 自洽未宣称 | 产品级 ONIOM/QM-MM | **P1 叙事闭合**；产品级分解 → **P2-W2** |
| P1-4 | mitigation 升为 workflow block | PMSV/ZNE/SPAM DAG；`qermit_analog` | [`mitigation/`](../src/qchem_stack/mitigation/)；[`tests/test_mitigation_dag_trace_homology.py`](../tests/test_mitigation_dag_trace_homology.py)；[`mitigation_PMSV_ZNE_Qermit_mapping.md`](mitigation_PMSV_ZNE_Qermit_mapping.md)；[`configs/example_h2_zne_circuit_fold.yaml`](../configs/example_h2_zne_circuit_fold.yaml) | **partial+caveat**：DAG 与 trace 同源；非商业 Qermit | 进阶 shadows 等 | **P1 闭合**；进阶块 → **P2-W4** |

---

## §2 差距文档 §3「P1 中程」三条映射

| 差距文档条目 | 实现要点 | 单测 / 脚本 |
|--------------|----------|-------------|
| **嵌入** `repro.embedding_config` = 全 `EmbeddingSpec` | `collect_repro_metadata` / `EmbeddingSpec` 序列化 | [`tests/test_repro_snapshot_qse_sceom.py`](../tests/test_repro_snapshot_qse_sceom.py) 内 `test_repro_includes_embedding_config_block`（差距文内点名） |
| **激发态报告** `excited_methods_unified` + export `excited_resource_from_config` | `orchestration` 内 `excited_resource_summary`；export v2 | `tests/test_orchestration_pipeline.py`；`export_parity_criteria_table` config-only 路径 |
| **PMSV** 合并 `protocol_counts['pmsv_report']` | `mitigation.pmsv.finalize_pmsv_report` | `tutorial_inquanto_chain_h2.yaml` + 管线测；`check_parity_export_sample` 含链式 YAML |

**结论**：三条均为 **done**（在「可发表 L1」语义下）；残余 **partial** 见差距总表 §1「激发态 / 经典化学」行（算法深度），属 H1 与矩阵 §2，不与此三条矛盾。

---

## §3 L1 签字表审计索引

**主表**（矩阵锚点 → 审计结论；与 §1 去重处写「见 §1」）。

| 矩阵锚点 | gap.id | 审计结论 | 备注 |
|----------|--------|----------|------|
| §1 五阶段 Protocol | （多项） | **partial+caveat** | `protocols/protocol.py`；异步非 Nexus：`tests/test_api_runs.py` |
| §1 qnexus / HQC | `cloud_nexus` | **n/a** 类比 | `jobs/nexus_analog` |
| §1 作业提交/轮询 | `http_submit_poll_workspace` | **partial+caveat** | `api/app.py` |
| §1 Qermit | `qermit_graph` | **partial+caveat** | 见 §1 P1-4 |
| §1 Computable | `composable_computable` | **partial+caveat** | 见 §1 P1-1 |
| §1 CuTensorNet | `tensornet` | **n/a** | stub + `parity_snapshot.tensornet_engine_resolved` |
| §2 Algorithms | `ucc_chem_ansatz` 等 | **partial+caveat** | 见 §1 P1-2 |
| §2 VQD / QSE / SCEOM | — | **partial+caveat** | `tests/test_qse_sceom_vqd_extended.py`、`pytest -m l1_excited` |
| §2 QPE / Bayesian | — / C14 | **partial+caveat** | `qpe_qec_demo`；`test_l1_phase_c_iqeb_bayesian.py` |
| §3 DMET / projection / driver | `dmet_scf_loop` 等 | **partial+caveat** | 见 §1 P1-3；driver：`tests/test_inquanto_driver_surface_l1.py` |
| §4 TKET | `compiler_pass_bundle` | **partial+caveat** | `tests/test_pytket_bridge.py`；[`example_h2_qpe_track_parity_integrations.yaml`](../configs/example_h2_qpe_track_parity_integrations.yaml) + `test_methods_resource_unified_qpe_plus_tket_probe_schema`（PySCF+pytket） |
| 设备比特串 | `qpu_shot_histogram` | **partial+caveat** | `tests/test_qiskit_pauli_shots.py` |
| 集成参考 / 评估支持 | `integrations_closure_layer` / `evaluate_support_set` | **done** / **improved** | `gap_closure_bundle.py`；`pauli_support` |

**H1**（激发态）：**partial+caveat** — CI 子集 `l1_excited`；残余入 [Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md)。  
**I1**（MD/ML）：**partial+caveat**（差异化长板）— `tests/test_md_bridge.py`、`pytest -m l1_md_ml`。

---

## §4 Parity 主表（§1–§3）P1 相关摘要与机读一致性

**脚本辅助计数**（主表 §1–§3 行，`scripts/count_parity_matrix_main_tables.py`）：`yes=3`，`partial=14`，`n/a=2`（与 [InQuanto_Y1_public_alignment_ledger.md](InQuanto_Y1_public_alignment_ledger.md) Y1-M04 手填一致时以 gap 语义为准）。

**与 `inquanto_gap_categories()` 一致性**（[`protocols/inquanto_contract.py`](../src/qchem_stack/protocols/inquanto_contract.py)）：

- 矩阵 §1 **Computable** 行 `partial` 与 gap `composable_computable` 的 `status: analog_v2_semantic_graph_rich_optional` **叙事一致**（非矛盾）。
- 矩阵 §2 **UCC/ADAPT** 与 gap `ucc_chem_ansatz` 的 `partial_jw_uccsd_and_trotter_packaged_bk_scbk_uccsd_na` **一致**（BK/SCBK Trotter **n/a** 已写明）。
- 矩阵 §1 **TN** `n/a` 与 gap `tensornet`（若单列）及 stub 实现 **一致**。
- **未发现**「矩阵写 `yes` 而 gap 写未实现」类硬矛盾；若公开站改版，按 [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md) §5 做 diff 登记。

**P1 范围内仍偏 `partial` 的矩阵主题**（摘录）：五阶段 Protocol 异步边界、Computable 产品深度、ADAPT/IQEB/QSE/SCEOM/VQD、QPE/Bayesian、DMET/projection/driver、编译 TKET 非默认全链、缓解非 Qermit。

---

## §5 建议实施队列（按「影响 × 成本」排序）

以下为 **P1 收尾或诚实升 P2** 的标题级队列，**不含**具体 PR 代码。

1. **填满 [Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md)**：为矩阵 §2 各 `partial` 算法行指定季度或升 P2-W3/W4。  
2. **激发态总回归门禁**（对齐 B→J **H1**）：文档化 `pytest -m l1_excited` 为必跑或 nightly 的哪一种；与 CI 对齐。  
3. **编译叙事默认链**（若仍标 partial）：在矩阵 §4 与 `compiler_pass_bundle` 备注中写清「可选 pytket」与默认 `CompilerSpec` 边界，避免读者误以为 TKET 默认全开。  
4. **ADAPT 与公开池差异**：单测或文档一节对照 Tangelo/InQuanto 公开描述的 pool 差异（低成本文档）。  
5. **`computables_rich` 入 repro**：仅在 `parity_integrations.include_computables_rich_in_repro: true` 时的 golden（L1 signoff 已提示）；补 export 样例可选。  
6. **driver 表面与 PySCF 版本**：`test_inquanto_driver_surface_l1` 与矩阵 §3 同步更新当 PySCF 次版本变化时。  
7. **QPE Methods 合一**：已新增 `example_h2_qpe_track_parity_integrations.yaml`；将 **P2-W1** 后续「资源估计深度」与 P1 边界写一句在竞争定位 §141（已由 P2 文档承接）。  
8. **MD/ML**：`l1_md_ml` 与 `QMEFDataset` 字段冻结清单（偏 P2-W6，若坚持算 P1 长板则先做文档）。  
9. **BayesianQPE / Phayes**：维持 `partial` + stub 单测；不冒充产品。  
10. **B→J 序 21（Computable 双向转换）**：若战略需要，从 `ComputableRef` 与 workflow-preview 的互转单测补起（中高成本，偏 P2）。  
11. **插件分解 demo**：`example_decomposition_plugin_toy.yaml` 在矩阵与教程索引中互链（低成本）。  
12. **parity export**：保持 `check_parity_export_sample.py` 与新增 config 同步（已部分覆盖）。

### §5 已落实项（维护指针，随能力变更修订）

| 队列项 | 落实位置 |
|--------|----------|
| 1 SLA 扩写 | [Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md)（算法 partial、HTTP、compiler、`computables_rich`、插件分解、MD/ML） |
| 2 激发态门禁与 CI | [CONTRIBUTING.md](../CONTRIBUTING.md)「CI markers」；`.github/workflows/ci.yml` |
| 3 编译默认链 | [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) §4「默认 vs 可选 pytket」；SLA 行 `compiler_pass_bundle` |
| 4 ADAPT 池 | 矩阵 §2 `AlgorithmAdaptVQE` 行；SLA 行 |
| 5 `computables_rich` | CONTRIBUTING + SLA 行；单测见 CONTRIBUTING 所列 |
| 6 driver / PySCF | [inquanto_driver_surface.py](../src/qchem_stack/chem/inquanto_driver_surface.py) 模块 docstring；SLA `drivers_cosmo_pbc` |
| 7 QPE §141 | [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) §141；矩阵 §2 QPE 行 |
| 8 MD/ML | CONTRIBUTING + SLA `l1_md_ml` |
| 9 Bayesian / Phayes | SLA 行（维持 partial + stub，无产品冒充） |
| 10 Computable 双向 | **未代码化**（仍为 P2）；见 [InQuanto_B_J_逐项闭合计划.md](InQuanto_B_J_逐项闭合计划.md) |
| 11 插件 demo | [case-study-h2-family.md](../docs-site/docs/tutorial/case-study-h2-family.md)；矩阵 §3 |
| 12 export 样例列表 | [CONTRIBUTING.md](../CONTRIBUTING.md)；`scripts/check_parity_export_sample.py` `SAMPLE_CONFIGS_REL` |

---

## 相关链接

- [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) §6  
- [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md) §1、§3  
- [L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md)  
- [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md)  
- [InQuanto_B_J_逐项闭合计划.md](InQuanto_B_J_逐项闭合计划.md)  

**维护**：本审计随「竞争定位 §6 已落地段」或 L1 表结构变更而修订；重大能力收束时更新 §5 队列。

---

## §6 P1 完成声明（核对口径）

在 **L1 非云非硬件对齐** 语义下（允许矩阵行保持诚实 **`partial`** / **`n/a`**，不要求闭源 L0）：

| 判据 | 状态 |
|------|------|
| 竞争定位 §6 四行 + 差距 §3 三条 | §1–§2 已标 **done** 或 **partial+caveat** 且证据路径齐全 |
| L1 signoff 主表 + H1/I1 | CI 与文档已对齐（见 §3、§5 已落实项） |
| §5 建议队列 1–9、11–12 | **已落实**（维护指针见 §5 表） |
| §5 项 10（Computable 双向 / B→J 序 21） | **未实现**：刻意保留为 **P2**（见 [P2_详细实施计划.md](P2_详细实施计划.md) §6 执行序表末行） |

**结论**：**P1 已闭合**；后续增量走 **P2 WBS** 与 [Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md) 季度行。

**下一动作**：按 [P2_详细实施计划.md](P2_详细实施计划.md) §6「建议执行顺序」实施；闸门仍用 **P2** 文档 §5 出口闸门与 §5 已落实的 CI + `check_parity_export_sample.py`（抽样列表含 B→J 附录表所列代表 YAML）。
