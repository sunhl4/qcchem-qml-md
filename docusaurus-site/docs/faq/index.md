---
title: 常见问题
description: 安装、schema、采样互斥、GQE extras、API 与选型等高频问题。
keywords:
  - FAQ
  - schema_version
  - PySCF
  - Psi4
  - GQE
---

# 常见问题

安装与跑通卡点。深入说明见 [模块手册](/modules/) 与 [教程](/tutorial/)。

---

## 缺少 PySCF / 没有 chem extras

**症状：** `ImportError` / `ModuleNotFoundError: pyscf`，或 SCF 阶段失败。

**处理：**

```bash
pip install "qchem-stack[chem]"
# 或开发树：
pip install -e ".[chem]"
```

无 PySCF 时可只跑预计算路径：

```bash
python3 scripts/smoke_pipeline.py --precomputed-only
```

见 [开始使用](/getting-started) · [安装档位](/reference/install-profiles)。

---

## Psi4 环境怎么配

Psi4 不在默认 wheel 里；需本机安装 Psi4，并设 `scf.driver: psi4`。示例配置见仓库 `configs/example_h2_psi4_rhf_sto3g.yaml`。

能力与门控见 [Psi4 后端](/guide/psi4-backend) · [化学求解器](/modules/chem/solvers)。

---

## `schema_version` 必须是 `"2"`

实验 YAML 顶层必须：

```yaml
schema_version: "2"
```

这是 `SCHEMA_VERSION_CURRENT`。旧扁平 schema 会在加载时迁移或拒绝。详见 [config 模块](/modules/config)。

---

## `precomputed` 的 `bundle_path` 在哪

`scf.driver: precomputed` 时，路径写在**嵌套**子块，不是顶层：

```yaml
scf:
  driver: precomputed
  precomputed:
    bundle_path: "path/to/bundle.json"
```

组合限制见 [Pre-quantum YAML 矩阵](/reference/pre-quantum-yaml-matrix) · [scf 字段](/reference/config-fields/scf)。

---

## SCBK 与 UCCSD 能一起用吗

UCCSD Trotter 路径按 $n_{\mathrm{so}} = n_{\mathrm{qubits}}$ 断言；**SCBK / HCB** 会改变有效量子比特数，勿与默认 UCCSD 假定混用。优先 **JW**（或兼容的 BK）。对照：[映射手册](/modules/chem/mappings) · [UCCSD](/modules/quantum/algorithms/uccsd)。

---

## `run_sampled` 与 `run_qiskit_shots` 互斥

Pauli 协议两条采样路径**不能同时开**：

| 开关 | 含义 |
|------|------|
| `quantum.pauli.run_sampled` / `run_sampled_pauli_protocol` | 通用采样协议 |
| `run_qiskit_shots_pauli_protocol` | Qiskit 比特串 counts |

二选一。见 [Qiskit shots](/reference/qiskit-shot-counts) · [Pauli 协议](/modules/quantum/algorithms/pauli-protocol)。

---

## GQE 需要 `[gqe]` extra

GPT-QE / GQE 依赖 JAX：

```bash
pip install "qchem-stack[gqe]"
```

未装时相关算法不可用。见 [GQE](/modules/quantum/algorithms/gqe) · [教程](/tutorial/gqe-nakaji-h2)。

---

## API 为何绑定 `127.0.0.1`

本地 HTTP 默认只建议：

```bash
uvicorn qchem_stack.api.app:app --host 127.0.0.1 --port 8000
```

避免无意暴露作业面。见 [HTTP + SQLite](/reference/http-api-sqlite-jobs) · [异步 HTTP 教程](/tutorial/async-run-via-http)。

---

## configs catalog 与 scenarios 有何区别

| 概念 | 用途 |
|------|------|
| **catalog** | 仓库/文档中的配置清单与浏览（[配置目录](/reference/configs-catalog)） |
| **scenarios** | 入门场景 id（`configs/scenarios/`，`qchem-run --list-scenarios` / `SCENARIOS`） |

新手先用 scenarios；查全量 YAML 用 catalog。见 [示例](/examples/) · [SDK](/modules/api-sdk)。

---

## Barren plateaus（梯度消失）提示

深 HEA / 随机初参易出现 barren plateaus：训练信号 $\nabla_\theta E \approx 0$。实务建议：

- 先用浅层 HEA 或化学启发 ansatz（UCCSD / ADAPT）
- 控制深度与参数维数
- 用小体系验证可学习性后再放大

见 [VQE/HEA](/modules/quantum/algorithms/vqe-hea) · [算法选型](/guide/algorithm-and-ansatz-menu)。

---

## 相关入口

- [模块手册](/modules/) · [阅读路径](/modules/reading-paths)
- [教程](/tutorial/) · [15 分钟上手](/tutorial/quickstart)
- [术语表](/glossary/) · [配置字段](/reference/config-fields/)
