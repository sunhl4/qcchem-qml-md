# P1 · 化学与嵌入（Chemistry & embedding）

对应 InQuanto 文档中的 **Chemical Specification**：分子或周期体系建模、后 HF、嵌入与活性空间。

## 你将学到

- `qchem_stack.chem` 中驱动与哈密顿量构建的分工。  
- DMET / projection / Schmidt 在 YAML 与 `parity_snapshot` 中的占位与契约。  
- 与 InQuanto 全量 driver 名称表的 **名称映射**边界（非闭源行级对齐）。

## 相关文档

- [DMET · parity_snapshot](/reference/dmet-parity-snapshot)  
- [母仓库 `docs/`：活性空间、冻结轨道与 AVAS（完整长文）](../../../../docs/活性空间指定与AVAS_理论实践与开源对照.md)（相对链接自本站；亦可从磁盘打开仓库内 `docs/` 同名文件）
- [多后端统一输入输出适配合同](/guide/chemistry-and-embedding/backend-adapter-unified-io)
- [后端适配快速接入（模板 + 自检）](/guide/chemistry-and-embedding/backend-adapter-quickstart)
- [InQuanto-PySCF 叙事对照（量子问题 / AO / 对称性）](/guide/chemistry-and-embedding/inquanto-pyscf-problem-analog)
- [二次量子化读表：Fock 态与费米哈密顿量](/guide/chemistry-and-embedding/second-quantization-fock-hamiltonian-readout)
- [架构边界](/concept/architecture-boundaries) — 闭源能力闭合说明  
- [公开契约矩阵 §3](/parity/public-matrix) — Classical chemistry & embedding  

## 在 InQuanto 镜像中的对应位置

- [extensions / inquanto-pyscf](/mirror/extensions/inquanto_pyscf/) — 完整 PySCF driver / DMET / FMO 类列表
- [manual / embedding](/mirror/manual/embedding/) — DMET / 投影嵌入 / NEVPT2-AC0 概念页

<PillarMirror pillar="P1" locale="zh" />

## 下一步

[P2 算法与协议](/guide/algorithms-and-protocols/) · [15 分钟上手](/tutorial/quickstart)
