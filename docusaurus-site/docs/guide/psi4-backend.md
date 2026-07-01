---
title: Psi4 经典后端
description: Psi4 作为 ChemIntegralSolver 可选后端的配置与设计说明。
---

# Psi4 经典后端

**设计文档**：仓库 [`docs/execution/psi4_get_integrals_design.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/execution/psi4_get_integrals_design.md)。

## 示例 YAML

| 文件 | 说明 |
|------|------|
| `example_h2_psi4_rhf_sto3g.yaml` | Psi4 RHF 基准 |
| `example_h2_psi4_avas.yaml` | AVAS 活性空间 |
| `example_h2_psi4_schmidt_dmet.yaml` | Schmidt DMET |

## CI

Psi4 测试在 GitHub Actions `test-psi4` job 中运行：`pytest -m psi4`。

## 与 PySCF 的关系

PySCF 仍是 CI 数值主路径；Psi4 用于交叉验证与多后端 parity。见 [`docs/execution/psi4_pyscf_parity_matrix.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/execution/psi4_pyscf_parity_matrix.md)。
