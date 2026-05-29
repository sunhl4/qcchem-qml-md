# MD/ML Export 配置（`md_ml_export` 节）

控制 pipeline 完成后是否附加 QMEF 数据集块，供 `md_bridge` 与 QML-FF 在线学习使用。

## 字段

| 字段 | 说明 |
|------|------|
| `enabled` | 为 true 时在 `repro` 中写入 `qmef_ml_attachment_v1` |
| `include_forces` | 是否请求力/梯度（依赖 labeling 路径） |
| `label_energy_reference` | `variational` / `scf` / `full_pipeline` 等 |
| `trajectory_export` | 是否导出扩展 XYZ 轨迹块 |

## 示例（UQC mock + MD/ML）

见 [`configs/example_h2_uqc_mock_md_ml.yaml`](../configs/example_h2_uqc_mock_md_ml.yaml)。

## 相关文档

- [`qmlff_md_integration_说明.md`](qmlff_md_integration_说明.md)
- [`说明_UQC_mock与分子力场在线学习.md`](说明_UQC_mock与分子力场在线学习.md)
- Docusaurus：[MD/ML 主动学习教程](../docusaurus-site/docs/tutorial/md-ml-active-learning.md)

## 代码入口

- `qchem_stack.md_bridge.from_pipeline` — pipeline `out` → QMEF attachment
- `qchem_stack.md_bridge.run_md_validation_loop` — 多轮 MD + 标注 + 训练
