---
title: 新用户三条路径
description: 从「能跑起来」「能对齐 InQuanto 公开契约」「MD/ML 长板」三选一或组合入门的推荐阅读顺序
---

本页是 **P2-W7** 双月交付的入口索引；操作细节仍以各教程页与仓库 YAML 为准。

## 路径 A：先跑通一条量子化学管线

适合：只想尽快看到能量 / `repro` 片段的贡献者与用户。

1. [15 分钟上手](/tutorial/quickstart)  
2. [工作流与 YAML 概览](/tutorial/workflow-overview)  
3. 任选一条加深：[UCCSD Trotter + export](/tutorial/uccsd-trotter-export) 或 [案例：H₂ 家族](/tutorial/case-study-h2-family)

## 路径 B：先理解 L1 / parity 契约再改代码

适合：要对齐 `inquanto_gap_categories`、export 或 CI 闸门的维护者。

1. [公开 parity 矩阵](/parity/public-matrix)  
2. [L1 签字清单](/parity/l1-signoff)  
3. [差距与实施计划](/parity/gap-implementation-plan) 与 [P2 详细计划](/concept/p2-detailed-plan) §6–§8  
4. 克隆仓库根目录 **`CONTRIBUTING.md`**（CI markers、`check_parity_export_sample`、可选 extras）

## 路径 C：MD / ML 与 `QMEFDataset`

适合：势函数 / 数据集 / 与 `repro` 弱耦合的长板。

1. [原理与阅读建议](/guide/principles-and-reading) 中与执行、缓解相关的节（按需）  
2. 源码 `src/qchem_stack/md_bridge/` 与母稿 **`docs/工程记忆_Quantinuum对标与数据流技术文档.md` §16**（`QMEFDataset` / `repro` 冻结字段）  
3. 运行 `pytest -m l1_md_ml`（见根目录 `CONTRIBUTING.md`）

---

**维护**：双月周历见仓库 `docs/与InQuanto能力差距与实施计划.md`（附录 A） §8；更新本页时同步根目录 `CONTRIBUTING.md` 中的「新用户三条路径」链接。
