---
title: integrations 模块
description: GQE、TKET、Nexus、L3 基准；GQE 为顶层 gqe 块。
---

# integrations 模块

`qchem_stack.integrations` 放置跨栈编排胶水与研究/对标参考（非 chem/quantum 数学内核）。

**GQE 深读**：[GQE 算法页](./quantum/algorithms/gqe) · 选型：[GQE](/guide/gqe-generative-eigensolver) · 教程：[GQE Nakaji H₂](/tutorial/gqe-nakaji-h2) · [GQE 变体](/tutorial/gqe-variants)。

**QPE demo 包**：见下文「qpe_qec_demo 侧车」· 算法页 [QPE](./quantum/algorithms/qpe) · 教程 [QPE track](/tutorial/qpe-track)。

---

## 1. 文献与角色

| 能力 | 角色 |
|------|------|
| **GQE** | 生成式本征求解 sidecar；**顶层 `gqe:` 块**，不是 `quantum.algorithm` |
| **TKET** | 电路 IR / peephole 统计与闭包描述 |
| **Nexus** | 可选安装探测、工作流蓝图、analog/cloud 账本 |
| **L3** | 能量 bootstrap CI stub 等对标统计 |

integrations **不是**内核；算法层勿 import 重型胶水。

---

## 2. 理论

GQE 用生成模型提出候选，再经能量评估筛选，目标仍是近似基态：

$$
E \approx \min_{\alpha\sim p_\phi} \langle \psi_\alpha | H | \psi_\alpha \rangle
$$

TKET / Nexus / L3 提供**对照与能力面**，默认不改变主变分数学路径。

---

## 3. 实现

### GQE

| 项 | 路径 |
|----|------|
| 配置 | `config/gqe.py` → `GqeSpec` |
| 入口 | `integrations/gqe/api.py` → `run_gqe_from_config` |
| 编排钩子 | `pipeline_stage_runners._maybe_run_gqe_stage`（`gqe.enabled`） |
| 蓝图 / probe | `blueprint.py`、`probe_jax.py`、`probe_cudaq.py` |
| Schema | `GQE_TRAIN_REPORT_V1`、`GQE_BLUEPRINT_V1`、`GQE_PROBE_V1` 等 |

`gqe.skip_variational` 时可跳过主变分。训练细节见深读页。

### TKET

| 入口 | 路径 |
|------|------|
| `describe_tket_closure_layer` | `integrations/tket_fullchain.py` |
| `circuit_ir_to_tket_stats_or_none` | 同上 |
| `circuit_ir_tket_peephole_optimize_stats_or_none` | 同上 |
| IR 桥 | `backends/pytket_bridge.py` |

YAML：`parity_integrations.tket_first_circuit_stats` → repro `parity_snapshot` 探针。

### Nexus

| 入口 | 路径 |
|------|------|
| `probe_qnexus_installation` | `integrations/nexus_optional.py` |
| `nexus_public_workflow_blueprint` | 同上 |
| 配置 | `nexus_analog`、`nexus_cloud`（`config/nexus.py`） |
| 作业账本 | `jobs/nexus_analog.py`、`jobs/nexus_cloud.py` |

### L3 benchmarks

| 入口 | 路径 |
|------|------|
| `energy_bootstrap_ci_stub` | `integrations/l3_statistics_reference.py` |
| Schema | `L3_ENERGY_BOOTSTRAP_STUB_V1` |

其他：`schmidt_per_fragment_vqe`、`gap_closure_bundle`、`open_driver_surface`、`qermit_reference`、`tensornet_closure`。

---

## 4. YAML

**GQE 必须写在顶层**（勿写成 `quantum.algorithm: gqe`）：

```yaml
schema_version: "2"
# … molecule / scf / active_space / quantum / backend …
gqe:
  enabled: true
  mode: native          # 以 GqeSpec 为准
  train_mode: demo
  skip_variational: false
  epochs: 2
  # molecule / bond_angstrom / loss / … 见 config.gqe
parity_integrations:
  tket_first_circuit_stats: false
  tensornet_closure_reference: false
nexus_analog: {}
nexus_cloud: {}
```

代表：`configs/example_h2_gqe_condition.yaml` 等。

---

## 5. Python

```python
from qchem_stack.sdk import workflow_preview_payload, load_experiment_config
from qchem_stack.integrations.gqe import run_gqe_from_config  # 或 integrations.gqe.api

cfg = load_experiment_config("configs/example_h2.yaml")
preview = workflow_preview_payload(cfg)
print(sorted(preview.keys())[:6])

# GQE：需启用 gqe 的配置
# report = run_gqe_from_config(cfg)
```

TKET / L3：

```python
from qchem_stack.integrations.tket_fullchain import describe_tket_closure_layer
from qchem_stack.integrations.l3_statistics_reference import energy_bootstrap_ci_stub

print(describe_tket_closure_layer())
```

---

## 6. 验证

```bash
python3 -c "from qchem_stack.sdk import workflow_preview_payload; from qchem_stack.config import load_experiment_config; p=workflow_preview_payload(load_experiment_config('configs/example_h2.yaml')); print(sorted(p.keys())[:6])"
```

期望：preview 顶层键片段。

```bash
python3 -c "from qchem_stack.config import load_experiment_config; from qchem_stack.config.gqe import GqeSpec; c=load_experiment_config('configs/example_h2.yaml'); print(hasattr(c, 'gqe'), type(c.gqe).__name__)"
```

期望：`True GqeSpec`（确认顶层块存在）。

---

## 7. 调优建议

- GQE 与主 VQE 资源竞争时设 `skip_variational` 或缩短 `epochs`。  
- TKET/Nexus 探针默认关；对标实验再开，避免污染基线 `repro`。  
- L3 stub 仅统计参考，非生产不确定度 SLA。  
- 细节参数以 [GQE 深读](./quantum/algorithms/gqe) 为准。

---

## 8. qpe_qec_demo 侧车

包路径：`qchem_stack.qpe_qec_demo`（与 `quantum.algorithms.qpe` 配合的 **Methods / demo sidecar**，不是生产 FT 编译器）。

| 符号 | 作用 |
|------|------|
| `BayesianQPEStub` | 玩具 Bayesian 相位 MAP（schema `bayesian_qpe_stub_map_v1`） |
| `kitaev_qpe_energy_estimate` | 稠密 Kitaev 能量捷径 |
| `pipeline_track.qpe_demo_track_payload` | 组装 demo track 字典供 pipeline 挂载 |
| `FaultTolerantDemoAdapter` | FT 演示适配占位 |

典型配置标志：YAML 中的 `demo_track_n_bits` 等（见 `example_h2_qpe_track.yaml`、`example_h2_qpe_main.yaml`、`qpe_dual_track_demo.yaml`）。编排在 `protocol_finalize` 阶段经 `attach_qpe_demo_track_if_requested` 挂载。

```bash
python3 -c "
from qchem_stack.qpe_qec_demo import BayesianQPEStub
print(BayesianQPEStub().estimate([(0.0, 0.5), (1.0, 1.0)])['schema'])
"
```

期望：`bayesian_qpe_stub_map_v1`。

---

## 9. 相关

- **深读**：[GQE](./quantum/algorithms/gqe) · [QPE](./quantum/algorithms/qpe)
- [quantum](./quantum/) · [orchestration](./orchestration) · [jobs](./jobs) · [tensornet](./tensornet)
