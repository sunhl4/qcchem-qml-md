# Parity export schema 版本（D79）

**顶键**：`scripts/export_parity_criteria_table.py` 输出字段中的 **`parity_export_schema_version`**（当前 **`"3"`**，与 `PARITY_EXPORT_V3_STABLE_KEYS` 对齐）。

| 版本 | 含义 | 兼容约定 |
|------|------|-----------|
| `3` | config-only 稳定键集合 `PARITY_EXPORT_V3_STABLE_KEYS`（`qchem_stack.protocols.product_contract`） | `scripts/check_parity_export_sample.py` 断言；bump 时需同步黄金样例（若结构变化） |

**与包版本**：Python 包 `qchem_stack.__version__`（`pyproject.toml`）与 export schema **独立** bump；论文 Methods 可同时钉二者。
