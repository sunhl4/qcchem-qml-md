# Day91+ Next Phase Plan (2026Q3)

角色：承接 2026Q2 Day12–Day90 收口后的下一阶段执行计划（P2 深化）。

## 目标

- 在不越过 L0 边界的前提下，把 P2 残余项继续推进到“可发表 + 可回归 + 可审计”。

## 工作包与节奏（建议 6 周）

### Week 1–2：P2-W1 深化（资源估计叙事）

- 在 `resource_estimation_preview_v1` 上扩展深度字段（保持非云计价口径）。
- 同步更新：
  - `src/qchem_stack/protocols/product_contract.py`（**`qchem_stack.protocols.product_contract`**：[CONTRIBUTING](../../CONTRIBUTING.md#product-contracts-and-workflow-preview-stable-imports)）
  - `scripts/export_parity_criteria_table.py`
  - `tests/test_methods_resource_unified_export.py`
- 交付：新增字段的 config-only 与 `--results` 双路径测试。

### Week 3–4：P2-W3 + W4（经典边界 + 缓解进阶）

- W3：保持 AVAS/CASSCF `partial` 边界，不做闭源等价宣称。
- W4：补一条 mitigation 进阶块（优先 ZNE 变体）。
- 同步更新：
  - `docs/mitigation_PMSV_ZNE_Qermit_mapping.md`
  - `docs/public_parity_matrix.md`
  - 相关 run summary / export 镜像测试。

### Week 5–6：P2-W7 与发布前收口

- 扩充 docusaurus-site 与 examples 的索引闭环（新用户三路径）。
- **算法 L3 可选门禁**：设置 `QCHEM_RUN_L3=1` 时跑 `pytest -m l3`（**7** 条代表配置：基线 **`example_h2.yaml`**（VQE）+ ADAPT singles/doubles、**ADAPT `uccsd_jw` 别名**、IQEB fermionic doubles、**IQEB `qubit_excitation` 别名**、excited-smoke），见 [`tests/test_l3_benchmark_smoke.py`](../tests/test_l3_benchmark_smoke.py)；汇总 JSON 可跑 `python scripts/l3_algorithm_benchmark_report.py`（可选 `--merged`）。
- 做一轮总闸：
  - `pytest`
  - `python scripts/check_parity_export_sample.py`
  - 文档/contract/矩阵一致性复核。

## 验收闸门

1. 新增键均在 contract 注册。  
2. 导出脚本可稳定输出并有测试覆盖。  
3. parity 抽样脚本覆盖新增代表 YAML。  
4. docs 与 docusaurus-site 同步，无冲突口径。  

## 非目标（保持）

- 不宣称 Quantinuum 云/Nexus/HQC 等商业能力等价。
- 不宣称闭源 Qermit / cuTensorNet L0 等价。
