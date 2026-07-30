---
title: orchestration 模块
description: 管线阶段 scf→protocol_finalize、run_pipeline_sync/from_config、embedding_workflow 与 pre-quantum。
---

# orchestration 模块

`qchem_stack.orchestration` 串联化学前置、变分、嵌入审计、激发态与 Pauli finalize。算法/驱动**不得**反向 import 编排层。

阶段归属：仓库 `docs/engineering/pipeline_stage_ownership.md`。

---

## 1. 文献与角色

| 角色 | 说明 |
|------|------|
| 调度 | 有序阶段组合，写入结构化 `out`，失败发 `stage.<name>.failed` |
| 入口 | `run_pipeline_sync`、`run_pipeline_from_config` |
| 事件 | `pipeline_events.PipelineEvents` / `get_event_bus` |
| 选型 | [开始使用](/getting-started) · [parity 契约](/guide/parity-repro-contract) |

管线是阶段复合 $\mathcal{S}_1 \circ \cdots \circ \mathcal{S}_n$，不是单文件脚本。

---

## 2. 理论

每个阶段：

1. 发 `started`  
2. 变异 `PipelineSyncContext` / 写入 `out`  
3. 发 `completed` 或 `failed`（并记入 `repro.run_summary`）  

哈密顿量在 **pre_quantum** 固定；变分消费 `qh`；**embedding_workflow** 只做变分后审计，**不替换** `qh`。

---

## 3. 实现：阶段列表

`PIPELINE_STAGE_SPECS`（`orchestration/stage_registry.py`）命名阶段：

| 顺序 | 阶段 | Runner |
|------|------|--------|
| 1 | `scf` | `run_scf_stage_ctx` |
| 2 | `pre_quantum` | `run_pre_quantum_stage_ctx` |
| — | **repro 收集** | `bind_post_pre_quantum_ctx`（`pre_quantum` 的 `post_run`） |
| 3 | `variational` | `run_variational_stage_ctx`（可挂 GQE sidecar） |
| 4 | `embedding_workflow` | `run_embedding_workflow_stage_ctx` |
| 5 | `excited` | `run_excited_stage_ctx` |
| 6 | `protocol_finalize` | `run_protocol_finalize_stage_ctx` |
| — | **可选 `job_enqueue`** | `run_pipeline_from_config(..., job_db=...)` 在 Pauli 启用时入队 |

概念流：

```text
scf → pre_quantum → (repro) → variational → embedding_workflow
    → excited → protocol_finalize → [job_enqueue?]
```

外层包装生命周期：`PIPELINE_WRAPPER_LIFECYCLE`（`pipeline` started/completed/failed）。

### embedding_workflow vs pre-quantum

| | **pre_quantum** | **embedding_workflow** |
|--|-----------------|------------------------|
| 时机 | 变分前 | 变分后 |
| 目的 | 构建/固定 `QubitHamiltonian` | 嵌入审计 / sidecar |
| 输出 | `out["pre_quantum_input"]` | `out["embedding_workflow"]` |
| 对 `qh` | **定义** 变分哈密顿 | **不替换**（`post_variational_embedding_audit_only`） |
| 路径选择 | `resolve_pre_quantum_path` | DMET / projection / plugin / none |

### 入口

| 函数 | 行为 |
|------|------|
| `run_pipeline_sync(cfg, *, cfg_path, run_context, …)` | 进程内完整管线 |
| `run_pipeline_from_config(cfg_path, *, job_db, enqueue_only, run_context)` | 加载 YAML + sync；可选 Pauli 作业 |
| `run_pipeline_async` / `run_pipeline_batch_async` | 线程池包装 |

实现：`pipeline.py` → `pipeline_sync_runner.py`。

---

## 4. YAML

编排本身几乎无独立块；行为由 `ExperimentConfig` 各 section 决定。影响阶段开关的典型键：

| 键 | 影响 |
|----|------|
| `scf` / `active_space` / `embedding` | SCF + pre_quantum 路径 |
| `quantum` / `gqe` | variational（GQE 可 `skip_variational`） |
| `excited.*` | excited 阶段 |
| `quantum.pauli.use_protocol` | protocol_finalize 深度 |
| `md_ml_export.attach_single_frame_to_repro` | finalize sidecar |

```yaml
schema_version: "2"
# … molecule / scf / active_space / quantum / backend …
```

---

## 5. Python

```python
from qchem_stack.orchestration.pipeline import (
    run_pipeline_sync,
    run_pipeline_from_config,
)
from qchem_stack.config import load_experiment_config
from qchem_stack.orchestration.stage_registry import PIPELINE_STAGE_SPECS

print([s.name for s in PIPELINE_STAGE_SPECS])

cfg = load_experiment_config("configs/example_h2.yaml")
out = run_pipeline_sync(cfg)
# 或
out = run_pipeline_from_config("configs/example_h2.yaml")
```

SDK（推荐）：

```python
from qchem_stack.sdk import run_pipeline_from_config, run_pipeline_sync, load_experiment_config
```

可选：`run_context=`、`QCHEM_PIPELINE_PROFILE_MEM=1`（阶段峰值内存）。

---

## 6. 验证

```bash
python3 -c "from qchem_stack.orchestration.stage_registry import PIPELINE_STAGE_SPECS; print([s.name for s in PIPELINE_STAGE_SPECS])"
```

期望：`['scf', 'pre_quantum', 'variational', 'embedding_workflow', 'excited', 'protocol_finalize']`。

```bash
python3 -c "from qchem_stack.sdk import run_pipeline_from_config; o=run_pipeline_from_config('configs/example_h2.yaml'); assert 'repro' in o; print(sorted(o.keys())[:8])"
```

期望：退出码 `0`；`repro` 在结果中。

---

## 7. 调优建议

- 阶段顺序以 `PIPELINE_STAGE_SPECS` 为准，业务代码勿复制调度。  
- 调试哈密顿：只看 `pre_quantum` + `resolve_pre_quantum_path`；勿在 embedding_workflow 找 `qh` 替换。  
- 异步：用 `job_db` 或 HTTP `/v1/runs`，worker 见 [jobs](./jobs)。  
- 失败后先读 `out["repro"]["run_summary"]`。

---

## 8. 相关

- [config](./config) · [chem](./chem/) · [quantum](./quantum/) · [protocols](./protocols)  
- [jobs](./jobs) · [repro](./repro) · [api-sdk](./api-sdk)
