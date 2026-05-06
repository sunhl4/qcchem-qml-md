# UCCSD Trotter 与导出

本教程演示 UCCSD Trotter 配置和结果导出的基本路径。

## 关键配置

- 指定 `quantum` 算法相关键
- 配置 `uccsd_trotter_steps`
- 保留 `repro` 与资源行输出

## 导出建议

- 导出 `run_summary` 作为对外摘要
- 保留 `repro` 作为追溯证据
- 配合 `export_parity_criteria_table` 做判据对齐
