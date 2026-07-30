---
title: 自定义变分插件
description: algorithm_factory 完整手册：契约、安全边界、示例与注册。
---

# 自定义变分插件

把用户定义的变分阶段接入与内建 VQE/ADAPT 相同的管线槽位。契约：`VariationalRunContext` → `VariationalStageOutcome`。

实现：`qchem_stack.quantum.variational_plugins`（`registry`、`loader`、`spec`）。

---

## 1. 要解决什么问题

内建算法 ID 不够时，用 **工厂字符串** 加载 runner，仍享受 SCF → pre-quantum → protocol → repro 全链路，无需 fork 编排器。

---

## 2. 契约

Runner 必须返回管线兼容结果：

| 字段 | 要求 |
|------|------|
| `energy` | 浮点基态/变分能量 |
| `angles` | 一维 float 向量（默认可按 HEA 形状；否则在 meta 说明） |
| `algo_meta` / `algorithm_report` | 可选结构化报告 |

加载形态（`load_variational_runner_from_factory`）：

1. 零参插件类，含 `run_variational(ctx)`  
2. 零参工厂 → runner 或实例  
3. 单参可调用 `runner(ctx)`  

解析：`resolve_variational_runner(algorithm, algorithm_factory)` → `run_variational_stage`。

---

## 3. 安全边界

- 工厂模块路径须以 `qchem_stack.` 开头  
- 例外：环境变量 `QCHEM_QUANTUM_ALGORITHM_FACTORY_ALLOW_EXTERNAL=1`  
- 内建插件 ID 不可注销  
- 未知 `quantum.algorithm` 且无 factory → `PipelineError`

---

## 4. YAML

```yaml
quantum:
  algorithm: micro_vqe_yaml_plugin_demo          # 报告用标签
  algorithm_factory: qchem_stack.quantum.variational_plugins.examples.vqe_micro_plugin:micro_vqe_runner_factory
  vqe:
    depth: 1
    maxiter: 40
```

| 配置 | 工厂 |
|------|------|
| `configs/example_h2_micro_vqe_plugin.yaml` | `vqe_micro_plugin:micro_vqe_runner_factory` |
| `configs/example_h2_echo_variational_plugin.yaml` | `echo_runner:echo_runner_factory` |

运行时注册：`register_variational_plugin(...)` + `sync_algorithm_registry_from_variational`。

---

## 5. 函数调用与验证

```python
from qchem_stack.quantum.variational_plugins.registry import run_variational_stage
from qchem_stack.sdk import run_pipeline_from_config

out = run_pipeline_from_config("configs/example_h2_micro_vqe_plugin.yaml")
print(out.get("energy_after_variational"), "algorithm_report" in out)
```

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c=load_experiment_config('configs/example_h2_micro_vqe_plugin.yaml')
print('ok', c.quantum.algorithm_factory)
"
```

---

## 6. 相关

- [算法索引](./) · [orchestration](/modules/orchestration) · [VQE](./vqe-hea)
