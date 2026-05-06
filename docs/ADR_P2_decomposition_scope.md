# ADR：P2-W2 分解与大体系 — 最小可跑 demo 范围钉扎

**状态**：已接受（文档 ADR，2026-05-07）。**母稿**：[P2_详细实施计划.md](P2_详细实施计划.md) §6 序 4、§8 第 1–2 周。

---

## 背景

P2 需在「不冒充 InQuanto 闭源分解产品」前提下，选一条 **最小可跑** 的分解 / 大体系增量（ONIOM、QM-MM、MI-FNO、预计算 fragment 等叙事并存）。

---

## 决策

1. **双轨保留，双月内只深做一轨**  
   - **轨 A — ONIOM / 层场玩具 → 可插拔层元数据**：继续以 `embedding.oniom_layers_v1` + `configs/example_oniom_toy.yaml` 为基线；P2 代码增量优先落在 **文档化插件边界**（`embedding.mode: plugin` + 已有 toy YAML），不宣称全文献 ONIOM 能量一致。  
   - **轨 B — 预计算 fragment / 用户 bath**：继续以 `schmidt_bath_sidecar_json_path` + DMET fragment exact 小体系为基线；全文献 DMET bath 自洽 **不** 在本 ADR 内承诺为 `yes`。

2. **本双月默认优先级**：**轨 A（插件 + 层元数据路径）** 先于轨 B 扩代码；轨 B 以 **gap `dmet_scf_loop` 文档 + 侧车** 收束，避免并行两套大改。

3. **非目标（重申）**：真 Nexus；闭源 ONIOM/QM-MM **数值** L0；无 `repro` 机读键的新「营销级」分解宣称。

---

## 后果

- 差距表与 [inquanto_public_parity_matrix.md](inquanto_public_parity_matrix.md) §3 **DMET / embedding** 行保持 **`partial`**，本 ADR 作为 caveat 引用。  
- 若产品方强制轨 B，需 **新开 ADR** 修订优先级并更新 [Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md) 对应行季度。

---

## 链接

- [与InQuanto能力差距与实施计划.md](与InQuanto能力差距与实施计划.md) §1 经典化学 / Ansatz。  
- [技术文档_DMET与parity_snapshot开放契约.md](技术文档_DMET与parity_snapshot开放契约.md)。
