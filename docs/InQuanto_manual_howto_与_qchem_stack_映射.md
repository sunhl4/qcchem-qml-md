# InQuanto 公开手册「How to use」与 `qchem_stack` 映射

**钉扎文档（维护时对照）**：[How to use InQuanto](https://docs.quantinuum.com/inquanto/manual/howto.html)（站内手册；截图/版本以当时公开页为准）。

**用途**：把对方 **用户指南级** 叙事（算法 ↔ 可计算量 ↔ 协议 ↔ pytket 后端）映射到本仓库**可检证**的模块与 JSON 出口。**不**声称与 InQuanto 闭源包或默认工作流二进制一致；边界见 [竞争定位与路线图_对标Quantinuum产品与技术路线.md](竞争定位与路线图_对标Quantinuum产品与技术路线.md) §4。

---

## 1. Chemistry workflows（手册「算法用 computables；协议执行 computables」）

| 公开叙事要点 | `qchem_stack` 落点 | 机读 / 运维 |
|--------------|---------------------|-------------|
| `Algorithm*` 求解化学量（基态/激发等） | `qchem_stack/quantum/algorithms/`（VQE、ADAPT、IQEB、VQD/QSE/SCEOM 等）；激发态 `run_summary` 见 [工程记忆 §3.1](工程记忆_Quantinuum对标与数据流技术文档.md) | `repro.parity_snapshot` 量子段；`export_parity_criteria_table.py` |
| 符号层 **Computable** + **Protocol** 评估 | `protocols/computable.py`、`protocols/protocol.py`（`PauliAveragingProtocol` 五阶段）；**图预览** `integrations/inquanto_workflow_preview.py` | `POST /v1/meta/workflow-preview`、`POST /v1/meta/computables-preview`；[parity 矩阵 §1](inquanto_public_parity_matrix.md) |
| **pytket** 驱动编译与后端 | 可选：`backends/pytket_bridge.py`、`integrations/tket_fullchain.py`；资源/门集叙事见 [技术文档_CircuitIR与TKET桥接及作业契约.md](技术文档_CircuitIR与TKET桥接及作业契约.md) | `parity_snapshot.tket_first_compiled_circuit_probe`（若启用） |
| 端到端编排 | `orchestration/pipeline.py`、`config.ExperimentConfig` + YAML | `run_pipeline_sync` / `run_pipeline_from_config`；`repro.run_summary` |

---

## 2. Preparing chemical systems（几何、驱动、活性空间）

| 公开叙事要点 | `qchem_stack` 落点 | 备注 |
|--------------|---------------------|------|
| Geometry / drivers / mean-field | `chem/drivers/pyscf_driver.py`、`chem/hamiltonian.py`；扩展 `chemistry_extended`（ddCOSMO、PBC、k 点等） | 名称别名：`src/qchem_stack/chem/inquanto_driver_surface.py` |
| FCIDUMP 互操作 | 以 PySCF 为主路径；FCIDUMP **未**作为一等入口时在 [parity 矩阵 §3](inquanto_public_parity_matrix.md) 标保守 `partial` | |
| Embedding（DMET 等手册分支） | `chem/embedding/`、`integrations/schmidt_dmet_self_consistent.py` 等 | [技术文档_DMET与parity_snapshot开放契约.md](技术文档_DMET与parity_snapshot开放契约.md) |

---

## 3. Spaces, operators, states, mappings（费米子 → Pauli）

| 公开叙事要点 | `qchem_stack` 落点 |
|--------------|---------------------|
| Fermionic space / qubit mapping | `chem/fermion.py`、`chem/hamiltonian.QubitHamiltonian`；JW 等见 Hamiltonian `meta` |
| Ansatz / HEA / UCC 家族叙事 | `quantum/algorithms/`、`integrations/gap_closure_bundle.py`（UCC 钩子等）；与闭源 **ChemicallyAware** 完整对齐为 `partial` |

---

## 4. Running computables and algorithms（build / run / 结果对象）

| 公开叙事要点 | `qchem_stack` 落点 |
|--------------|---------------------|
| Protocol 上挂缓解 | `mitigation/`、`MitigationSpec`；叙事对照 [mitigation_PMSV_ZNE_Qermit_mapping.md](mitigation_PMSV_ZNE_Qermit_mapping.md) |
| 资源估计 | `backends/spec.py`：`dataframe_circuit_shot_rows` 等 |
| 作业队列（产品向「云 UX」） | **本地类比**：`qchem_stack.api`、`jobs/`；见 [launch_retrieve_nexus_analog.md](launch_retrieve_nexus_analog.md) |

---

## 5. Expert use（自定义映射、pytket 电路、`get_circuit`）

| 公开叙事要点 | `qchem_stack` 落点 |
|--------------|---------------------|
| 自定义 compiler pass / pytket 对象注入 | `config.CompilerSpec`、`backends/compile_passes.py`；可选 pytket 桥接（上文 §1） |
| 真云 / Nexus / HQC | 本栈 **刻意不对齐** 真 Nexus；见 [架构_InQuanto闭源能力闭合与可复现边界.md](架构_InQuanto闭源能力闭合与可复现边界.md) |

---

## 6. 维护约定

- 公开站结构改版时：对照 [howto](https://docs.quantinuum.com/inquanto/manual/howto.html) 侧边栏是否重排；更新本页 **章节标题对齐** 与 [L1_InQuanto_alignment_signoff.md](L1_InQuanto_alignment_signoff.md) 钉扎说明。
- 单一真相顺序不变：**代码键** → `export` / `repro` → [parity 矩阵](inquanto_public_parity_matrix.md) → `inquanto_gap_categories()`。

---

*版本：初版；与 Y1 台账 [InQuanto_Y1_public_alignment_ledger.md](InQuanto_Y1_public_alignment_ledger.md) 的「公开文档周一对照」一致。*
