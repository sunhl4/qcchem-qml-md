# UCCSD Trotter 与导出

本教程演示 UCCSD Trotter 的最小配置思路，以及如何导出用于验收的结果。

## 目标

- 跑通 UCCSD Trotter 配置
- 读取关键摘要与 `repro`
- 使用 parity 导出脚本产出对齐材料

## 前置条件

- 已安装开发依赖：`pip install -e ".[dev]"`
- 可用配置：`configs/example_h2_uccsd_trotter.yaml`

## 关键配置

- 指定 `quantum` 算法相关键
- 配置 `uccsd_trotter_steps`
- 保留 `repro` 与资源行输出

## 运行示例

```bash
python scripts/smoke_pipeline.py --config configs/example_h2_uccsd_trotter.yaml
```

## 导出示例

```bash
python scripts/export_parity_criteria_table.py configs/example_h2_uccsd_trotter.yaml --results out.json
```

## 导出建议

- 导出 `run_summary` 作为对外摘要
- 保留 `repro` 作为追溯证据
- 配合 `export_parity_criteria_table` 做判据对齐

## 验证清单

- 运行成功并返回关键摘要
- `repro` 中保留算法与资源相关键
- 导出脚本执行成功且结果可读

## 下一步

- [repro 关键字段速览](./read-repro-keys)
- [公开契约矩阵](../parity/public-matrix)
