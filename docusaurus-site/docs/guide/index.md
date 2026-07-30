---
title: 手册总览
description: qchem-stack 工程手册入口：选型 P1–P4 与源码包模块双地图。
---

# 手册总览

两条导航并行使用：

| 路径 | 回答 | 入口 |
|------|------|------|
| **选型 · P1–P4** | 该用什么算法、映射、后端？ | 下文能力地图 |
| **模块手册** | 包如何调用、公式与参数？ | [模块手册](/modules/) |

动手操作见 [教程](/tutorial/)；可运行脚本见 [示例](/examples/)；字段契约见 [Python SDK](/reference/python-sdk)。

## 按角色

| 角色 | 建议首跳 |
|------|----------|
| 量子化学研究者 | [化学与嵌入](./chemistry-and-embedding) → [映射](./fermion-qubit-mappings) → [算法菜单](./algorithm-and-ansatz-menu) |
| 算法 / 协议开发 | [P2 程序构建](./program-construction) → [算符池](./operator-pools-adapt-iqeb) → [模块 · quantum](/modules/quantum/) |
| 平台 / 运维 | [P4 作业](./jobs-and-reproducibility) → [模块 · jobs](/modules/jobs) → [HTTP API](../reference/http-api-sqlite-jobs) |
| 新同学 | [开始使用](../getting-started) → [三条路径](./onboarding-three-paths) → [模块总览](/modules/) |

## 能力地图（选型 · P1–P4）

### P1 化学与嵌入

| 页面 | 覆盖 |
|------|------|
| [化学与嵌入](./chemistry-and-embedding) | 分子、SCF、活性空间、嵌入入口 |
| [双线路经典输入](./dual-classical-ingress) | geometry_file / precomputed |
| [费米子—量子比特映射](./fermion-qubit-mappings) | JW / BK / SCBK / JKMN / HCB |
| [AVAS → CASSCF](./avas-casscf-workflow) | 活性空间工作流 |
| [Psi4 后端](./psi4-backend) · [后端适配](./backend-adapter-quickstart) | 经典驱动扩展 |

### P2 算法与协议

| 页面 | 覆盖 |
|------|------|
| [P2 枢纽](./program-construction) | 决策树 |
| [算法与 ansatz 菜单](./algorithm-and-ansatz-menu) | `algorithm` / `ansatz` 注册表 |
| [算符池](./operator-pools-adapt-iqeb) | ADAPT / IQEB |
| [Pauli 协议](./pauli-protocol-and-shots) | 采样阶段 |
| [激发态侧车](./excited-states-vqd-qse-sceom) | VQD / QSE / SCEOM |
| [GQE](./gqe-generative-eigensolver) | 生成式本征求解 |

### P3 执行与分析

| 页面 | 覆盖 |
|------|------|
| [P3 枢纽](./execution-and-analysis) | 执行顺序 |
| [后端与 profile](./backends-and-profiles) | provider 注册表 |
| [误差缓解](./mitigation-zne-shadows) | ZNE / shadows |
| [MD/ML 闭环](./md-ml-active-learning) | QMEF 主动学习 |
| [资源估计](./resource-estimation-methods) | Methods 代理量 |

### P4 作业与可复现

| 页面 | 覆盖 |
|------|------|
| [P4 枢纽](./jobs-and-reproducibility) | 队列与 HTTP |
| [parity / repro 契约](./parity-repro-contract) | 验收与导出 |

## 源码包模块地图

| 模块 | 包 | 链接 |
|------|-----|------|
| config | `qchem_stack.config` | [模块页](/modules/config) |
| chem | `qchem_stack.chem` | [模块页](/modules/chem/) |
| quantum | `qchem_stack.quantum` | [模块页](/modules/quantum/) |
| backends | `qchem_stack.backends` | [模块页](/modules/backends) |
| protocols | `qchem_stack.protocols` | [模块页](/modules/protocols) |
| orchestration | `qchem_stack.orchestration` | [模块页](/modules/orchestration) |
| mitigation | `qchem_stack.mitigation` | [模块页](/modules/mitigation) |
| md_bridge | `qchem_stack.md_bridge` | [模块页](/modules/md-bridge) |
| jobs / repro / api | 平台面 | [jobs](/modules/jobs) · [repro](/modules/repro) · [api-sdk](/modules/api-sdk) |
| integrations / contracts / tensornet | 扩展面 | [integrations](/modules/integrations) · [contracts](/modules/contracts) · [tensornet](/modules/tensornet) |

完整索引：[模块手册总览](/modules/)。

## 推荐阅读顺序

1. [开始使用](../getting-started) / [15 分钟上手](../tutorial/quickstart)
2. 上表中与你任务相关的 **一条 P1→P2→P3** 链，或对应 **模块手册** 章
3. [parity 契约](./parity-repro-contract) + [Python SDK](../reference/python-sdk)
4. 需要时：[云与运维](../cloud/overview)
