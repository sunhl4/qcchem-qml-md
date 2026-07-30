---
title: 四柱一览
description: P1–P4 与全部指南子页地图；详细能力见手册总览。
---

# 四柱一览

完整能力地图与模块双导航见 **[手册总览](/guide/)**。本页是**全部指南页地图**：按柱跳转，并链到教程与模块深读。

:::tip 模块手册
选型在本区；公式 / API → [模块手册总览](/modules/) · [按任务阅读](/modules/reading-paths)
:::

## 四柱入口

| 柱 | 入口 | 回答的问题 |
|----|------|------------|
| P1 化学与嵌入 | [化学与嵌入](./chemistry-and-embedding) | 分子、SCF、映射、嵌入怎么选？ |
| P2 算法与协议 | [程序构建](./program-construction) | 算法、ansatz、池、协议怎么选？ |
| P3 执行与分析 | [执行与分析](./execution-and-analysis) | 后端、缓解、MD/ML 怎么跑？ |
| P4 作业与可复现 | [作业与可复现](./jobs-and-reproducibility) | 作业、HTTP、repro 怎么验收？ |

新同学：[三条上手路径](./onboarding-three-paths) · [按角色导航](./role-based-paths) · [按任务阅读（模块）](/modules/reading-paths)。

## P1 子页地图

| 页面 | 覆盖 |
|------|------|
| [化学与嵌入](./chemistry-and-embedding) | 决策总表、嵌入边界、代表 YAML |
| [双线路经典输入](./dual-classical-ingress) | geometry_file / precomputed |
| [费米子—量子比特映射](./fermion-qubit-mappings) | JW / BK / SCBK / JKMN / HCB |
| [AVAS → CASSCF](./avas-casscf-workflow) | 活性空间工作流 |
| [Psi4 后端](./psi4-backend) | ChemIntegralSolver Psi4 |
| [后端适配快速接入](./backend-adapter-quickstart) | 自定义经典 solver 插件 |

模块对照：[chem](/modules/chem/) · [dual-ingress](/modules/chem/dual-ingress) · [mappings](/modules/chem/mappings) · [embedding](/modules/chem/embedding)。

## P2 子页地图

| 页面 | 覆盖 |
|------|------|
| [程序构建](./program-construction) | 决策树与柱内索引 |
| [算法与 ansatz 短菜单](./algorithm-and-ansatz-menu) | 短决策矩阵；权威在算法深读 |
| [算符池 ADAPT / IQEB](./operator-pools-adapt-iqeb) | 池 ID 与别名 |
| [Pauli 协议与采样](./pauli-protocol-and-shots) | shots / CircuitIR |
| [激发态 VQD / QSE / SCEOM](./excited-states-vqd-qse-sceom) | 激发态侧车 |
| [GQE](./gqe-generative-eigensolver) | 生成式本征求解 |

模块对照：[算法深读索引](/modules/quantum/algorithms/)。

## P3 子页地图

| 页面 | 覆盖 |
|------|------|
| [执行与分析](./execution-and-analysis) | 执行顺序与解释清单 |
| [后端与 profile](./backends-and-profiles) | provider 注册表 |
| [误差缓解](./mitigation-zne-shadows) | ZNE / shadows |
| [MD/ML 闭环](./md-ml-active-learning) | QMEF 主动学习 |
| [资源估计](./resource-estimation-methods) | Methods 代理量 |

模块对照：[backends](/modules/backends) · [mitigation](/modules/mitigation) · [md-bridge](/modules/md-bridge)。

## P4 子页地图

| 页面 | 覆盖 |
|------|------|
| [作业与可复现](./jobs-and-reproducibility) | 队列、HTTP、SDK |
| [parity / repro 契约](./parity-repro-contract) | 验收与导出键 |

模块对照：[jobs](/modules/jobs) · [repro](/modules/repro) · [api-sdk](/modules/api-sdk)。

## 导航与原理页

| 页面 | 用途 |
|------|------|
| [手册总览](./) | 选型 + 模块双地图 |
| [三条上手路径](./onboarding-three-paths) | 新用户入口 |
| [按角色导航](./role-based-paths) | 研究者 / 平台 / 维护者 |
| [原理与阅读](./principles-and-reading) | 深读顺序 |
| [工程架构](../concept/engineering-architecture) | 管线阶段图 |

## 教程交叉入口

| 主题 | 教程 |
|------|------|
| 最小跑通 | [quickstart](../tutorial/quickstart) |
| ADAPT 池 | [adapt-pool-smoke](../tutorial/adapt-pool-smoke) |
| QPE track | [qpe-track](../tutorial/qpe-track) |
| DMET 自洽 | [dmet-self-consistent](../tutorial/dmet-self-consistent) |
| GQE 变体 | [gqe-variants](../tutorial/gqe-variants) |
| ONIOM | [oniom-smoke](../tutorial/oniom-smoke) |
| 示例馆 | [examples](../examples/) |

## 推荐一条最短链

1. [onboarding-three-paths](./onboarding-three-paths)（选路径 A）
2. [chemistry-and-embedding](./chemistry-and-embedding) → [program-construction](./program-construction)
3. [execution-and-analysis](./execution-and-analysis)（仅 statevector）
4. 需要服务化时再进 [jobs-and-reproducibility](./jobs-and-reproducibility)

## 与示例馆 / 教程的边界

| 区 | 职责 |
|----|------|
| 本指南区 | **选型**：该用什么、何时不要用 |
| [教程](../tutorial/) | **逐步做**：验证命令与期望输出 |
| [示例馆](../examples/) | **可运行入口清单**（含 gallery-body） |
| [模块手册](/modules/) | **公式 / API / 参数** |

验证本页链接可达的最小检查：

```bash
python3 -c "from qchem_stack.config import load_experiment_config; print(load_experiment_config('configs/example_h2.yaml').experiment_id)"
```

期望：打印非空 `experiment_id`。
