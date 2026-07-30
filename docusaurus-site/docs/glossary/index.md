---
title: 术语表
description: PreQuantumInput、ExperimentConfig、ansatz、embedding、parity、QMEF 等核心术语短释义。
keywords:
  - glossary
  - PreQuantumInput
  - ExperimentConfig
  - QMEF
---

# 术语表

短定义 + 文档链接。更长论述见 [模块手册](/modules/) 与 [概念](/concept/docs-information-architecture)。

| 术语 | 定义 | 链接 |
|------|------|------|
| **PreQuantumInput** | 进入量子阶段前的统一输入：活性空间积分、费米子/量子比特哈密顿量与元数据。 | [哈密顿量](/modules/chem/hamiltonian) · 源码 `chem.pre_quantum_input` |
| **ExperimentConfig** | `schema_version: "2"` 的类型化实验配置（分子、SCF、活性空间、量子、后端等）。 | [config](/modules/config) · [字段索引](/reference/config-fields/) |
| **ansatz** | 变分试探波函数线路族（HEA、UCCSD、ADAPT 池生长等）。 | [算法索引](/modules/quantum/algorithms/) · [选型](/guide/algorithm-and-ansatz-menu) |
| **operator pool** | ADAPT / IQEB 候选算符集合（如费米子单双激发）。 | [算符池](/modules/quantum/algorithms/operator-pools) |
| **PauliAveragingProtocol** | 将哈密顿量期望值拆成 Pauli 组并按协议采样/估计的运行时对象。 | [Pauli 协议](/modules/quantum/algorithms/pauli-protocol) · [协议模块](/modules/protocols) |
| **repro** | 管线结果中的可复现导出字典（严格 JSON 子集）；可用 `repro_json_dumps`。 | [repro](/modules/repro) · [读 repro 键](/tutorial/read-repro-keys) |
| **parity** | Methods 风格对照表/导出（算法×映射×后端等一致性证据）。 | [parity 合约路径](/reference/parity-contract-import-paths) · [公开矩阵](/parity/public-matrix) |
| **capability_surface** | 机器可读能力面（`capability_surface_v2`）：当前安装能跑什么。 | [contracts](/modules/contracts) · `GET /v1/meta/capability-surface` |
| **embedding** | 分片/嵌入：DMET、Schmidt bath、投影（Mulliken 等）或 plugin。 | [嵌入总览](/modules/chem/embedding) · [DMET](/modules/chem/embedding-dmet) · [Schmidt](/modules/chem/embedding-schmidt) · [projection](/modules/chem/embedding-projection) |
| **HEA** | Hardware-Efficient Ansatz：浅层参数化门层，与化学结构弱耦合。 | [VQE/HEA](/modules/quantum/algorithms/vqe-hea) |
| **UCCSD** | Unitary Coupled Cluster Singles and Doubles；化学启发 ansatz。 | [UCCSD](/modules/quantum/algorithms/uccsd) |
| **VQD / QSE / SCEOM** | 激发态路径：变分量子虚时/惩罚（VQD）、量子子空间展开（QSE）、方程运动式 SCEOM。 | [激发态](/modules/quantum/excited-states) · [VQD](/modules/quantum/algorithms/vqd) · [QSE](/modules/quantum/algorithms/qse) · [SCEOM](/modules/quantum/algorithms/sceom) |
| **BackendSpec** | 执行目标描述（`provider`、shots、Qiskit/UQC 等字段）；`executor_from_spec` 据此建执行器。 | [backends](/modules/backends) · [API 面](/reference/api-surface) |
| **schema_ids** | `contracts.schema_ids` 中稳定 schema 字符串常量（SoT），避免魔法字面量。 | [contracts](/modules/contracts) |
| **QMEF** | Quantum Molecular Energy/Force 数据集模式（帧/轨迹附着到 MD/ML 导出）。 | [md-bridge](/modules/md-bridge) · [MD/ML 指南](/guide/md-ml-active-learning) |

---

## 相关

- [FAQ](/faq/) · [开始使用](/getting-started)
- [配置字段](/reference/config-fields/) · [Python SDK](/reference/python-sdk)
