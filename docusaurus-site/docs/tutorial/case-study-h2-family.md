# 案例：H2 家族链式改配

本案例展示如何基于同一模板配置，逐步修改参数完成一组小体系实验并产出对照记录。

## 目标

- 用统一骨架做多组可对比实验
- 让每一步配置改动可解释、可追溯
- 产出可复盘的对照结果表

## 案例步骤

1. 以 `example_h2` 为基线（`scf.driver: pyscf`）
2. 调整活性空间与算法参数
3. 比较不同 **量子** backend 和 shots 的输出差异
4. 汇总 `run_summary` 与 `repro` 做对照表

### 经典化学 driver 变体（同一 H₂ 骨架）

| 主题 | 配置 |
|------|------|
| PySCF 默认 canonical | `configs/example_h2.yaml` |
| Psi4 canonical CASCI | `configs/example_h2_psi4_rhf_sto3g.yaml` |
| Psi4 Schmidt DMET | `configs/example_h2_psi4_schmidt_dmet.yaml` |
| Psi4 AVAS | `configs/example_h2_psi4_avas.yaml` |
| Psi4 Mulliken projection | `configs/example_h2_psi4_projection_mulliken.yaml` |

加载期组合规则见仓库 [`docs/pre_quantum_yaml_matrix.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/pre_quantum_yaml_matrix.md)。

## 实施建议

- 统一命名每个变体配置（如 `h2_v1`, `h2_v2`）
- 每次只改一个主题（算法/后端/采样）  
- 记录每次改动的“预期影响”和“实际结果”

## 产出建议

- 一份配置差异表
- 一份结果摘要表
- 一份可复现实验记录（含 trace 与版本信息）

## 验证清单

- 所有变体都可独立运行
- 对照表包含配置差异与关键结果
- 任一结果可回溯到对应配置和运行记录

## 下一步

- [切换 Backend 并对比结果](./switch-backend-compare)
- [repro 关键字段速览](./read-repro-keys)
