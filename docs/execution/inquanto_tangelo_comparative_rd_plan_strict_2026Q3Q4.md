# InQuanto vs Tangelo 对比研发计划（严格实施版，2026Q3-Q4）

## 1. 目标与边界

- 目标：在现有 `qchem_stack` 基础上，形成可检证的 InQuanto 公开能力对齐，并对 Tangelo 开源能力做可执行广度补齐。
- 边界：不承诺复现闭源运行时、商业云计费、专有硬件校准；仅承诺公开文档/开源源码可证据化对齐。
- 交付：计划文档 + 机器可校验台账 + 代码/测试/导出证据三位一体。

## 2. 外部对照基线（证据）

### InQuanto（公开文档）

- Algorithms 总览（instantiate -> build -> run）：<https://docs.quantinuum.com/inquanto/manual/algorithms_overview.html>
- API 入口与算法类族（VQE/ADAPT/VQD/QSE/SCEOM 等）：<https://docs.quantinuum.com/inquanto/api/inquanto/algorithms.html>
- 官方文档主页：<https://docs.quantinuum.com/inquanto>

### Tangelo（开源）

- 项目仓库：<https://github.com/sandbox-quantum/Tangelo>
- 文档总览：<https://sandbox-quantum.github.io/Tangelo/overview.html>
- 代码与安装说明（README）：<https://raw.githubusercontent.com/sandbox-quantum/Tangelo/main/README.rst>

## 3. 当前仓库能力现状（与计划直接相关）

- InQuanto 对齐主契约：`src/qchem_stack/protocols/inquanto_contract.py`（稳定 import：**`qchem_stack.protocols.inquanto_contract`**；字面量：**`internal_reports/competitor/inquanto_contract.py`** — 见 [CONTRIBUTING](../../CONTRIBUTING.md#parity-and-workflow-preview-stable-imports)）
- HTTP 对齐面：`src/qchem_stack/api/app.py`（`/v1/meta/capability-surface`、`/v1/meta/parity-gaps`）
- 工作流 / Computable：`src/qchem_stack/integrations/inquanto_workflow_preview.py`（**`qchem_stack.integrations.inquanto_workflow_preview`**；字面量 **`internal_reports/competitor/inquanto_workflow_preview.py`**）
- Tangelo 对照点：`src/qchem_stack/chem/fermion_mapping_registry.py`、`src/qchem_stack/quantum/algorithms/excited.py`
- 公开矩阵：`docs/inquanto_public_parity_matrix.md`
- 已有执行链：`docs/execution/day121_day180_inquanto_tangelo_calendar_2026Q3.md`

## 4. 差距优先级（P0 -> P2）

### P0（必须先做）

1. VQD deflation 工程化双路径（statevector overlap 与 circuit-overlap 可切换）
2. ADAPT/IQEB operator pool 广度补齐（含 alias 与导出稳定键）
3. `ChemIntegralSolver` 在 PySCF 路径的 `get_integrals` 可检证闭合

### P1（强建议本周期完成）

1. BK/SCBK 与 UCCSD 语义边界固化（实现或明确 `n/a` 并机读化）
2. Tangelo mapping alias 扩展（含 JKMN/HCB 规划位与显式 non-executable 标注）
3. Mitigation 执行模型补齐（runtime trace + async 语义对照）

### P2（可并行推进）

1. L3 benchmark 样本覆盖扩展（算法/映射/嵌入切面）
2. TensorNet/cutensornet stub 到 optional-demo 的可证据链
3. parity 导出样本 YAML 扩容与 CI 稳定键覆盖

## 5. 实施节奏（60 天）

### 阶段 A（Day121-Day135，基线冻结 + 快速收口）

- 冻结差距清单与锚点：`inquanto_gap_categories()` 与 `capability_surface` 同步
- 完成 P0-1 / P0-2 的最小可测闭环（代码 + 测试 + 导出）

### 阶段 B（Day136-Day155，算法/化学主链对齐）

- 完成 P0-3 + P1-1
- 形成 Tangelo 对照专项报告（映射、VQD、DMET/embedding 接口）

### 阶段 C（Day156-Day180，证据化封板）

- 完成 P1-2 / P1-3 与 P2 关键项
- 封板材料：矩阵更新、回归报告、风险遗留、下一周期 WBS

## 6. 严格实施机制（本计划强制）

1. 所有任务必须登记在台账：`docs/execution/inquanto_tangelo_comparative_backlog.yaml`
2. 每个任务必须绑定：
   - 代码触点（`target_files`）
   - 测试触点（`tests`）
   - 验收标准（`acceptance_criteria`）
3. 已完成任务必须填写 `evidence`，否则校验失败
4. 使用脚本 `scripts/check_inquanto_tangelo_comparative_backlog.py` 校验结构与完成证据
5. 用例 `tests/test_check_inquanto_tangelo_comparative_backlog_script.py` 保障脚本稳定性

## 7. 每周执行与闸门

- 周一：更新台账状态（`todo/in_progress/done/blocked`）并补齐证据链接
- 周三：跑最小闸门（contract + API + parity export + 关键算法测试）
- 周五：发布周报（完成项、偏差项、下周纠偏）

建议最小闸门命令：

```bash
pytest tests/test_inquanto_contract.py tests/test_api_runs.py -q --tb=short
pytest tests/test_fermion_qubit_mapping.py tests/test_excited_qse_hs.py -q --tb=short
python scripts/check_inquanto_tangelo_comparative_backlog.py
```

## 8. 风险与应对

- 可选依赖风险（PySCF/Qiskit/Psi4）：任务定义中区分必测与可选测，避免假失败
- 对齐叙事漂移风险：以 `inquanto_contract` 为单一机读源，文档只能引用不能自定义
- 大规模改动冲突风险：按任务分批提交，优先低耦合切片（registry/export/test）

## 9. 完成定义（DoD）

- 台账任务 `done` 且具备 `evidence`
- 对应测试新增或更新并通过
- `docs/inquanto_public_parity_matrix.md` 与 `capability-surface` 保持一致
- 无新增 lint 错误（至少覆盖改动文件）
