---
title: contracts 模块
description: schema_ids 为 SoT、assert_payload_schema 与版本递增策略。
---

# contracts 模块

`qchem_stack.contracts` 存放机器可读的 schema 标识与共享类型，避免魔法字符串漂移。参考：[parity import 路径](/reference/parity-contract-import-paths)。

---

## 1. 文献与角色

| 角色 | 说明 |
|------|------|
| **SoT** | `contracts/schema_ids.py` 稳定 `*_V1` / `*_V2`；stub 见 `schema_ids_experimental.py`（仍经 `schema_ids` re-export 一版） |
| 消费者 | API meta、repro、parity、激发态资源、作业结果 |
| 校验 | `assert_payload_schema` |
| 类型 | `excited_resource_types`、`rdm_correction_types` 等 |

文档只**引用**常量名，不复制易漂移的字面量副本（除验证示例外）。

---

## 2. 理论

每个导出文档带稳定 schema 字符串 $s\in\Sigma$：

$$
s = \langle\mathrm{name}\rangle\_v\langle n\rangle
$$

例如 `capability_surface_v2`、`pipeline_profile_v1`、`product_surface_v1`。

**字段变更 ⇒ 递增版本**。旧 id 可短期保留（如「一个发布周期」），但新导出必须用新常量。

Parity 另有整型 `parity_export_schema_version: 3`（`PARITY_EXPORT_SCHEMA_VERSION_V3`），与字符串 schema id 并行。

---

## 3. 实现

### schema_ids（SoT）

```python
from qchem_stack.contracts.schema_ids import (
    CAPABILITY_SURFACE_V2,
    PIPELINE_PROFILE_V1,
    PRE_QUANTUM_INPUT_SCHEMA_V1,
    PRODUCT_SURFACE_V1,
    FULL_PIPELINE_JOB_RESULT_V1,
    QERMIT_RUNTIME_V1,
    QMEF_ML_ATTACHMENT_V1,
    DENSE_EXPECTATION_REFERENCE_V1,
)
```

再导出中枢：`contracts/__init__.py`。

### `assert_payload_schema`

```python
from qchem_stack.contracts.validate import assert_payload_schema, schema_field

assert_payload_schema(payload, schema_id, *, field="schema")
# 若 payload[field] != schema_id → ValueError
```

### 稳定性守卫（parity）

- `assert_parity_export_keys_stable`  
- `assert_parity_export_schema_version`  

（`repro/schema.py` 等。）

---

## 4. YAML

本模块无运行时 YAML。契约出现在导出 JSON 的 `schema` 字段，例如：

```json
{
  "schema": "capability_surface_v2"
}
```

实验配置仍要求：

```yaml
schema_version: "2"
```

（实验 schema ≠ contracts payload schema。）

---

## 5. Python

```python
from qchem_stack.contracts.schema_ids import (
    CAPABILITY_SURFACE_V2,
    PRODUCT_SURFACE_V1,
    PIPELINE_PROFILE_V1,
)
from qchem_stack.contracts.validate import assert_payload_schema

print(CAPABILITY_SURFACE_V2, PRODUCT_SURFACE_V1)
payload = {"schema": PRODUCT_SURFACE_V1, "ok": True}
assert_payload_schema(payload, PRODUCT_SURFACE_V1)
```

---

## 6. 验证

```bash
python3 -c "from qchem_stack.contracts.schema_ids import CAPABILITY_SURFACE_V2, PRODUCT_SURFACE_V1; assert CAPABILITY_SURFACE_V2.endswith('v2'); print(PRODUCT_SURFACE_V1)"
```

期望：打印 `product_surface_v1`（或当前常量值）。

```bash
python3 -c "from qchem_stack.contracts.validate import assert_payload_schema; from qchem_stack.contracts.schema_ids import PIPELINE_PROFILE_V1; assert_payload_schema({'schema': PIPELINE_PROFILE_V1}, PIPELINE_PROFILE_V1); print('ok')"
```

期望：`ok`。

---

## 7. 版本递增策略（调优 / 维护）

1. 新增或改动导出字段 → 在 `schema_ids.py` 增加 `*_vN`（$N$ 递增）。  
2. 更新所有生产者、测试与 OpenAPI / 文档引用。  
3. 旧常量保留至迁移窗口结束，再删除。  
4. Parity：改稳定键集合时同步 `PARITY_EXPORT_V3_STABLE_KEYS` 与键稳定测试。  
5. 禁止在业务代码中硬编码与常量不一致的字符串。

---

## 8. 相关

- [protocols](./protocols) · [api-sdk](./api-sdk) · [repro](./repro) · [jobs](./jobs)  
- [parity 契约指南](/guide/parity-repro-contract)
