---
title: P2 程序构建
description: 算法、ansatz、算符池、协议与变分插件的决策指南。
---

# P2 程序构建

:::tip 模块手册
[quantum 算法深读](/modules/quantum/algorithms/) · [protocols](/modules/protocols) · [orchestration](/modules/orchestration) · [算符池](/modules/quantum/algorithms/operator-pools)
:::

P2 把化学问题组织成可执行程序：**外层算法 → ansatz / 算符池 → Pauli 协议 →（可选）激发态侧车**。

实现主路径：`orchestration` 调用 `quantum.variational_plugins` → 可选 `excited_stages` → `protocols`。

**论文级参数与公式以 [算法深读索引](/modules/quantum/algorithms/) 为权威**；本页只做选型。短菜单见 [algorithm-and-ansatz-menu](./algorithm-and-ansatz-menu)。

## 决策树

```text
需要自适应生长 ansatz？
  ├─ 是 → algorithm: adapt | iqeb  +  选定算符池
  └─ 否 → algorithm: vqe（或 sa_vqe / qpe…）
           └─ 选择 variational.ansatz（hea / uccsd / qcc / …）

需要采样可观测量？
  └─ 启用 Pauli 协议 + 后端 shots

需要激发态？
  └─ 配置 VQD / QSE / SCEOM 侧车

研究生成式？
  └─ 顶层 gqe: 块（不是 quantum.algorithm）
```

## 外层算法选型

| `quantum.algorithm` | 何时用 | 何时不要用 | 代表 YAML | 深读 |
|---------------------|--------|------------|-----------|------|
| `vqe` | 默认变分、CI 基线 | — | `example_h2.yaml` | [VQE/HEA](/modules/quantum/algorithms/vqe-hea) |
| `adapt` | 需要池生长、可解释算符序列 | 超大池无截断的首次调试 | `example_h2_adapt_singles_pool.yaml` | [ADAPT](/modules/quantum/algorithms/adapt-vqe) |
| `iqeb` | IQEB 外环 + 内层 VQE | 与 ADAPT 混配同一池而不懂别名 | `example_h2_iqeb.yaml` | [IQEB](/modules/quantum/algorithms/iqeb) |
| `sa_vqe` | 态平均 / 多态 | 单态基线对比 | `example_h2_sa_vqe.yaml` | [SA-VQE](/modules/quantum/algorithms/sa-vqe) |
| `qpe` / QPE 轨道 | 相位估计演示、Methods sidecar | 当作生产基态能量主路径 | `example_h2_qpe_main.yaml` · `example_h2_qpe_track.yaml` | [QPE](/modules/quantum/algorithms/qpe) |

完整注册表以运行时 `list_registered_algorithm_ids()` 为准。

## Ansatz 选型（`variational.ansatz`）

| ID | 何时用 | 何时不要用 | 代表 YAML |
|----|--------|------------|-----------|
| `hea` | 硬件友好、快速烟测 | 需要化学可解释激发算符时 | `example_h2.yaml` |
| `uccsd` | 化学相关闭壳层 | 非 JW 映射主线 | `example_h2_uccsd.yaml` |
| `qcc` / `upccgsd` / `puccd` | 成对 / 受限簇 | 与 HEA 深度键混用且不对照 | `example_h2_qcc.yaml` 等 |
| `algorithm: iqcc`（+PT） | 迭代穿衣 QCC（开放实现） | 默认生产主路径 / 闭源比特对齐 | `example_h2_iqcc.yaml` / `_pt` |
| `uccgd` / `qite` / `vsqs` | 研究插件 | 生产默认路径 | 对应 `example_h2_*` |

## 算符池与协议

| 主题 | 选型页 | 模块权威 |
|------|--------|----------|
| ADAPT / IQEB 池 | [operator-pools-adapt-iqeb](./operator-pools-adapt-iqeb) | [operator-pools](/modules/quantum/algorithms/operator-pools) |
| Pauli 采样 | [pauli-protocol-and-shots](./pauli-protocol-and-shots) | [pauli-protocol](/modules/quantum/algorithms/pauli-protocol) |
| 激发态侧车 | [excited-states-vqd-qse-sceom](./excited-states-vqd-qse-sceom) | [VQD](/modules/quantum/algorithms/vqd) · [QSE](/modules/quantum/algorithms/qse) · [SCEOM](/modules/quantum/algorithms/sceom) |
| GQE | [gqe-generative-eigensolver](./gqe-generative-eigensolver) | [GQE](/modules/quantum/algorithms/gqe) |

## 何时不要用（总则）

- 不要在未跑通 `vqe` + `hea` + `statevector` 前启用 ADAPT + Pauli shots + VQD。
- 不要把 `gqe.enabled` 写成 `quantum.algorithm: gqe`（无效）。
- 不要把研究插件（QITE / VSQS）或未收敛的 iQCC 大规模协议写进「默认生产」CI 主路径；iQCC 小分子烟雾可用 `example_h2_iqcc.yaml`。
- 不要假设激发态侧车会改写基态 `energy_after_variational` 的语义而不读 repro 键。

## 本柱子页

| 主题 | 页面 |
|------|------|
| 算法与 ansatz 短菜单 | [algorithm-and-ansatz-menu](./algorithm-and-ansatz-menu) |
| 算符池 ADAPT / IQEB | [operator-pools-adapt-iqeb](./operator-pools-adapt-iqeb) |
| Pauli 协议与采样 | [pauli-protocol-and-shots](./pauli-protocol-and-shots) |
| 激发态 VQD / QSE / SCEOM | [excited-states-vqd-qse-sceom](./excited-states-vqd-qse-sceom) |
| GQE（研究轨道） | [gqe-generative-eigensolver](./gqe-generative-eigensolver) |

## 代表配置速查

| 意图 | YAML |
|------|------|
| HEA-VQE | `configs/example_h2.yaml` |
| UCCSD | `configs/example_h2_uccsd.yaml` |
| ADAPT singles 池 | `configs/example_h2_adapt_singles_pool.yaml` |
| IQEB | `configs/example_h2_iqeb.yaml` |
| VQD | `configs/example_h2_vqd_uccsd.yaml` |
| QPE track | `configs/example_h2_qpe_track.yaml` |
| GQE Plan B | `configs/example_h2_gqe_plan_b.yaml` |
| Pauli + UCCSD | `configs/example_h2_uccsd_pauli_protocol.yaml` |

## 最小 YAML 形状

```yaml
quantum:
  algorithm: vqe
  vqe:
    depth: 2
    maxiter: 80
  variational:
    ansatz: hea
```

ADAPT 示例要点：

```yaml
quantum:
  algorithm: adapt
  adapt:
    pool: singles          # 以注册表 / 代表 YAML 为准
  variational:
    ansatz: hea
```

## 源码锚点

| 关注点 | 模块 |
|--------|------|
| Ansatz 注册 | `quantum.ansatz_registry` |
| 算法 / 插件 | `quantum.algorithm_registry`、`quantum.variational_plugins` |
| 算符池 | `quantum.operator_pool_registry` |
| 协议 | `protocols.protocol`、`protocol_run*` |
| 激发态 | `quantum.excited_plugins`、`orchestration.excited_stages` |

## 工程原则

- 算法实现与编排解耦；扩展优先走注册表 / 插件，而不是改 pipeline 核心。
- 中间产物写入 `run_summary` / parity，便于回归。
- 研究插件单独标注，勿与生产默认路径混淆。

## 验证命令

```bash
python3 -c "
from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids
from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
print('ansatz', sorted(list_registered_ansatz_ids())[:8])
print('algo', sorted(list_registered_algorithm_ids())[:8])
"
```

期望：打印非空 ID 列表。

配置加载：

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c = load_experiment_config('configs/example_h2_adapt_singles_pool.yaml')
print(c.experiment_id, c.quantum.algorithm)
"
```

期望：`h2_adapt_singles_pool_sto3g adapt`（或配置内等价 algorithm 字段）。

## 相关教程

- [ADAPT pool 烟测](../tutorial/adapt-pool-smoke)
- [QPE track](../tutorial/qpe-track)
- [GQE 变体](../tutorial/gqe-variants)
- [UCCSD Trotter 导出](../tutorial/uccsd-trotter-export)

## 下一步

进入 [P3 执行与分析](./execution-and-analysis)。
