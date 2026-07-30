---
title: repro 模块
description: out['repro'] 键、repro_json_dumps 与 ReproExportError。
---

# repro 模块

`qchem_stack.repro` 保证 `repro` 字典可安全序列化为 RFC JSON，无静默类型丢失。选型：[parity / repro 契约](/guide/parity-repro-contract)。

---

## 1. 文献与角色

| 角色 | 说明 |
|------|------|
| 写入方 | 编排 `collect_repro_metadata`、`attach_run_summary`、finalize sidecars |
| 导出方 | `repro_json_dumps` / HTTP `GET /v1/runs/{id}/repro` |
| 消费者 | 对标、审计、MD/ML 附着、作业结果存档 |
| 教程 | [读 repro 键](/tutorial/read-repro-keys) |

`repro` 是「这次跑了什么、用了什么、结果摘要」的机器可读账本。

---

## 2. 理论

对合法 `repro` 对象 $R$：

$$
\mathrm{json.loads}(\mathrm{repro\_json\_dumps}(R)) \equiv \mathrm{JSON\text{-}native}(R)
$$

拒绝：非有限浮点、循环引用、不可序列化类型 → 抛 `ReproExportError`（`qchem_stack.exceptions`）。`allow_nan=False`。

---

## 3. 实现

### `out["repro"]` 核心键

来自 `orchestration/repro_metadata.py` 等：

| 键 | 含义 |
|----|------|
| `experiment_id` | 实验 id |
| `random_seed` | 种子 |
| `config_sha256_prefix` | 配置摘要前缀 |
| `config_path` | 配置路径 |
| `python` / `packages` | 解释器与包版本 |
| `classical_software_versions` / `pyscf_version` | 经典栈版本 |
| `embedding_config` | 嵌入快照 |
| `chemistry_extended_config` | 扩展化学 |
| `nexus_analog_config` / `nexus_cloud_config` | Nexus |
| `parity_snapshot` | 对标快照（可再 patch） |
| `workflow_preview_v1` | 工作流预览 |
| `workflow_preview_variational_execution_v1` | 变分执行预览（可选） |
| `workflow_preview_vqs_track_v1` / `workflow_preview_qpe_track_v1` | 侧车预览（可选） |

### 管线过程中追加

| 键 | 何时 |
|----|------|
| `run_context` | pre_quantum `post_run` |
| `run_summary` | `attach_run_summary` / 阶段失败记录 |
| `pipeline_profile` | protocol finalize |
| `embedding_workflow` | 自 `out` 拷贝 |
| `qmef_ml_attachment_v1` | `md_ml_export.attach_single_frame_to_repro` |

`parity_snapshot` patch 示例：`pre_quantum_build_cache_v1`、`active_space_exporters_registry_v1`、`pre_quantum_branch_registry_v1`、`pre_quantum_handoff_v1`。

类型形状：`repro/schema.py`（`ParitySnapshotV1`、`RunSummaryV1`、`PipelineProfileV1` 等）。

### 导出 API

| 符号 | 路径 |
|------|------|
| `repro_dict_for_strict_json(repro)` | `repro/export.py` |
| `repro_json_dumps(repro, *, indent, ensure_ascii)` | 同上 |
| `ReproExportError` | `exceptions.py` |

公开：`repro/__init__.py`、SDK re-export。

---

## 4. YAML

无独立 `repro:` 块。影响附着的配置：

```yaml
schema_version: "2"
random_seed: 0
experiment_id: h2_demo
md_ml_export:
  attach_single_frame_to_repro: true
  energy_reference: variational
parity_integrations:
  # 探针开关会影响 parity_snapshot 内容
  tket_first_circuit_stats: false
```

---

## 5. Python

```python
from qchem_stack.sdk import run_pipeline_from_config, repro_json_dumps
from qchem_stack.repro.export import repro_dict_for_strict_json
from qchem_stack.exceptions import ReproExportError

out = run_pipeline_from_config("configs/example_h2.yaml")
repro = out["repro"]
print(sorted(k for k in repro if isinstance(k, str))[:12])
try:
    payload = repro_json_dumps(repro)
    print(payload[:120])
except ReproExportError as e:
    print("export failed", e)
```

---

## 6. 验证

```bash
python3 -c "from qchem_stack.sdk import run_pipeline_from_config, repro_json_dumps; o=run_pipeline_from_config('configs/example_h2.yaml'); s=repro_json_dumps(o['repro']); assert s.startswith('{'); print(len(s), 'run_summary' in o['repro'])"
```

期望：退出码 `0`；正整数长度；`run_summary` 多为 `True`。

```bash
python3 -c "from qchem_stack.exceptions import ReproExportError; from qchem_stack.repro.export import repro_json_dumps; 
try:
  repro_json_dumps({'x': float('nan')})
except ReproExportError as e:
  print(type(e).__name__)"
```

期望：打印 `ReproExportError`。

---

## 7. 调优建议

- **禁止** `json.dumps(repro, default=str)`。  
- 存档前先 `repro_json_dumps`；失败即修数据，勿吞异常。  
- 对标只依赖 `parity_snapshot` 稳定键 + [contracts](./contracts) schema id。  
- 大轨迹用 `md_ml_export` / QMEF，勿把整段 MD 塞进 `repro` 主体。

---

## 8. 相关

- [orchestration](./orchestration) · [protocols](./protocols) · [jobs](./jobs) · [api-sdk](./api-sdk)  
- [md-bridge](./md-bridge) · [contracts](./contracts)
