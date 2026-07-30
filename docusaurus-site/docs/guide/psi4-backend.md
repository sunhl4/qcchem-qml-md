---
title: Psi4 经典后端
description: Psi4 作为 ChemIntegralSolver 可选后端的配置、选型与验证。
---

# Psi4 经典后端

:::tip 模块手册
经典 solver 契约与注册 → [chem · solvers](/modules/chem/solvers) · [后端适配](./backend-adapter-quickstart) · [P1 化学](./chemistry-and-embedding)
:::

## 决策块

| | |
|--|--|
| **何时用** | 与 PySCF 交叉验证积分/RHF；Methods 需第二经典后端 |
| **何时不用** | 首次上手；无 Psi4 环境却依赖 CI 默认路径 |
| **互斥 / 注意** | PR 默认不跑完整 Psi4 job（label / schedule）；与量子算法改动分 PR |
| **链教程 + 深读** | [solvers](/modules/chem/solvers) · [backend-adapter](./backend-adapter-quickstart) · 仓库 psi4 设计稿 |

**设计文档**：仓库 [`docs/execution/psi4_get_integrals_design.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/execution/psi4_get_integrals_design.md)。

Psi4 是 **ChemIntegralSolver** 的可选实现，用于与 PySCF 交叉验证与多后端 parity，不是默认 CI 数值主路径。

## 何时用

- 需要与 PySCF 对照同一分子的积分 / RHF 能量
- 论文 Methods 要求声明第二经典后端
- 本地已有 micromamba / Psi4 环境

## 何时不要用

- 第一次跑通管线（先用 `scf.driver: pyscf` 或 precomputed）
- 无 Psi4 安装却在共享 CI 作业里依赖 Psi4（应使用 `pytest -m psi4` 专用 job）
- 把 Psi4 特有选项与量子算法改动混在同一次 diff 里排查

## 配置要点

```yaml
scf:
  driver: psi4
  method: RHF
  psi4:
    density_fit: false
    # 其余字段与代表 YAML 对齐
```

几何、活性空间、映射仍走标准 `molecule` / `active_space`；只切换经典驱动。

## 示例 YAML

| 文件 | 说明 |
|------|------|
| `example_h2_psi4_rhf_sto3g.yaml` | Psi4 RHF 基准 |
| `example_h2_psi4_avas.yaml` | AVAS 活性空间 |
| `example_h2_psi4_schmidt_dmet.yaml` | Schmidt DMET |
| `example_h2_psi4_projection_mulliken.yaml` | Projection Mulliken |

## 与 PySCF 的关系

| 项 | PySCF | Psi4 |
|----|-------|------|
| CI 数值主路径 | 是 | 否（专用 `test-psi4`） |
| 默认示例 | `example_h2.yaml` | 上表 Psi4 族 |
| Parity 矩阵 | 见仓库 docs | [`psi4_pyscf_parity_matrix.md`](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/execution/psi4_pyscf_parity_matrix.md) |

## 决策表：驱动选择

| 目标 | 选择 |
|------|------|
| 日常开发 / 文档烟测 | `pyscf` |
| 交叉验证积分与 HF | 同一几何下分别跑 PySCF 与 Psi4 YAML |
| 无经典 SCF、只验量子 | `precomputed` bundle |
| 自定义引擎 | [backend-adapter-quickstart](./backend-adapter-quickstart) |

## CI

Psi4 测试在 GitHub Actions `test-psi4` job 中运行：`pytest -m psi4`。

## 验证命令

配置可加载（不要求本机已装 Psi4）：

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c = load_experiment_config('configs/example_h2_psi4_rhf_sto3g.yaml')
print(c.experiment_id, c.scf.driver, c.scf.method)
"
```

期望：打印含 `psi4` 与 `RHF` 的一行。

若已安装 Psi4，可进一步：

```bash
python3 -m pytest -m psi4 -q
```

期望：Psi4 标记用例通过（或按本地选择跳过策略）。

## 相关

- [P1 化学与嵌入](./chemistry-and-embedding)
- [AVAS → CASSCF](./avas-casscf-workflow)
- [chem · solvers](/modules/chem/solvers)
- [双线路经典输入](./dual-classical-ingress)

## 排障速查

| 现象 | 可能原因 | 动作 |
|------|----------|------|
| `ImportError` / 找不到 psi4 | 未装 Psi4 环境 | 使用 micromamba 环境或改回 `pyscf` |
| 能量与 PySCF 差很大 | 基组 / 几何 / 密度拟合不一致 | 对齐 YAML 后再比 fingerprint |
| CI 失败仅在 psi4 job | 预期隔离 | 看 `test-psi4` 日志，勿在默认 job 强依赖 |

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
for p in [
  'configs/example_h2_psi4_rhf_sto3g.yaml',
  'configs/example_h2_psi4_avas.yaml',
  'configs/example_h2_psi4_projection_mulliken.yaml',
]:
  c = load_experiment_config(p)
  print(c.experiment_id, c.scf.driver)
"
```

期望：三行均可打印且 `driver` 为 `psi4`。
