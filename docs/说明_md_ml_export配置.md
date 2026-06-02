# MD/ML Export 配置（`md_ml_export` 节）

控制 pipeline 完成后是否附加 QMEF 数据集块，供 `md_bridge` 与 QML-FF 在线学习使用。

## 字段（`ExperimentConfig.md_ml_export`）

| 字段 | 说明 |
|------|------|
| `attach_single_frame_to_repro` | 为 true 时在 `repro` 中写入 `qmef_ml_attachment_v1` |
| `energy_reference` | `variational` / `scf` / `pauli_protocol` — 主帧能量来源 |
| `include_hf_nuclear_gradient` | 是否附加 HF 解析力（与 `energy_reference` 非 scf 时可能不一致，见警告） |
| `trajectory.extra_coordinates_bohr` | 额外几何（Bohr） |
| `trajectory.theory_level` | `hf_scf` / `full_pipeline` — 额外几何的标注级别 |

## MD 验证环（独立 loop YAML）

`MdValidationLoopConfig` 字段见 `md_loop_config.py`：

| 字段 | 说明 |
|------|------|
| `label_energy_reference` | 训练标注能量参考 |
| `validation_energy_reference` | \|ΔE\| 评分参考（默认继承 label） |
| `validation_theory_level` | 验证轮 pipeline 级别（默认 `label_top_theory_level`） |

**契约**：`validate_loop_energy_consistency()` 在 `run_md_validation_loop` 启动时检查 loop 与 experiment YAML 的 `energy_reference` 对齐。

## 示例

- Pipeline attachment：[`configs/example_h2_uqc_mock_md_ml.yaml`](../configs/example_h2_uqc_mock_md_ml.yaml)
- 主动学习环：[`configs/example_h2_uqc_mock_qmlff_loop.yaml`](../configs/example_h2_uqc_mock_qmlff_loop.yaml)

## 相关文档

- [`qmlff_md_integration_说明.md`](qmlff_md_integration_说明.md)
- [`在线学习云上调度.md`](在线学习云上调度.md) §7–§8（能量参考一致性）
- Docusaurus：[MD/ML 主动学习教程](../docusaurus-site/docs/tutorial/md-ml-active-learning.md)

## 代码入口

- `qchem_stack.md_bridge.from_pipeline` — pipeline `out` → QMEF attachment
- `qchem_stack.md_bridge.energy_reference` — 语义校验
- `qchem_stack.md_bridge.run_md_validation_loop` — 多轮 MD + 标注 + 训练
