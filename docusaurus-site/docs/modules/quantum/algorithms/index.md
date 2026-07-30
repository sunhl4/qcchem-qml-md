---
title: 算法深读索引
description: 完整算法目录：文献级深读入口、YAML 线索与跨模块链接。
---

# 算法深读索引

本目录面向**使用者**：每个算法一页，固定包含文献、理论思想、数学实现、参数、函数调用、验证与边界（风格对齐 PennyLane / Qiskit 手册）。  
任务导向：[按任务阅读路径](/modules/reading-paths)。  
速查枢纽（不重复正文）：[ansatz-algorithms](../ansatz-algorithms) · [adapt-iqeb](../adapt-iqeb) · [excited-states](../excited-states)。

---

## 1. 如何使用本目录

1. 用下表按任务选算法。  
2. 打开深读页：文献 → 问题 → 理论 → 本栈数学 → YAML → Python → 验证 → 调参。  
3. 化学前置：[chem 索引](/modules/chem/)；执行后端：[backends](/modules/backends)。

选型总表：[算法与 ansatz 菜单](/guide/algorithm-and-ansatz-menu)。

---

## 2. 基态 / 变分

| 算法 | YAML 线索 | 深读页 |
|------|-----------|--------|
| VQE + HEA | `algorithm: vqe` + `ansatz: hea` | [VQE / HEA](./vqe-hea) |
| UCCSD-VQE | `ansatz: uccsd` | [UCCSD](./uccsd) |
| ADAPT-VQE | `algorithm: adapt` | [ADAPT-VQE](./adapt-vqe) |
| IQEB | `algorithm: iqeb` | [IQEB](./iqeb) |
| iQCC / iQCC+PT | `algorithm: iqcc`（`iqcc.enable_pt`） | [iQCC](./iqcc) |
| QCC / upCCGSD / pUCCD | `ansatz: qcc` 等 | [成对/量子耦合簇](./qcc-paired) |
| SA-VQE | `algorithm: sa_vqe` | [SA-VQE](./sa-vqe) |
| UCCGD | `ansatz: uccgd` | [UCCGD](./uccgd) |
| QITE | 见深读 | [qite](./qite) |
| VSQS | 见深读 | [vsqs-ansatz](./vsqs-ansatz) |
| Tetris / 研究 ansatz | 见索引 | [research-ansatze](./research-ansatze) |
| 自定义插件 | `algorithm_factory` | [custom-plugin](./custom-plugin) |

摘要入口：[ADAPT / IQEB](../adapt-iqeb) · [算法与 ansatz](../ansatz-algorithms)。

---

## 3. 激发态

| 算法 | YAML 线索 | 深读页 |
|------|-----------|--------|
| VQD | `excited.vqd` | [VQD](./vqd) |
| QSE | `excited.qse` | [QSE](./qse) |
| SCEOM | `excited.sceom` | [SCEOM](./sceom) |

摘要入口：[激发态](../excited-states) · 选型：[VQD / QSE / SCEOM](/guide/excited-states-vqd-qse-sceom)。

---

## 4. 相位估计 / 动力学 / 生成式

| 算法 | YAML 线索 | 深读页 |
|------|-----------|--------|
| QPE 三件套 | `qpe_*` / `demos.qpe` | [QPE](./qpe) |
| VQS / McLachlan | `demos.vqs` | [VQS](./vqs) |
| GQE (GPT-QE) | `gqe` 块 | [GQE](./gqe) |

---

## 5. 测量、池与嵌入（跨模块）

| 主题 | 深读页 |
|------|--------|
| 算符池全表 | [operator-pools](./operator-pools) |
| Pauli 平均协议 | [pauli-protocol](./pauli-protocol) |
| 费米子映射 | [chem · 映射](../../chem/mappings) |
| 哈密顿量 / 指纹 | [chem · hamiltonian](../../chem/hamiltonian) |
| AVAS–CASSCF | [avas-casscf](../../chem/avas-casscf) |
| 双线路 / precomputed | [dual-ingress](../../chem/dual-ingress) |
| 嵌入总览 | [embedding](../../chem/embedding) |
| DMET / projection / Schmidt | [DMET](../../chem/embedding-dmet) · [projection](../../chem/embedding-projection) · [Schmidt](../../chem/embedding-schmidt) |
| ZNE / PMSV / SPAM | [mitigation](../../mitigation) |
| Backends 分册 | [backends](../../backends) |

---

## 6. 注册表速查

```python
from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
from qchem_stack.quantum.excited_plugins.registry import list_registered_excited_ids

print(list_registered_ansatz_ids())
print(list_registered_algorithm_ids())
print(list_registered_excited_ids())
```

---

## 7. 验证命令

```bash
python -c "from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids; print(list_registered_algorithm_ids())"

pytest tests/quantum/test_executor_backends.py -q --tb=no
```

最小端到端（HEA）：

```bash
python -c "from qchem_stack.sdk import run_pipeline_from_config; o=run_pipeline_from_config('configs/example_h2.yaml'); print(o.get('energy_after_variational'))"
```

---

## 8. 相关

- [quantum 模块](/modules/quantum/) · [reading-paths](/modules/reading-paths)  
- [chem](/modules/chem/) · [backends](/modules/backends) · [protocols](/modules/protocols)
