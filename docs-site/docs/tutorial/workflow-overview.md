---
title: 工作流与 YAML 概览
description: 从配置文件理解一条量子化学编排任务；与四柱指南的衔接
---

本页在 [15 分钟上手](/tutorial/quickstart) 能跑通的基础上，说明**一条任务在 YAML 里如何组织**，方便你改示例、写自己的 `experiment`。

一页总览图（Mermaid）见 [产品功能](/product/features) 中的「一页图」。

## 一条管线的逻辑顺序

典型顺序与四柱对应关系（概念上）：

1. **分子与经典化学**（驱动、电荷、基组等）→ 对应 [P1 化学与嵌入](/guide/chemistry-and-embedding/)  
2. **量子子问题**（活性空间、映射、算法名）→ P1 与 [P2 算法与协议](/guide/algorithms-and-protocols/) 交界  
3. **协议与阶段**（变分步、Pauli 协议、激发等）→ P2  
4. **后端与采样**（statevector / Qiskit / shots 等）→ [P3 执行与分析](/guide/execution-and-analysis/)  
5. **作业、API、repro**（若启用异步或 HTTP）→ [P4 作业与可复现](/guide/jobs-and-reproducibility/)  

不必一次读完所有 YAML 键；先跑通 `configs/example_h2.yaml`，再按上表打开指南里与你相关的章节。

## YAML 里你最先会改的几类块

| 块（概念名） | 作用 |
|--------------|------|
| 分子 / 周期元数据 | 定义体系与电荷等 |
| 经典计算 / 驱动 | PySCF 等驱动与 SCF 选项 |
| 量子 / 活性空间 | 活性轨道与电子数、映射方式 |
| 量子 / 算法 | VQE、ADAPT、激发等开关与超参 |
| 后端 | `statevector`、`qiskit` 等与 shots 相关项 |
| 作业 / API（可选） | 与 SQLite、HTTP 示例相关配置 |

具体键名与默认值以仓库 `configs/*.yaml` 与源码中的配置模型为准；指南各柱会按主题展开。

## 与「产品功能」页的关系

- [产品功能](/product/features)：按**层次**说明能做什么、接口在哪。  
- 本页：按**时间顺序 / 配置结构**帮你把 YAML 与四柱对齐。  
- 命令与脚本：[命令行与脚本](/reference/cli-and-scripts)。  

## 下一步

- 深入某柱：从 [指南总览](/guide/) 进入 P1–P4。  
- UCCSD Trotter 配置与 export：[UCCSD Trotter 与 export](/tutorial/uccsd-trotter-export)。  
- ZNE×Qiskit 机读键：[ZNE × Qiskit repro](/tutorial/zne-qiskit-repro)。  
- Projection 轨迹与 Mulliken 哈密顿量：[Projection 嵌入深入](/tutorial/projection-embedding-deep-dive)。  
- 原理与扩展阅读：[原理与阅读建议](/guide/principles-and-reading)。  
