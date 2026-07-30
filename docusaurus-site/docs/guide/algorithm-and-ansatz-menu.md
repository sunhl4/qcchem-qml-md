---
title: 算法与 ansatz 菜单
description: 短决策矩阵；论文级表以 modules/quantum/algorithms 为权威。
---

# 算法与 ansatz 菜单

:::tip 模块手册
**论文 + 数学 + 参数 + 调用（权威）** → [算法深读索引](/modules/quantum/algorithms/)
:::

本页只保留**短决策矩阵**。完整注册表、公式、YAML 字段与验证命令见算法深读页；柱内总决策见 [P2 程序构建](./program-construction)。

## 两层名字

| 层 | YAML 键 | 作用 |
|----|---------|------|
| 外层算法 | `quantum.algorithm` | `vqe` / `adapt` / `iqeb` / `iqcc` / `sa_vqe` / `qpe` … |
| 变分 ansatz | `quantum.variational.ansatz` | `hea` / `uccsd` / `qcc` / … |

物化入口：`quantum.variational_plugins.registry.run_variational_stage`。

## 短决策矩阵

| 你的目标 | 建议 | 深读（权威） |
|----------|------|----------------|
| 先跑通 | `vqe` + `hea` + statevector | [VQE/HEA](/modules/quantum/algorithms/vqe-hea) |
| 化学相关变分 | `ansatz: uccsd`（JW） | [UCCSD](/modules/quantum/algorithms/uccsd) |
| 成对 / 受限簇 | `qcc` / `upccgsd` / `puccd` | [QCC…](/modules/quantum/algorithms/qcc-paired) |
| 自适应生长 | `adapt` 或 `iqeb` + 池 | [ADAPT](/modules/quantum/algorithms/adapt-vqe) · [IQEB](/modules/quantum/algorithms/iqeb) · [池全表](/modules/quantum/algorithms/operator-pools) |
| 迭代 QCC / +PT | `algorithm: iqcc`（`enable_pt`） | [iQCC](/modules/quantum/algorithms/iqcc) |
| 态平均 | `sa_vqe` | [SA-VQE](/modules/quantum/algorithms/sa-vqe) |
| 激发态侧车 | VQD / QSE / SCEOM | [VQD](/modules/quantum/algorithms/vqd) · [QSE](/modules/quantum/algorithms/qse) · [SCEOM](/modules/quantum/algorithms/sceom) |
| 相位估计演示 | QPE / demo track | [QPE](/modules/quantum/algorithms/qpe) |
| 生成式研究 | 顶层 `gqe:` | [GQE](/modules/quantum/algorithms/gqe) |
| 自定义 | 变分插件 | [custom-plugin](/modules/quantum/algorithms/custom-plugin) |
| 研究 ansatz | UCCGD / QITE / VSQS（iQCC 见上行） | [研究索引](/modules/quantum/algorithms/research-ansatze) |

## 何时不要用

- 不要在本页复制维护长注册表（会与深读页漂移）——以 `/modules/quantum/algorithms/` 为准。
- 不要把 GQE 写成 `quantum.algorithm: gqe`。
- 不要在非 JW 映射上假设 UCCSD 主线可运行。

## 最小 YAML

```yaml
quantum:
  algorithm: vqe
  vqe:
    depth: 2
    maxiter: 80
  variational:
    ansatz: hea
```

## 验证命令

```bash
python3 -c "
from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids
print(sorted(list_registered_ansatz_ids()))
"
```

期望：非空 ansatz ID 列表。

## 相关

- [P2 程序构建](./program-construction)
- [算符池](./operator-pools-adapt-iqeb)
- [算法深读索引](/modules/quantum/algorithms/)
- [按任务阅读](/modules/reading-paths)
