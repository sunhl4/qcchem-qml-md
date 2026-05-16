# P2 执行对齐笔记（Vendor platform 公开面 × Tangelo 借鉴）

**用途**：记录「90 日计划」类迭代的 **文档—代码 drift** 与 **Tangelo 可借用边界**，避免口头对齐。权威 parity 仍以 [public_parity_matrix.md](public_parity_matrix.md) 与 **`product_gap_categories()`**（HTTP/export 字段 `gaps` / `capability_gap_categories`）为准。**逐日核对表**：[`P2_ninety_day_execution_checklist.md`](P2_ninety_day_execution_checklist.md)。

## 1. Vendor platform How-to 映射 drift（滚动）

| 日期 | 观察 | 动作 |
|------|------|------|
| 2026-05-12 | 公开站三支柱（spec / program / execution）不变 | 母稿继续用 [Vendor platform_manual_howto_与_qchem_stack_映射.md](Vendor platform_manual_howto_与_qchem_stack_映射.md)；HTTP `workflow-preview` 对齐五阶段 |

*维护约定*：Quantinuum 文档改版 → 先更新矩阵 §5 / [L1_Vendor platform_alignment_signoff.md](L1_Vendor platform_alignment_signoff.md) 钉扎日期，再登记本表一行。

## 2. Tangelo：借用 vs 不借用

| 决策 | 理由 |
|------|------|
| **借用**：算法名词与多后端叙事对照表（见 [P2_W5_algorithm_registry_alignment.md](P2_W5_algorithm_registry_alignment.md) §5） | 开源可追溯，便于 Methods 对齐 |
| **借用**：`examples/tangelo_facade_demo.py` 将研究员指向 **封装 YAML** | Notebook 友好，但不绕过 Pydantic |
| **不借用**：以松散 dict 替换 `ExperimentConfig` | 违背本栈「可校验契约」定位 |
| **不借用**：闭源深度等价声称 | 与 [P2_详细实施计划.md](P2_详细实施计划.md) §2 非目标一致 |

## 3. Tangelo DMET / QMMM（边界 honesty · D34）

本仓库 **不** 宣称与 Tangelo problem-decomposition notebooks **数值同构**；开放栈提供 **DMET 形 orchestration、Schmidt 生产、插件分解玩具**，矩阵 §3 保持 **`partial`**。对照 YAML：`configs/example_h4_dmet_fragment_exact_small.yaml`、`configs/example_decomposition_plugin_toy.yaml`。

## 4. 竞品 release notes（滚动 · D58/D59）

**程序**：公开文档重大改版 → 更新 [L1_Vendor platform_alignment_signoff.md](L1_Vendor platform_alignment_signoff.md) 钉扎日期 → 登记本表一行；Tangelo 侧 algorithm/registry 变更 → 同步 [P2_W5_algorithm_registry_alignment.md](P2_W5_algorithm_registry_alignment.md) §1–§4。

| 日期 | 来源 | 动作 |
|------|------|------|
| 2026-05-12 | Quantinuum Vendor platform | 钉扎见 [L1_Vendor platform_alignment_signoff.md](L1_Vendor platform_alignment_signoff.md)；改版→矩阵 §5 diff |
| 2026-05-12 | Tangelo（GitHub releases） | [P2_W5_algorithm_registry_alignment.md](P2_W5_algorithm_registry_alignment.md) §4 随算法/registry 变更更新 |
