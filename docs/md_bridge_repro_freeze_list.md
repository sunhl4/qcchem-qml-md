# MD/ML：`QMEFDataset` / `QMFrame` 与 `repro` 对齐冻结清单（P2-W6 起步）

**母稿**：[P2_详细实施计划.md](P2_详细实施计划.md) §6 序 5、§8 第 1–2 周；SLA 行见 [Y1_residual_partial_SLA_template.md](Y1_residual_partial_SLA_template.md)。

**范围**：`l1_md_ml` 契约与导出到扩展 XYZ / stub 训练器；与量子管线 `repro` 全量并集时，下列字段为 **稳定性承诺**（改名须 bump 导出 schema 或显式 major）。

---

## 1. `QMFrame`（Pydantic）

| 字段 | 类型（概念） | 冻结说明 |
|------|----------------|----------|
| `atomic_numbers` | `list[int]` | 与帧一致 |
| `positions_bohr` | `list[list[float]]` | 长度 3，Bohr |
| `energy_hartree` | `float` | Hartree |
| `forces_hartree_bohr` | `list[list[float]]` | 可空列表，与原子数对齐 |
| `charge` | `int` | 默认 0 |
| `multiplicity` | `int` | 默认 1 |
| `box` | `list[float] \| None` | 可选周期盒 |
| `method_tag` | `str` | 自由文本，建议短 token |
| `active_space_hash` | `str` | 与量子侧 active space 摘要对齐用占位 |
| `protocol_hash` | `str` | 与 job / protocol 摘要弱关联 |
| `repro_config_sha256_prefix` | `str` | **对齐** `repro.config_sha256` 类前缀时填写 |
| `backend_noise_tag` | `str` | 噪声 / 后端标签 |

源码：`src/qchem_stack/md_bridge/schema.py`。

---

## 2. `QMEFDataset`

| 字段 | 说明 |
|------|------|
| `frames` | 非空 `list[QMFrame]` |
| `provenance_yaml` | 来源 YAML 片段或路径摘要，便于审计 |

---

## 3. 与量子 `repro` 的衔接（约定）

- 从同一次实验写入 `QMFrame.repro_config_sha256_prefix` 时，应与 `repro.config_sha256` **前缀策略**一致（见 L1 signoff 与 pipeline 元数据）。  
- 新增顶层 `repro` 键不得 shadow MD 侧字段名；若合并 JSON-LD 式导出，使用 **命名空间前缀**（例如 `md_bridge.*`）在 ADR 中另行登记。

---

## 4. 回归

- `pytest -m l1_md_ml`（见 [CONTRIBUTING.md](../CONTRIBUTING.md)）。  
- 代表测：`tests/test_md_bridge.py`。
