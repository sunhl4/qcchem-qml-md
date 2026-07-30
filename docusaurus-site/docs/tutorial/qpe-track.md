---
title: QPE track 烟测
description: 用 example_h2_qpe_track.yaml 验证 QPE demo track 配置与相关键。
---

# QPE track 烟测

本教程覆盖 **QPE Methods / demo track** 代表配置：`configs/example_h2_qpe_track.yaml`（亦可对照 `example_h2_qpe_main.yaml`）。

## 目标

- 加载 QPE track YAML
- 理解 demo track 与主变分路径的关系（sidecar / Methods，而非默认生产基态路径）
- 知道 `qpe_qec_demo` 包的入口（Bayesian stub、track payload）

## 前置

```bash
pip install -e ".[chem]"
```

## 配置选择

| 文件 | 用途 |
|------|------|
| `configs/example_h2_qpe_track.yaml` | track / sidecar 演示（本教程主配置） |
| `configs/example_h2_qpe_main.yaml` | QPE 主算法轨道对照 |
| `configs/example_h2_qpe_track_parity_integrations.yaml` | 含 resource / parity integrations |

深读：[QPE](/modules/quantum/algorithms/qpe) · [integrations · qpe_qec_demo](/modules/integrations)。

## 验证命令

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c = load_experiment_config('configs/example_h2_qpe_track.yaml')
print(c.experiment_id)
print(c.quantum.algorithm)
from qchem_stack.qpe_qec_demo import BayesianQPEStub
print(BayesianQPEStub().estimate([(0.0, 0.5), (1.0, 1.0)]).get('schema'))
"
```

## 期望输出

- 退出码 `0`
- `experiment_id` 含 `qpe_track`（或配置内 id）
- 打印 `quantum.algorithm`（常见为 `vqe` 且另挂 demo track，以 YAML 为准）
- Bayesian stub schema 为 `bayesian_qpe_stub_map_v1`（或实现导出的等价 schema 字符串）

## 可选：对照 main 配置

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
for p in ['configs/example_h2_qpe_track.yaml', 'configs/example_h2_qpe_main.yaml']:
  c = load_experiment_config(p)
  print(p, c.experiment_id, c.quantum.algorithm)
"
```

期望：两行均可打印，无异常。

## 下一步

- [P2 程序构建](../guide/program-construction)
- [资源估计](../guide/resource-estimation-methods)
- [读 repro 键](./read-repro-keys)
