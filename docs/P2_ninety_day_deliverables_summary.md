# 90 日计划交付包摘要（D90）

**计划原文**：用户确认的 Cursor 计划「90 天对标 Vendor platform / 借鉴 Tangelo」（本地 `.cursor/plans/`）；**逐日核对台账**：[`P2_ninety_day_execution_checklist.md`](P2_ninety_day_execution_checklist.md)。

## 闸门最小集合（D15/D30/D45/D60/D69/D76/D82/D88）

```bash
python -m pytest
python scripts/check_parity_export_sample.py
```

可选：`bash scripts/verify_ninety_day_gates.sh`

## 本轮工程增量（相对「仅文档」基线）

- **W3**：`repro.run_summary.classical_active_space_caveat_v1`（AVAS/CASSCF 诚实边界）。  
- **W4**：`mitigation_pec_literature_stub_v1`（文献向 PEC 占位）+ `configs/example_h2_pec_literature_stub.yaml`。  
- **W5/Tangelo**：[`P2_W5_algorithm_registry_alignment.md`](P2_W5_algorithm_registry_alignment.md) §4、[`examples/tangelo_facade_demo.py`](../examples/tangelo_facade_demo.py)。  
- **W7**：[`examples/README.md`](../examples/README.md)、Docusaurus [`tutorial-index-three-paths.md`](../docusaurus-site/docs/tutorial/tutorial-index-three-paths.md)、分解教程页。  
- **回归**：[`scripts/sample_pipeline_configs.py`](../scripts/sample_pipeline_configs.py)（抽样 10 YAML）、[`tests/test_computable_roundtrip_minimal.py`](../tests/test_computable_roundtrip_minimal.py)、HTTP workflow-preview 异常单测。

## 下一阶段（M-P2-c/d）

见 [`P2_详细实施计划.md`](P2_详细实施计划.md) §4 里程碑表；残余 `partial` 维护 [`Y1_residual_partial_SLA_template.md`](Y1_residual_partial_SLA_template.md)。
