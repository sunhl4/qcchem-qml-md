# P1 · 化学与嵌入（Chemistry & embedding）

对应 InQuanto 文档中的 **Chemical Specification**：分子或周期体系建模、后 HF、嵌入与活性空间。

## 你将学到

- `qchem_stack.chem` 中驱动与哈密顿量构建的分工。  
- DMET / projection / Schmidt 在 YAML 与 `parity_snapshot` 中的占位与契约。  
- 与 InQuanto 全量 driver 名称表的 **名称映射**边界（非闭源行级对齐）。

## 相关文档

- [DMET · parity_snapshot](/reference/dmet-parity-snapshot)  
- [架构边界](/concept/architecture-boundaries) — 闭源能力闭合说明  
- [公开契约矩阵 §3](/parity/public-matrix) — Classical chemistry & embedding  

## 在 InQuanto 镜像中的对应位置

- [extensions / inquanto-pyscf](/mirror/extensions/inquanto_pyscf/) — 完整 PySCF driver / DMET / FMO 类列表
- [manual / embedding](/mirror/manual/embedding/) — DMET / 投影嵌入 / NEVPT2-AC0 概念页

<PillarMirror pillar="P1" locale="zh" />

## 下一步

[P2 算法与协议](/guide/algorithms-and-protocols/) · [15 分钟上手](/tutorial/quickstart)
