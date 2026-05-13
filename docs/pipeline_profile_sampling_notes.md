# Pipeline profile 慢阶段抽样（D48）

**目的**：记录 `repro.pipeline_profile`（`pipeline_profile_v1`）用于运维/METHODS 附录时的读法；**不在此迭代做性能优化承诺**。

- **生成**：`run_pipeline_sync` 内 `PipelineStageTimer`；摘要字段见 `run_summary.pipeline_total_wall_ms`、`pipeline_slowest_stage`。  
- **典型慢段**：PySCF SCF、Schmidt 生产（若启用）、Pauli 编译与分组（大 Pauli 集）。  
- **Issue 模板**：若某 YAML 在 CI 外超时，附件贴 `pipeline_profile.stages` JSON + `experiment_id` + `config_sha256_prefix`。
