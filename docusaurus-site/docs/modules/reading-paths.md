---
title: 按任务阅读路径
description: 基态、自适应、激发态、测量缓解、化学嵌入五条任务路径（与选型 P1–P4 编号无关）。
---

# 按任务阅读路径

按**你现在要做的事**选一条路，链向 [算法深读](./quantum/algorithms/) 与模块手册。

> **编号说明**：下方是**任务路径名**（基态 / 自适应 / …）。工程能力四柱仍叫 **选型 P1–P4**（见 [手册](/guide/) 与首页），二者不要混用同一套 P 编号。

选型总览：[手册 · 选型 P1–P4](/guide/) · 模块地图：[总览](./)。

---

## 1. 五条任务路径

| 路径 | 科学问题 | 深读重心 |
|------|----------|----------|
| **基态** | 基态变分 | VQE/HEA、UCCSD |
| **自适应** | 生长 ansatz | ADAPT、IQEB、算符池 |
| **激发态** | 激发能级 | VQD、QSE、SCEOM |
| **测量缓解** | 分组测量与缓解 | Pauli、backends、mitigation |
| **化学嵌入** | 活性空间 / 嵌入 | AVAS、DMET、projection、dual-ingress |

辅助：GQE sidecar、作业/repro、MD/ML（见文末）。

---

## 2. 怎么用

1. 选一条任务路径。  
2. 深读 → 模块 → 代表 YAML。  
3. 跑各页验证命令。  
4. 平台面转 [jobs](./jobs) / [api-sdk](./api-sdk) / [ops-light](./ops-light)。

```python
from qchem_stack.sdk import run_pipeline_from_config, load_experiment_config
```

---

## 3. YAML 线索

| 路径 | 典型线索 |
|------|----------|
| 基态 | `quantum.algorithm: vqe` + `ansatz: hea` / `uccsd` |
| 自适应 / 迭代 QCC | `algorithm: adapt` / `iqeb` / `iqcc` |
| 激发态 | `excited.vqd` / `qse` / `sceom` |
| 测量缓解 | `quantum.pauli.use_protocol` + `backend` + `mitigation` |
| 化学嵌入 | `embedding.*` / AVAS / `scf.driver: precomputed` |
| GQE | **顶层** `gqe:`（不是 `quantum.algorithm`） |

所有实验：`schema_version: "2"`。

---

## 4. 路径明细

### 基态

1. [开始使用](/getting-started) · [15 分钟上手](/tutorial/quickstart)  
2. [VQE / HEA](./quantum/algorithms/vqe-hea) · [UCCSD](./quantum/algorithms/uccsd) · [映射](./chem/mappings)  
3. [config](./config) · [orchestration](./orchestration)  

配置：`configs/example_h2.yaml`、`example_h2_uccsd.yaml`。

```bash
python3 -c "from qchem_stack.sdk import run_pipeline_from_config; o=run_pipeline_from_config('configs/example_h2.yaml'); print('ok', 'repro' in o)"
```

### 自适应

1. [ADAPT](./quantum/algorithms/adapt-vqe) · [IQEB](./quantum/algorithms/iqeb) · [iQCC](./quantum/algorithms/iqcc) · [算符池](./quantum/algorithms/operator-pools)  
2. 教程：[ADAPT pool 烟测](/tutorial/adapt-pool-smoke) · 配置：`example_h2_iqcc.yaml`  

### 激发态

1. [VQD](./quantum/algorithms/vqd) · [QSE](./quantum/algorithms/qse) · [SCEOM](./quantum/algorithms/sceom)  
2. 选型：[激发态](/guide/excited-states-vqd-qse-sceom)  

### 测量缓解

1. [Pauli 协议](./quantum/algorithms/pauli-protocol) · [protocols](./protocols)  
2. [Qiskit](./backends/qiskit) · [mitigation](./mitigation)  
3. [切换后端](/tutorial/switch-backend-compare) · [ZNE](/tutorial/zne-qiskit-repro)  

### 化学嵌入

1. [AVAS–CASSCF](./chem/avas-casscf)  
2. [DMET](./chem/embedding-dmet) · [projection](./chem/embedding-projection) · [Schmidt](./chem/embedding-schmidt)  
3. [dual-ingress](./chem/dual-ingress) · 教程：[DMET](/tutorial/dmet-self-consistent)、[projection](/tutorial/projection-embedding-deep-dive)  

记住：`pre_quantum` 定 `qh`；`embedding_workflow` 只审计。

---

## 5. 扩展

| 目标 | 下一跳 |
|------|--------|
| GQE | [深读](./quantum/algorithms/gqe) · [选型](/guide/gqe-generative-eigensolver) |
| 自定义 | [custom-plugin](./quantum/algorithms/custom-plugin) |
| 作业 / HTTP | [jobs](./jobs) · [api-sdk](./api-sdk) · [repro](./repro) |
| MD/ML | [md-bridge](./md-bridge) |

---

## 6. 相关

- [算法深读](./quantum/algorithms/) · [教程索引](/tutorial/) · [配置↔教程矩阵](/reference/tutorial-config-matrix)  
- [parity](/guide/parity-repro-contract) · [选型 P1–P4](/guide/)
