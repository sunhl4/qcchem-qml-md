# Day 1 Inventory (2026Q2)

目标：把 **`product_gap_categories()`**（HTTP `gaps` / export `capability_gap_categories`）的残余项映射到本季度可执行目标，作为 90 天实施的固定看板输入。

## 当前 gap 状态快照

| gap.id | status | 本季度处理策略 |
|---|---|---|
| `cloud_nexus` | `analog_v1_plus_adapter` | 维持类比实现；不升格为真云能力。 |
| `http_submit_poll_workspace` | `local_analog_v1` | 稳定 API 契约与队列可观测性，不做厂商鉴权。 |
| `qermit_graph` | `analog_v2_runtime` | 推进进阶 mitigation block，但保持 open analog 边界。 |
| `composable_computable` | `analog_v2_semantic_graph_rich_optional` | 强化 rich 可选路径与 workflow-preview 一致性。 |
| `evaluate_support_set` | `improved_v1` | 维持；仅做回归稳定性与文档对齐。 |
| `compiler_pass_bundle` | `improved_v1` | 维持可选 pytket 路径，不改为硬依赖。 |
| `ucc_chem_ansatz` | `partial_jw_uccsd_and_trotter_packaged_bk_scbk_uccsd_na` | 本季度补 registry/文档/测试，不承诺 BK/SCBK UCCSD Trotter。 |
| `dmet_scf_loop` | `schmidt_density_feedback_v1_plus_hooks_oniom_toy_yaml` | 推进 P2-W2 最小可跑分解路径（plugin/ONIOM）。 |
| `tensornet` | `n_a_no_shipped_l3_chemistry_contraction_reason_open_stack_stub_only_not_vendor_cutensornet` | 维持 `n/a` 诚实降级；不做商业二进制 parity。 |
| `integrations_closure_layer` | `reference_v1` | 维持引用层，防止文档/代码漂移。 |
| `drivers_cosmo_pbc` | `partial_kmesh` | 做边界文档与 driver surface 可检证扩展（P2-W3）。 |
| `qpu_shot_histogram` | `yes_qiskit` | 维持稳定并覆盖更多样例回归。 |

## 90 天内优先收口的高价值项

1. `dmet_scf_loop`：从 toy/钩子走向最小可跑产品路径（P2-W2）。
2. `ucc_chem_ansatz`：补算法与映射叙事一致性（P2-W5）。
3. `qermit_graph`：新增一条进阶 mitigation block（P2-W4）。
4. `drivers_cosmo_pbc`：完成 P2-W3 边界文档 + 测试闭环。

## 冻结规则（执行期间）

- 任一状态变化必须同步三处：`docs/public_parity_matrix.md`、`docs/public_parity_matrix.md`、`src/qchem_stack/protocols/product_contract.py`（**`qchem_stack.protocols.product_contract`**：`product_gap_categories()` 等 — 见 [CONTRIBUTING](../../CONTRIBUTING.md#product-contracts-and-workflow-preview-stable-imports)）。
- 对云/硬件/闭源二进制相关项保持 `n/a` 或 `partial+caveat`，不允许营销式升格。
