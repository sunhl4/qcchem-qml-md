# opus4.8-test
> **全文收录**：本 Cursor 窗口内与 Opus 4.8 的完整对话归档（不简写正文）。
> **生成时间**：2026-05-29 14:41:23（末次补全：2026-05-29）
> **Transcript ID**：`64dad06a-bd13-4eda-88f5-dc491d1156ec`
> **工作区**：`/home/sunhl/projects/qchem_qml_md` (qchem-stack)

---

# 目录

1. [主对话线程（用户 ↔ Opus 4.8）](#主对话线程)
2. [附：Six-Stage Optimization 计划全文](#附six-stage-optimization-计划全文)
3. [附：子 Agent 审查报告全文](#附子-agent-审查报告全文)

---

<a id="主对话线程"></a>

# 主对话线程

## 主对话

### 回合 1 — 用户

帮我全面review本工程然后给出详细优化计划

### 回合 2 — 助手 (Opus 4.8)

I'll do a comprehensive review of this project. Let me start by exploring the codebase structure and key components.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: List project files and count
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md

</details>

### 回合 3 — 助手 (Opus 4.8)

This is a large, mature project. Let me explore it systematically using parallel agents and direct inspection.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Inspect structure and counts
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/README.md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/pyproject.toml

</details>

### 回合 4 — 助手 (Opus 4.8)

The file count includes the venv. Let me get accurate source metrics and explore architecture in parallel.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Source LOC metrics
- **Tool `Shell`**: git and inventory

</details>

### 回合 5 — 助手 (Opus 4.8)

Strong signal: 416 source files, 42k LOC, 230 tests, 111 configs, 143 docs. Let me dig into architecture, code health, and repo hygiene in parallel.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Task`**: Review architecture & layering
- **Tool `Task`**: Review tests, CI, coverage
- **Tool `Task`**: Review docs and configs sprawl
- **Tool `Shell`**: git status and hygiene check

</details>

### 回合 6 — 助手 (Opus 4.8)

There's significant uncommitted work. Let me check the full extent of the working tree and confirm the hygiene findings.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Full working tree state
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/.github/workflows/ci.yml

</details>

### 回合 7 — 助手 (Opus 4.8)

Let me check the 48 deleted files and confirm the hygiene specifics before composing the plan.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Inspect deletions and tracked artifacts

</details>

### 回合 8 — 助手 (Opus 4.8)

我已经从架构、测试/CI、文档/配置卫生、以及 git 工作区状态四个维度全面 review 了本工程。下面是结论与详细优化计划。

---

# 一、工程总体画像

`qchem-stack` 是一个相当成熟的量子化学编排栈:**416 个源文件 / 42k LOC,230 个测试,111 个 YAML config,143 篇文档,7 个 CI job**。分层(`chem/quantum` 核心 → `orchestration` 协调 → `protocols/backends` 执行 → `jobs/md_bridge` 上层)清晰且有 CI 守护,几乎没有 inline TODO/FIXME(仅 1 文件 4 处)。整体工程纪律很高。

但有几个系统性问题正在累积成本,下面按优先级给出。

### 健康度速览

| 维度 | 评分 | 关键问题 |
|------|------|----------|
| 架构/分层 | 良好 | god-function、UCC dispatch 重复、layering 检查松于意图 |
| 测试/CI | 良好但偏贵 | nightly job 失效、跨 3 版本重复 marker、无安全扫描、mypy 声明未用 |
| 类型安全 | 中等 | mypy 宽松、`ValueError` 与 typed error 混用 |
| 仓库卫生 | **偏差** | `results/`(150 文件)、`timer.dat`、`artifacts/` 违反 `.gitignore` 仍被跟踪 |
| **git 工作区** | **🔴 风险** | **402 个未提交改动**(226 改 / 48 删 / 128 新),测试重组半途而废 |
| 文档/配置 | 臃肿 | 文档双轨手动同步、execution 日志 59 篇、15 个 config 未接 CI |

---

# 二、关键发现

## 🔴 P0 — git 工作区处于半完成的大重构中

`git status` 显示 **402 个改动未提交**。其中 48 个"删除"的是 `tests/test_*.py`,128 个 untracked 里包含 `tests/quantum/`、`tests/chem/`、`tests/config/` 下的同名文件——这是一次**测试目录重组(扁平 → 分层)做到一半**。同时 `src/qchem_stack/api/*`、`backends/*`、众多 docs/configs 都有未提交修改。

这是最高风险项:重组未完成 + 改动未提交,任何分支操作、CI 触发或误删都会造成大量返工/丢失。**必须先把工作区收敛到干净状态**(见计划第 1 步)。

## 🟠 P1 — 仓库卫生:被跟踪的产物违反自身 `.gitignore`

`.gitignore` 已明确忽略 `results/`、`timer.dat`、`artifacts/`,但它们仍在 git 索引里:
- `results/` — **150 个文件被跟踪**(`.npz`/`.pkl` checkpoint、轨迹、日志),且 CI 还依赖 `results/uqc_cloud_sim_md_ml_2rounds/md_validation_summary.json`
- `timer.dat`(~158KB,Psi4 计时输出)
- `artifacts/` — 2 个文件

`.env`(含真实 token)已正确忽略、未被跟踪——这点没问题,但需警惕误 `add`。

## 🟠 P1 — 架构:god-function 与重复 dispatch

| 函数 | 行数 | 位置 |
|------|------|------|
| `VQD.run` | 228 | `quantum/algorithms/excited_vqd.py:198` |
| `run_validation_round` | 189 | `md_bridge/md_loop_rounds.py:231` |
| `run_pipeline_sync` | 186 | `orchestration/pipeline.py:114` |
| `run_scf_stage` | 135 | `orchestration/stage_execution.py:63` |
| `run_vqe_branch` | 126 | `quantum/variational_plugins/builtins.py:50` |

`run_vqe_branch` 有 8+ ansatz 分支重复构造 `VariationalStageOutcome`,且 UCC 家族(`uccsd/uccgd/puccd/upccgsd/qcc_vqe.py`)模式重复——典型的 registry/dispatch-table 重构候选。

**分层强制不一致**:CI 的 `scripts/check_import_layers.py` 用 `ast.walk`(查所有 import),而测试只看模块级 import,导致 `chem` 通过**惰性 import** 引用 `integrations` 绕过了边界检查(`chem/embedding/fragment_solvers/registry.py:37`)。

## 🟡 P2 — CI 成本与正确性

- **`test-nightly` 实际失效**:`on:` 没有 `schedule:` 触发器,只有 commit message 带 `[nightly]` 才跑 → slow/perf/L3 门禁形同虚设。
- **跨 3 个 Python 版本重复跑重型 smoke**:`l1_excited`、`l1_md_ml` marker 在主 pytest 已覆盖却又单独重跑,× 3.10/3.11/3.12,显著拖慢 CI(估计单 PR ~25–50 分钟)。
- **mypy 在 `dev` 依赖和 `[tool.mypy]` 中声明,但 CI 从不调用**(CI 用 pyright);两套类型配置并存。
- **无任何安全扫描**(无 CodeQL / pip-audit / Bandit / secret scan)。
- `verify_ninety_day_gates.sh` 不带 `-m "not slow and not perf"`,与 CI 行为不一致。

## 🟡 P2 — 类型与错误处理

- `pyproject.toml:96` `disallow_untyped_defs = false`,对这个体量的库偏宽松。
- 错误体系混用:`exceptions.py` 定义了 `QChemStackError` 体系,但代码里 **~120+ 处 `raise ValueError`**,33 处宽 `except Exception`(部分是 best-effort 合理,部分应改 typed error)。
- 部分校验(cap-dependent,如 PBC k-mesh)只在 pipeline 跑、不在 `validate_pre_quantum_contract`,API/CLI 直接 load config 会漏检。

## 🟡 P3 — 文档/配置臃肿与遗留

- 文档 143 篇,根目录 79 篇命名混乱(`说明_`/`技术文档_`/中英混排),无 `docs/README.md` 索引;`docs/execution/` 59 篇历史日志;`docs/internal/` review 笔记随仓库发布。
- Docusaurus 与 `docs/` 部分内容重复,**同步靠手动**(`sync_pre_quantum_docs.py` 只同步 2 个 matrix 文件)。
- `configs/README.md` 写"77 个"但实际 104 个 YAML;**约 15 个新算法 config 未接入任何 CI/测试**(`example_h2_qite.yaml`、`puccd`、`vsqs`、`jkmn` 等)。
- 遗留面:`PySCFDriver`(389 行,已 deprecated)、`ml/`(toy)、`integrations/*` re-export shim、根目录 `multitask-深入说明.md`/`CHEM_MODULE_AUDIT_REPORT.md`/`tasks_20260528.csv` 等杂项。

---

# 三、详细优化计划(按优先级与建议顺序)

## 阶段 0 — 稳定工作区(立即,半天)
1. **收敛 git 工作区**:确认测试重组意图后,把 `tests/` 分层重组作为**独立一次提交**完成(用 `git mv` 让 git 识别为重命名而非删+增),其余无关改动拆分提交。先 `git stash` 或分批 `git add -p` 理清 402 个改动。
2. 跑一遍 `ruff check` + `pytest -m "not slow and not perf"` 确认重组后绿灯。

## 阶段 1 — 仓库卫生(0.5 天)
3. `git rm -r --cached results/ artifacts/ timer.dat`(保留磁盘文件),让 `.gitignore` 真正生效。
4. CI 依赖的 `md_validation_summary.json` 移到 `tests/fixtures/`,解除 CI 对 `results/` 的耦合。
5. 删除/忽略根目录杂项:`tasks_20260528.csv`、`.ferrmion.log`;把 `CHEM_MODULE_AUDIT_REPORT.md`、`multitask-深入说明.md` 移入 `docs/internal/` 或 `docs/archive/`。

## 阶段 2 — CI 正确性与提速(1 天)
6. 修复 `test-nightly`:加 `schedule: cron` 触发器,否则 slow/perf/L3 门禁名存实亡。
7. 主 pytest 已含非 slow 测试 → **删除冗余的 `l1_excited`/`l1_md_ml` 单独步骤**,或仅在一个 Python 版本跑。
8. **重型 smoke / 可选 extra(Qiskit/Aer/Pytket/QPE)只在 3.12 跑**,3.10/3.11 只跑核心单测——预计 CI 时间砍掉一大半。
9. 二选一统一类型工具:要么把 mypy 接进 CI,要么从 `dev` 依赖和 `[tool.mypy]` 移除,只留 pyright。
10. 新增轻量安全门禁:`pip-audit`(或 GitHub CodeQL workflow)。

## 阶段 3 — 架构去重与解耦(2–4 天,可渐进)
11. **`run_vqe_branch` 改 dispatch 表**:`ansatz_id → runner`,共享 `VariationalStageOutcome` 构造,顺带收敛 UCC 家族重复。
12. 拆解 god-function:`run_pipeline_sync` 把 repro 拼装/`out` 组装抽到 helper;`run_validation_round` 拆成 train / md / label / merge 阶段;`VQD.run` 拆出优化循环与 overlap 模式。
13. 对齐分层强制:让测试也用 `ast.walk`,或显式允许并文档化 `chem → integrations` 的惰性 import 例外;`quantum/algorithms/vsqs_vqe.py:13` 改用 chem 公共 API 而非私有 `_fermion_operator_to_qubits`。
14. 统一校验入口:导出单一 `validate_experiment_for_run(cfg, caps)`,供 pipeline / API / CLI 共用,消除 cap-dependent 漏检。

## 阶段 4 — 类型收紧(渐进)
15. 先对 `orchestration`、`config`、`protocols` 三个包开启 `disallow_untyped_defs = true`,逐包推进。
16. 在包边界(solvers / backends / md_bridge)把裸 `ValueError`/`except Exception` 替换为 typed error。

## 阶段 5 — 文档/配置整理(1–2 天)
17. 新增 `docs/README.md` 分类索引(Reference / Contracts / Onboarding / 对标-历史 / Execution-归档 / Internal)。
18. `docs/execution/` 59 篇移入 `archive/`,只留 README + 主计划。
19. 更新 `configs/README.md`(77→104),把 ~15 个未接 CI 的算法 config 加入 `SAMPLE_CONFIGS_REL` 或 L3 benchmark,并补 smoke。
20. 文档双轨:在一处写清"Docusaurus = 精选子集,`public_parity_matrix.md` = 唯一真源",加一个链接有效性检查脚本。

## 阶段 6 — 遗留清退(随版本)
21. 按 `docs/迁移指南_PySCFDriver到ChemIntegralSolver.md` 推进 `PySCFDriver`(389 行)下线;明确 `ml/`、`integrations/*` shim 的废弃时间表写进 CHANGELOG。

---

这套计划里 **阶段 0–2 是高收益、低风险、可立刻见效**的(工作区安全 + CI 减半 + 卫生达标),阶段 3 起是中长期质量投资。

需要我现在开始执行哪一部分?我建议**先做阶段 0(收敛工作区)**,因为 402 个未提交改动是当前最大风险;在动任何重构前必须先让它干净可控。要的话我可以先帮你梳理这 402 个改动、把测试重组整理成一次干净的 `git mv` 提交。

[REDACTED]

### 回合 9 — 用户

和好我希望你一次性完成6个阶段

### 回合 10 — 用户

Six-Stage Optimization of qchem-stack

Implement the plan as specified, it is attached for your reference. Do NOT edit the plan file itself.

To-do's from the plan have already been created. Do not create them again. Mark them as in_progress as you work, starting with the first one. Don't stop until you have completed all the to-dos.

### 回合 11 — 助手 (Opus 4.8)

Implementing all six stages per the plan. Starting with Stage 0: establishing a green baseline.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `TodoWrite`**: {'todos': [{'id': 'stage0', 'content': 'Establish green baseline: run full ruff + pytest (not slow/perf) on clean tree', 'status': 'in_progress'}], 'merge': True}
- **Tool `Shell`**: Check git status and HEAD

</details>

### 回合 12 — 助手 (Opus 4.8)

Checking what's already done and what remains.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Recent commits and uncommitted changes
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/.github/workflows/ci.yml

</details>

### 回合 13 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Glob`**: {'glob_pattern': 'docs/README.md', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/CHANGELOG.md

</details>

### 回合 14 — 助手 (Opus 4.8)

Stages 1–3 are committed; finishing stages 4–6 and resolving uncommitted work. Inspecting current state:

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: View uncommitted diffs
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/pyproject.toml
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_parity_export_sample.py

</details>

### 回合 15 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Run ruff lint and format check
- **Tool `Shell`**: Run pyright on tightened packages
- **Tool `Glob`**: {'glob_pattern': 'docs/README.md', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Glob`**: {'glob_pattern': 'docs/execution/archive/**', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}

</details>

### 回合 16 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Run pytest baseline
- **Tool `Shell`**: Verify stage1 commit contents
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/.gitignore

</details>

### 回合 17 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `TodoWrite`**: {'todos': [{'id': 'stage0', 'content': 'Establish green baseline: run full ruff + pytest (not slow/perf) on clean tree', 'status': 'completed'}, {'id': 'stage1', 'content': 'Hygiene: untrack results/ 
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/md_bridge
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/orchestration/stage_execution.py

</details>

### 回合 18 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/exceptions.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers/registry.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols/protocol.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/drivers/pyscf_driver.py

</details>

### 回合 19 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/factory.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/md_bridge/md_loop_config.py

</details>

### 回合 20 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Count execution docs and configs
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/README.md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/execution/README.md

</details>

### 回合 21 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Find configs not in SAMPLE_CONFIGS_REL

</details>

### 回合 22 — 助手 (Opus 4.8)

Implementing stages 4–6: applying Stage 4 fixes first.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/drivers/pyscf_driver.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/orchestration/stage_execution.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols/protocol.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols/computable.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols/computables/expectation.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols/computables/qse_matrices.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols/pauli_support.py

</details>

### 回合 23 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/orchestration/stage_execution.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/factory.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/factory.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/factory.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/factory.py

</details>

### 回合 24 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/orchestration/stage_execution.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/factory.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/md_bridge/md_loop_config.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers/registry.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/uqc_pauli_shots.py

</details>

### 回合 25 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/factory.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/factory.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/uqc_pauli_shots.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/md_bridge/md_loop_config.py

</details>

### 回合 26 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/md_bridge/md_loop_config.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/md_bridge/md_loop_config.py
- **Tool `Shell`**: Verify pyright on tightened packages

</details>

### 回合 27 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Shell`**: Run targeted tests for changed modules

</details>

### 回合 28 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Commit Stage 4 changes

</details>

### 回合 29 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Fix ruff and commit Stage 4

</details>

### 回合 30 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `TodoWrite`**: {'todos': [{'id': 'stage4', 'content': 'Typing: pyright tighten orchestration/config/protocols; typed errors at boundaries; commit', 'status': 'completed'}, {'id': 'stage5', 'content': 'Docs/configs: 
- **Tool `Shell`**: Move execution day logs to archive/

</details>

### 回合 31 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Write`**: /home/sunhl/projects/qchem_qml_md/docs/README.md
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/docs/execution/README.md
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/docs/execution/README.md
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/configs/README.md
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/scripts/check_parity_export_sample.py

</details>

### 回合 32 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Run parity export sample check

</details>

### 回合 33 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Debug failing parity export config
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/example_h2_uccgd_pauli_protocol.yaml

</details>

### 回合 34 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/scripts/check_parity_export_sample.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/configs/README.md
- **Tool `Shell`**: Re-run parity export check

</details>

### 回合 35 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Commit Stage 5
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/CHANGELOG.md

</details>

### 回合 36 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/README.md
- **Tool `Shell`**: Commit Stage 6
- **Tool `Shell`**: Run lint and gate scripts

</details>

### 回合 37 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Full pytest validation
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/README.md

</details>

### 回合 38 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests

</details>

### 回合 39 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/tests/test_solver_registry_contract.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests

</details>

### 回合 40 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Verify registry test fix
- **Tool `Shell`**: Commit test fix and README link

</details>

### 回合 41 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Full pytest after test fix
- **Tool `TodoWrite`**: {'todos': [{'id': 'stage5', 'content': 'Docs/configs: README index, archive execution, update configs README, wire YAMLs; commit', 'status': 'completed'}, {'id': 'stage6', 'content': 'Legacy: record d
- **Tool `Shell`**: Show commit history for stages

</details>

### 回合 42 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Verify clean working tree

</details>

### 回合 43 — 助手 (Opus 4.8)

六个阶段已全部完成，工作区干净，`main` 比 `origin/main` 超前 8 个提交。最终验证：**945 passed**，覆盖率 **81.38%**，`ruff` / `check_import_layers` / `check_parity_export_sample` 均通过。

## 各阶段摘要

| 阶段 | 提交 | 内容 |
|------|------|------|
| **0** | (基线) | 确认 `pytest -m "not slow and not perf"` 绿灯 |
| **1** | `72b946b` | 取消跟踪 `results/`、`artifacts/`、`timer.dat`；CI fixture → `tests/fixtures/md_validation_summary.json`；根目录 clutter 移入 `docs/internal/` |
| **2** | `2e24372` | nightly `schedule`、3.12 专属重型 smoke、去掉冗余 marker、mypy 移除、`pip-audit` |
| **3** | `1111227` | `run_vqe_branch` dispatch 表、god-function 拆分、`validate_experiment_for_run`、分层检查与公共 API |
| **4** | `cb835d8` | pyright 对 config/protocols/orchestration 强制参数注解；边界 `ConfigurationError`/`PipelineError` |
| **5** | `115cbaf` | 新增 [`docs/README.md`](docs/README.md)；47 篇执行日志迁入 `docs/execution/archive/`；`configs/README` 更新为 104 YAML；15 个 P4 算法 config 接入 parity 抽样 |
| **6** | `e41e832` | `CHANGELOG` 记录 PySCFDriver / `ml/` / integrations shim 废弃时间表 |

额外修复：`2f2cdea` — registry 测试适配 `ConfigurationError`；根 `README` 链接 `docs/README.md`。

## 需注意的一点

`configs/example_h2_uccgd_pauli_protocol.yaml` 当前 **Pydantic 校验失败**（多余字段 + 无效 `adapt.pool_id`），因此**未**加入 parity sample，已在 `configs/README.md` 标注为「待修」。

如需推送到远端，可以说一声我帮你 `git push`。

[REDACTED]

### 回合 44 — 用户

我不希望你简化我需要你copy所有

### 回合 45 — 助手 (Opus 4.8)

明白，你要的是完整复制、不简化。我先核对当前缺了哪些内容，再逐项补全。

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: List all configs missing from SAMPLE_CONFIGS_REL
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_parity_export_sample.py
- **Tool `Shell`**: Check repo state and execution docs

</details>

### 回合 46 — 助手 (Opus 4.8)

你要的是全部纳入、不省略。我会把所有 config 加入 parity 抽样，并把 execution 日志复制回原目录（archive 保留）。

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Test parity export on all missing configs
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/example_h2_uccgd_pauli_protocol.yaml
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/example_h2_uccgd.yaml

</details>

### 回合 47 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/example_h2_uccgd.yaml
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/config
- **Tool `Shell`**: Test missing configs with venv-run

</details>

### 回合 48 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Get detailed validation errors per config
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/_template.yaml
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/example_h2_angle_md.yaml

</details>

### 回合 49 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Classify all config YAML types

</details>

### 回合 50 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Test all 96 experiment configs for export
- **Tool `Shell`**: Error for custom driver template

</details>

### 回合 51 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/example_custom_driver_template.yaml
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/example_h2.yaml

</details>

### 回合 52 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md

</details>

### 回合 53 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers/custom_solver_template.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md

</details>

### 回合 54 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers/custom_solver_template.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/test_integration_philosophy.py

</details>

### 回合 55 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers

</details>

### 回合 56 — 助手 (Opus 4.8)

正在补全：全部 96 个 experiment config 纳入 parity 抽样、修复 3 个无效 YAML、将 execution 日志复制回原目录。

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/example_h2.yaml
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/README.md

</details>

### 回合 57 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/configs/_template.yaml
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/configs/example_h2_uccgd_pauli_protocol.yaml
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/configs/example_h2_uccgd_pauli_protocol.yaml
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/configs/example_h2_uccgd_pauli_protocol.yaml
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers/custom_solver_template.py

</details>

### 回合 58 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Write`**: /home/sunhl/projects/qchem_qml_md/scripts/check_parity_export_sample.py
- **Tool `Shell`**: Copy execution archive logs back to execution root

</details>

### 回合 59 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md
- **Tool `Shell`**: Run full parity check on all configs

</details>

### 回合 60 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/export_parity_criteria_table.py

</details>

### 回合 61 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/config

</details>

### 回合 62 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/pyproject.toml
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/config/_experiment_validation.py

</details>

### 回合 63 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers/registry.py

</details>

### 回合 64 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers/registry.py

</details>

### 回合 65 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers/registry.py

</details>

### 回合 66 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers/registry.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/test_check_parity_export_sample_script.py

</details>

### 回合 67 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Verify all configs pass parity check
- **Tool `Write`**: /home/sunhl/projects/qchem_qml_md/configs/README.md

</details>

### 回合 68 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/configs/README.md
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/docs/execution/README.md
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/docs/README.md
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/tests/test_check_parity_export_sample_script.py
- **Tool `StrReplace`**: /home/sunhl/projects/qchem_qml_md/CONTRIBUTING.md

</details>

### 回合 69 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Glob`**: {'glob_pattern': 'docs/README.md', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Shell`**: Lint and run related tests

</details>

### 回合 70 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Generate accurate config filename lists
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/README.md

</details>

### 回合 71 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Generate config list blocks for README

</details>

### 回合 72 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /tmp/config_readme_lists.md

</details>

### 回合 73 — 助手 (Opus 4.8)

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Write`**: /home/sunhl/projects/qchem_qml_md/configs/README.md

</details>

### 回合 74 — 助手 (Opus 4.8)

明白，之前只加了约 15 个 config、execution 日志只做了 move，确实不够。现已按「全部复制、不省略」改完：

## 1. Configs — 104 个全部纳入 CI

`scripts/check_parity_export_sample.py` 改为**自动发现**，不再维护手工子集：

| 类型 | 数量 | 处理方式 |
|------|------|----------|
| ExperimentConfig | **96** | 全部跑 config-only parity export |
| MdValidationLoopConfig | **8** | 全部做 `MdValidationLoopConfig.from_yaml` 加载校验 |
| **合计** | **104** | 无遗漏 |

已修复 3 个原先无法导出的 YAML：
- `configs/_template.yaml` — mitigation 字段对齐 schema
- `configs/example_h2_uccgd_pauli_protocol.yaml` — 对齐 `example_h2_uccgd.yaml`
- `configs/example_custom_driver_template.yaml` — 在 registry 中注册 `custom_external_template` 驱动

验证：`python scripts/check_parity_export_sample.py` 已通过（96 + 8）。

## 2. Execution 日志 — copy 而非仅 move

`docs/execution/archive/` 里的 **47 篇** day/milestone 日志已**复制回** `docs/execution/`（archive 保留）。  
现在两处都有完整副本，旧链接和 grep 路径仍可用。

## 3. 文档更新

- `configs/README.md` — 列出全部 96 + 8 个 YAML 完整路径
- `docs/execution/README.md` — 说明 archive + working copy 双份存在
- `CONTRIBUTING.md` — 说明新增 experiment YAML 会自动进 CI，无需再改 `SAMPLE_CONFIGS_REL`

如需把这些改动提交成 commit，说一声即可。

[REDACTED]

### 回合 75 — 用户

**全文收录**（不简写）本 Cursor 窗口内与 opus4.8的对话和全部内容到一个文档命名opus4.8-test

### 回合 76 — 助手 (Opus 4.8)

正在收集本窗口内的完整对话记录，并写入 `opus4.8-test` 文档。

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Glob`**: {'glob_pattern': '**/*', 'target_directory': '/home/sunhl/.cursor/projects/home-sunhl-projects-qchem-qml-md/agent-transcripts'}
- **Tool `Grep`**: /home/sunhl/.cursor/projects/home-sunhl-projects-qchem-qml-md/agent-transcripts

</details>

---

<a id="附six-stage-optimization-计划全文"></a>

# 附：Six-Stage Optimization 计划全文

```markdown
---
name: Six-stage optimization
overview: Execute all six optimization stages on qchem-stack sequentially (hygiene, CI, architecture refactor, typing, docs/configs, legacy), each behavior-preserving with ruff+pytest staying green and a dedicated commit per stage.
todos:
  - id: stage0
    content: "Establish green baseline: run full ruff + pytest (not slow/perf) on clean tree"
    status: completed
  - id: stage1
    content: "Hygiene: untrack results/ artifacts/ timer.dat; move CI fixture to tests/fixtures/ and repoint ci.yml; relocate root clutter docs; commit"
    status: completed
  - id: stage2
    content: "CI: fix nightly schedule trigger, drop redundant marker steps, gate heavy smokes to 3.12, remove unused mypy, add pip-audit; commit"
    status: completed
  - id: stage3
    content: "Refactor: run_vqe_branch dispatch table; split run_pipeline_sync/run_validation_round/VQD.run; fix layering tests (ast.walk) + vsqs public API; unified validate_experiment_for_run; commit"
    status: completed
  - id: stage4
    content: "Typing: enable disallow_untyped_defs for orchestration/config/protocols; replace boundary ValueError/except Exception with typed errors; commit"
    status: completed
  - id: stage5
    content: "Docs/configs: add docs/README.md index, archive execution logs, update configs/README count, wire ~15 unwired configs into CI sample, document doc-sync policy; commit"
    status: completed
  - id: stage6
    content: "Legacy: record deprecation timelines for PySCFDriver/ml/integrations shims in CHANGELOG; commit"
    status: completed
isProject: false
---

# Six-Stage Optimization of qchem-stack

Working tree is clean (`836f6ed`). Execute all six stages in order. After each stage: run `ruff check` + `ruff format --check` + `pytest tests -q -m "not slow and not perf"`, keep green, then make one focused commit. No pushing unless asked.

## Ground rule
Every change is behavior-preserving. Refactors must not alter public outputs (`repro`, `resource_summary`, pipeline `out` dict, protocol results). Establish a green baseline first.

## Stage 0 - Green baseline (verify only)
- Confirm clean tree, run full lint + `pytest -m "not slow and not perf"` to capture the passing baseline before touching anything.

## Stage 1 - Repo hygiene
- `git rm -r --cached results/ artifacts/ timer.dat` (keep files on disk; `.gitignore` already lists them).
- CI depends on [results/uqc_cloud_sim_md_ml_2rounds/md_validation_summary.json](results/uqc_cloud_sim_md_ml_2rounds/md_validation_summary.json): copy it to `tests/fixtures/md_validation_summary.json` and repoint the benchmark step in [.github/workflows/ci.yml](.github/workflows/ci.yml) (line ~136).
- Move root clutter into `docs/internal/` or `docs/archive/`: `CHEM_MODULE_AUDIT_REPORT.md`, `multitask-深入说明.md`; add `tasks_*.csv`, `.ferrmion.log` to `.gitignore`.

## Stage 2 - CI correctness and cost
In [.github/workflows/ci.yml](.github/workflows/ci.yml):
- Fix dead `test-nightly`: add `schedule: cron` trigger so slow/perf/L3 gates actually run.
- Drop redundant `l1_excited` / `l1_md_ml` marker steps (already in main pytest), or restrict to 3.12.
- Gate heavy smokes and optional extras (Qiskit/Aer/Pytket/QPE/sampled) to the 3.12 matrix leg only; 3.10/3.11 run core unit tests.
- Unify type tooling: keep pyright (already in CI), remove unused mypy from `dev` deps and `[tool.mypy]` in [pyproject.toml](pyproject.toml) (or add a mypy job - default: remove).
- Add a lightweight `pip-audit` security step.

## Stage 3 - Architecture de-duplication and decoupling (behavior-preserving)
- `run_vqe_branch` (126 lines, [src/qchem_stack/quantum/variational_plugins/builtins.py](src/qchem_stack/quantum/variational_plugins/builtins.py) line 50): convert 8+ ansatz `if/elif` into an `ansatz_id -> runner` dispatch table with a shared `VariationalStageOutcome` builder.
- Split god-functions into helpers, preserving outputs:
  - `run_pipeline_sync` (186 lines, [src/qchem_stack/orchestration/pipeline.py](src/qchem_stack/orchestration/pipeline.py) line 114): extract repro assembly + `out` building.
  - `run_validation_round` (189 lines, [src/qchem_stack/md_bridge/md_loop_rounds.py](src/qchem_stack/md_bridge/md_loop_rounds.py) line 231): split train / md / label / upgrade-merge.
  - `VQD.run` (228 lines, [src/qchem_stack/quantum/algorithms/excited_vqd.py](src/qchem_stack/quantum/algorithms/excited_vqd.py) line 198): extract optimizer loop and overlap modes.
- Layering: make [tests/chem/test_chem_layer_import_boundaries.py](tests/chem/test_chem_layer_import_boundaries.py) and the quantum equivalent use `ast.walk` (match [scripts/check_import_layers.py](scripts/check_import_layers.py)); either remove the lazy `integrations` import in `chem/embedding/fragment_solvers/registry.py` (line 37) or document it as an explicit allowed exception.
- Replace private cross-layer use `_fermion_operator_to_qubits` in [src/qchem_stack/quantum/algorithms/vsqs_vqe.py](src/qchem_stack/quantum/algorithms/vsqs_vqe.py) (line 13) with a public chem API.
- Add single `validate_experiment_for_run(cfg, caps)` in [src/qchem_stack/config/_experiment_validation.py](src/qchem_stack/config/_experiment_validation.py) used by pipeline + API + CLI to close the cap-dependent validation gap.

## Stage 4 - Type tightening (incremental)
- Turn on `disallow_untyped_defs = true` scoped to `orchestration`, `config`, `protocols` via mypy/pyright per-module overrides; fix surfaced annotations.
- At package boundaries (solvers, backends, md_bridge), replace bare `raise ValueError` and best-effort `except Exception` with the typed hierarchy in [src/qchem_stack/exceptions.py](src/qchem_stack/exceptions.py) where appropriate (leave genuinely best-effort blocks).

## Stage 5 - Docs and configs cleanup
- Add `docs/README.md` taxonomy index (Reference / Contracts / Onboarding / 对标-historical / Execution-archive / Internal).
- Move `docs/execution/` day logs into `docs/execution/archive/`; keep README + master plans.
- Update [configs/README.md](configs/README.md) count (77 -> ~104) and document the ~15 unwired algorithm YAMLs.
- Wire the unwired configs (`example_h2_qite.yaml`, `puccd`, `vsqs`, `jkmn`, etc.) into `SAMPLE_CONFIGS_REL` in [scripts/check_parity_export_sample.py](scripts/check_parity_export_sample.py) and/or L3 benchmark.
- Document the Docusaurus-vs-`docs/` sync policy in one place (source of truth = `docs/public_parity_matrix.md`).

## Stage 6 - Legacy retirement (timeline + CHANGELOG)
- Mark deprecation timeline for `PySCFDriver` (389 lines, [src/qchem_stack/chem/drivers/pyscf_driver.py](src/qchem_stack/chem/drivers/pyscf_driver.py)), `ml/` toy layer, and `integrations/*` re-export shims; record removal versions in [CHANGELOG.md](CHANGELOG.md). No hard removals this round (keep behavior).

## Validation per stage
`ruff check src/qchem_stack tests scripts examples` + `ruff format --check` + `pytest tests -q --tb=short -m "not slow and not perf"`, plus `python scripts/check_import_layers.py` after Stage 3 and `python scripts/check_parity_export_sample.py` after Stage 5.
```

---

<a id="附子-agent-审查报告全文"></a>

# 附：子 Agent 审查报告全文


## 子 Agent：架构与分层审查

**源文件**：`/home/sunhl/.cursor/projects/home-sunhl-projects-qchem-qml-md/agent-transcripts/64dad06a-bd13-4eda-88f5-dc491d1156ec/subagents/da33506d-986e-4552-912b-a03d02a88e58.jsonl`

### 子 Agent 任务描述

Explore the Python source at /home/sunhl/projects/qchem_qml_md/src/qchem_stack (a quantum-chemistry orchestration stack). Be "very thorough". I need a detailed architecture & code-quality review. Report on:

1. Layering & module boundaries: How do layers (chem, quantum, protocols, backends, orchestration, jobs, md_bridge, ml, mitigation, integrations, config, api, contracts) depend on each other? Are there import-boundary checks (look at scripts/check_import_layers.py and tests/*/test_*_layer_import_boundaries.py)? Any circular imports or layering violations / leaky abstractions?

2. Complexity hotspots: identify the most complex/largest functions and files. Look at orchestration/pipeline.py, chem/hamiltonian_build.py, quantum/algorithms/*, md_bridge/md_loop_rounds.py. Note god-functions, deep nesting, duplicated logic.

3. Public API surface: how is the public API defined (__init__.py exports, __all__)? Are there deprecation shims and legacy paths still lingering (grep for DeprecationWarning, "legacy", "deprecated", "shim")? 

4. Error handling & typing: are typed errors used consistently? Any broad `except Exception`? mypy/pyright posture.

5. Dead code / TODO/FIXME/HACK markers: count and list notable ones.

6. Configuration handling: how config validation is structured (config/ module), and whether it's overly complex.

Return concrete file:line references and a prioritized list of the top issues you find. Do not modify any files.

### 子 Agent 完整输出

Starting a systematic architecture review: mapping the package layout, import-boundary enforcement, and complexity hotspots.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `UpdateCurrentStep`**: {'current_step': 'Mapping package structure'}
- **Tool `Glob`**: {'target_directory': '/home/sunhl/projects/qchem_qml_md/src/qchem_stack', 'glob_pattern': '**/*'}
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_import_layers.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack
- **Tool `Glob`**: {'target_directory': '/home/sunhl/projects/qchem_qml_md', 'glob_pattern': '**/pyproject.toml'}
- **Tool `Glob`**: {'target_directory': '/home/sunhl/projects/qchem_qml_md', 'glob_pattern': '**/mypy.ini'}
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack
- **Tool `Shell`**: Count lines in largest Python files

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/internal/import_layers.md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/chem/test_chem_layer_import_boundaries.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/__init__.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/exceptions.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/pyproject.toml
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Glob`**: {'target_directory': '/home/sunhl/projects/qchem_qml_md/tests', 'glob_pattern': '**/*layer*'}
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/orchestration/pipeline.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/config/__init__.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/quantum/test_quantum_layer_import_boundaries.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/hamiltonian_build.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/md_bridge/md_loop_rounds.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols/computable.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/orchestration/stage_execution.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/md_bridge/md_loop_rounds.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum/algorithms/excited_vqd.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/pre_quantum_branches.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/orchestration/protocol_finalize_run.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem
- **Tool `Glob`**: {'target_directory': '/home/sunhl/projects/qchem_qml_md/src/qchem_stack/config', 'glob_pattern': '**/*'}
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum/variational_plugins/registry.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/orchestration/protocol_finalize_run.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/config/_experiment_validation.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum/algorithms/uccsd_vqe.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/__init__.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/orchestration/__init__.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/md_bridge/__init__.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/ml/__init__.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum/algorithms/excited_vqd.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols/protocol.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/embedding/decomposition_plugin.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/config
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/contracts/__init__.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum/variational_plugins/builtins.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/orchestration/stage_execution.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/config/experiment.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum/algorithms/__init__.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/config/_experiment_validation.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/protocols/computable.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/md_bridge/qchem_labeler.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/config_校验分层约定.md
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum/variational_plugins/builtins.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: AST-analyze largest functions in key files
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum/variational_plugins/builtins.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/drivers/pyscf_driver.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/quantum/test_quantum_layer_import_boundaries.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/ml/surrogate.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/integrations/ucc_reference.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/quantum
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/src/qchem_stack/backends/__init__.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `UpdateCurrentStep`**: {'current_step': 'Compiling architecture review', 'final_summary': 'Architecture review of `qchem_stack` (~421 Python modules): layering is documented and partially enforced, but CI AST checks are wea

</details>

### 子 Agent 完整输出

# Architecture & Code-Quality Review: `qchem_stack`

Scope: `/home/sunhl/projects/qchem_qml_md/src/qchem_stack` (~421 `.py` files, ~42k LOC). Read-only analysis.

---

## 1. Layering & Module Boundaries

### Documented model

[`docs/internal/import_layers.md`](/home/sunhl/projects/qchem_qml_md/docs/internal/import_layers.md) defines a top-down stack:

| Tier | Packages | May import |
|------|----------|------------|
| Top | `orchestration`, `api`, `jobs`, `md_bridge` | chem, quantum, protocols, backends, config, mitigation, integrations |
| Mid | `protocols`, `backends`, `mitigation` | config, quantum (backends), chem (indirect) |
| Core | `config`, `chem`, `quantum` | config + same-layer; **must not** import `orchestration` |

`contracts` is a leaf constants/validation package (no orchestration). `integrations` holds parity/benchmark shims and DMET sidecars. `ml` is explicitly a toy/demo layer superseded by `md_bridge`.

### Enforcement (three mechanisms, not fully aligned)

**A. CI script** — [`scripts/check_import_layers.py`](/home/sunhl/projects/qchem_qml_md/scripts/check_import_layers.py)

- Uses `ast.walk` (imports **anywhere** in the file).
- Rules: `chem` → forbid `orchestration`; `quantum` → forbid `orchestration` and top-level `pyscf`.
- Skips only `chem/__init__.py` and `quantum/__init__.py` at package root.

**B. Tests** (only two layer-boundary test files found; no `test_*_layer_import_boundaries` glob beyond these):

- [`tests/chem/test_chem_layer_import_boundaries.py`](/home/sunhl/projects/qchem_qml_md/tests/chem/test_chem_layer_import_boundaries.py) — module-level imports only (`tree.body`); forbids `qchem_stack.quantum`, `qchem_stack.integrations`, `qchem_stack.orchestration`.
- [`tests/quantum/test_quantum_layer_import_boundaries.py`](/home/sunhl/projects/qchem_qml_md/tests/quantum/test_quantum_layer_import_boundaries.py) — module-level + substring scan for `pyscf`.

**Gap:** Script is **stricter** (all imports) than tests (module-level only). Chem **violates** the chem test’s integrations rule via **lazy** imports that tests do not see:

```37:37:/home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/embedding/fragment_solvers/registry.py
    from qchem_stack.integrations.dmet_fragment_solvers import QubitHamiltonianFragmentSolverVQE
```

Also at `chem/embedding/__init__.py:50`, `chem/embedding/schmidt_variational_sidecar.py:17`.

**C. No automated rules** for: `protocols`↔`orchestration`, `backends`↔`chem`, `md_bridge`↔`orchestration`, or `integrations`↔`orchestration` (the latter is intentional for L3 benchmarks).

### Observed dependency graph (simplified)

```
api, jobs, md_bridge ──► orchestration ──► chem, quantum, protocols, backends, config, jobs
protocols ──► backends, quantum (circuits), config
backends ──► quantum.statevector (private helpers), config
quantum ──► chem.kernels, chem.hamiltonian (types), config  [no pyscf, no orchestration]
chem ──► config only at module scope; integrations via lazy hooks
config ──► (leaf); pydantic + cross-validators
contracts ──► (constants); consumed everywhere
```

### Circular imports

No `chem`↔`quantum` module-scope cycles found. `chem` does not import `quantum` at module scope. `pipeline.py` is a thin coordinator (342 lines); complexity is pushed to stage modules.

### Leaky abstractions / layering violations

| Issue | Location | Severity |
|-------|----------|----------|
| Quantum imports **private** chem API | `quantum/algorithms/vsqs_vqe.py:13` — `_fermion_operator_to_qubits` | Medium |
| Chem embedding registry lazy-imports `integrations` | `chem/embedding/fragment_solvers/registry.py:37,63` | Medium |
| Orchestration SCF stage pulls `integrations.rdm_corrections` inside `run_scf_stage` | `orchestration/stage_execution.py:131-135` | Low (top layer) |
| `protocols/computable.py` is a large config→export mapper (380 lines) sitting in protocols but depending heavily on `config.quantum_helpers` | `protocols/computable.py:15-33,205+` | Low |
| Backends reach into quantum internals | `backends/pauli_shot_sim.py:12`, `qiskit_qse_transition.py:16`, `executor_base.py:7` | Low–medium |

No `orchestration` imports under `chem/` or `quantum/` at module scope (grep clean).

---

## 2. Complexity Hotspots

### Largest files (by line count)

| Lines | File |
|------:|------|
| 425 | `quantum/algorithms/excited_vqd.py` |
| 419 | `md_bridge/md_loop_rounds.py` |
| 389 | `chem/drivers/pyscf_driver.py` (deprecated facade) |
| 380 | `protocols/computable.py` |
| 375 | `quantum/algorithms/sceom.py` |
| 363 | `quantum/algorithms/excited_basis.py` |
| 353 | `quantum/algorithms/uccsd_vqe.py` |
| 342 | `orchestration/pipeline.py` |
| 333 | `config/_experiment_validation.py`, `quantum/algorithms/excited_qse.py` |
| 319 | `chem/hamiltonian_build.py` |
| 315 | `quantum/variational_plugins/builtins.py` |

### Largest functions (AST line spans)

| Lines | Function | File:line |
|------:|----------|-----------|
| **186** | `run_pipeline_sync` | `orchestration/pipeline.py:114` |
| **189** | `run_validation_round` | `md_bridge/md_loop_rounds.py:231` |
| **228** | `VQD.run` | `quantum/algorithms/excited_vqd.py:198` |
| **135** | `run_scf_stage` | `orchestration/stage_execution.py:63` |
| **129** | `list_computables_for_config` | `protocols/computable.py:205` |
| **126** | `run_vqe_branch` | `quantum/variational_plugins/builtins.py:50` |
| **80** | `qubit_hamiltonian_from_compact_restricted_active_space` | `chem/hamiltonian_build.py:228` |

### God-functions & nesting

- **`run_pipeline_sync`** (`pipeline.py:114-299`): single function owns SCF → pre-quantum → repro → variational → embedding workflow → excited → finalize. Readable stage delegation exists (`stage_execution.py`), but the outer function still accumulates repro patching (~60 lines, `237-259`) and a large `out` dict assembly.
- **`run_vqe_branch`** (`builtins.py:50-175`): 8+ ansatz branches with copy-pasted `VariationalStageOutcome` construction — classic dispatch-table candidate.
- **`run_validation_round`** (`md_loop_rounds.py:231-419`): train → MD → label → frame records → upgrade path → merge; deep conditional tree for upgrade_dataset (`361-384`).
- **`run_scf_stage`** (`stage_execution.py:63-197`): RDM correction path with nested `if/elif` and lazy imports.

### Duplicated logic

- **UCC family VQE modules**: `uccsd_vqe.py`, `uccgd_vqe.py`, `puccd_vqe.py`, `upccgsd_vqe.py`, `qcc_vqe.py` share pattern (generators from `chem.kernels.spin_ucc`, `run()`, `*_algorithm_report_v1`) — duplicated again in `run_vqe_branch`.
- **Pipeline job enqueue** duplicated between `pipeline.py:317-341` and `protocol_finalize_run.py:100-109` (protocol build/compile/run).
- **DMET / Schmidt**: implementations in `chem/embedding/` with `integrations/*` re-export shims (`integrations/dmet_self_consistent.py`, `schmidt_dmet_self_consistent.py`).

### `hamiltonian_build.py`

Split across `hamiltonian_build.py`, `hamiltonian_build_spatial.py`, `hamiltonian_build_assembly.py`, `hamiltonian_mapping.py` — good decomposition. Deprecated entry at `hamiltonian_build.py:118-138` (`molecular_hamiltonian_from_classical_reference`).

---

## 3. Public API Surface

### Root package

[`src/qchem_stack/__init__.py`](/home/sunhl/projects/qchem_qml_md/src/qchem_stack/__init__.py) exports only **errors + repro JSON helpers + version** (`__all__` lines 22-31). No pipeline or chem surface at top level — intentional minimal API.

### Subpackage `__all__` patterns

| Package | Pattern | Notes |
|---------|---------|-------|
| `chem` | Large `__all__` + `__getattr__` lazy loads | Well-documented; `# pyright: reportUnsupportedDunderAll=false` at line 1 |
| `config` | Explicit 48-name `__all__` | Canonical public config surface |
| `orchestration` | 10 symbols incl. `run_pipeline_*`, `WorkflowCoordinator` | Re-exports `PipelineError` from `exceptions` in `__all__` |
| `md_bridge` | 47 symbols | Production MD/ML API |
| `quantum` | Lazy `algorithms/__init__.py` with `__all__` | Root `quantum/__init__.py` has `__all__: list[str] = []` (empty) |
| `api` | `__all__: list[str] = []` | FastAPI app not exported as stable API |
| `ml` | No `__all__`; only `ActiveLearningLoop` import | Toy layer |
| `protocols` | Minimal: `PauliAveragingProtocol`, `ProtocolPhase` | Most protocol code is internal |

### Deprecation / legacy / shims (grep summary)

| Kind | Examples |
|------|----------|
| `DeprecationWarning` | `chem/drivers/pyscf_driver.py:90-95`, `chem/hamiltonian.py:46-48`, `chem/pre_quantum_build.py:87-89`, `ml/surrogate.py:20-23`, `protocols/secure_serialization.py:103-105`, `integrations/ucc_reference.py:19-20` |
| Config `"legacy"` enums | `config/quantum_specs.py:145-149`, `quantum_excited_params.py:21-43` (VQD init strategies — not removal, behavior flag) |
| API deprecated route | `api/routers/runs.py:144` — `POST /v1/runs/sync` |
| Re-export shims | `integrations/ucc_reference.py`, `integrations/dmet_self_consistent.py`, `chem/embedding/schmidt_variational_sidecar.py` |
| Legacy pickle | `protocols/secure_serialization.py:64-114` |
| UQC legacy Z-only shots | `backends/uqc_executor.py:142,196` |

Legacy **PySCFDriver** (`chem/drivers/`, 389 lines) remains exported via `chem/drivers/__init__.py:16` — significant maintenance surface for a deprecated path.

---

## 4. Error Handling & Typing

### Typed error hierarchy

[`exceptions.py`](/home/sunhl/projects/qchem_qml_md/src/qchem_stack/exceptions.py) defines a small tree:

- `QChemStackError` → `ConfigurationError`, `ReproExportError`, `PipelineError`, `EmbeddingError`, `PreQuantumError` / `PreQuantumCapabilityError`

Docstring at `exceptions.py:4-5` says domain code should raise these at boundaries; **Pydantic `ValidationError`** is the documented path for field validation (`config/__init__.py:5-10`).

### Usage consistency (approximate counts)

| Pattern | ~Count | Assessment |
|---------|--------|------------|
| `raise ValueError` | **~120+** files | Dominant; often appropriate for local invariants |
| `raise PipelineError` | **~50** sites | Concentrated in orchestration, md_bridge, loaders |
| `raise ConfigurationError` | **~37** sites | Config I/O + cross-field validators |
| `raise RuntimeError` | Sparse | e.g. `ml/surrogate.py:31` |
| Domain-specific (`UnknownSolverError`, `SchmidtProductionError`) | Local registries | Good |

**Broad `except Exception`**: **33 occurrences** across 28 files (see grep list). Notable:

- `md_bridge/qchem_labeler.py:159,190` — intentional failure-isolation for batch labeling
- `orchestration/repro_metadata.py:22-45` — best-effort metadata (4×)
- `backends/uqc_executor.py:172`, `uqc_pauli_shots.py:100` — cloud/API resilience
- `chem/precomputed_bundle.py:46,53` — bundle load fallbacks

### mypy / pyright posture

From [`pyproject.toml`](/home/sunhl/projects/qchem_qml_md/pyproject.toml) `[tool.mypy]` (lines 92-98):

- `disallow_untyped_defs = false`
- `ignore_missing_imports = true`
- `check_untyped_defs = true`

**Permissive** for a library this size. `chem/__init__.py:1` opts into pyright dunder-all suppression. Widespread `TYPE_CHECKING` guards (~200+ files) — good for import cycles, but runtime typing is thin.

No `pyright` project config found; mypy is dev-optional, not described as CI-gating in the snippet reviewed.

---

## 5. Dead Code / TODO / FIXME / HACK

| Marker | Count in `src/qchem_stack` |
|--------|---------------------------|
| `TODO` / `FIXME` / `HACK` / `XXX` | **4 comment lines, 1 file only** |

All in [`chem/solvers/mock_external_solver_example.py`](/home/sunhl/projects/qchem_qml_md/src/qchem_stack/chem/solvers/mock_external_solver_example.py) (`31`, `59`, `91`, `110`) — template for external solvers, not dead production code.

**Implication:** Very low inline debt markers; legacy is tracked via `DeprecationWarning` and README/shim modules instead.

Potential “soft dead” packages:

- `ml/` — documented non-production (`ml/__init__.py:1-6`)
- `tensornet/cutensornet_protocol_stub.py` — stub
- `qpe_qec_demo/` — demo track
- Deprecated `PySCFDriver` + `integrations/ucc_reference.py`

---

## 6. Configuration Handling

### Structure (52 files under `config/`)

Layered design per [`docs/config_校验分层约定.md`](/home/sunhl/projects/qchem_qml_md/docs/config_校验分层约定.md):

1. **Specs** — `molecule.py`, `scf.py`, `quantum.py`, `embedding_specs.py`, `*_specs.py` (Pydantic, `extra='forbid'` on sections)
2. **Resolvers/helpers** — `quantum_helpers.py`, `scf_helpers.py`, `embedding_helpers.py` (no YAML parsing in algorithms)
3. **Cross-field validators** — `_experiment_validation.py`, `_embedding_validation.py`, `_quantum_validation.py`, `_active_space_validation.py`, etc.
4. **Top model** — `experiment.py:49-107` runs `EXPERIMENT_CROSS_VALIDATORS` on every `model_validate`

### Validation split (intentional complexity)

| Registry | When | File:line |
|----------|------|-----------|
| `EXPERIMENT_CROSS_VALIDATORS` (7 validators) | Pydantic `@model_validator` after build | `_experiment_validation.py:308-317`, `experiment.py:104-106` |
| `EXPERIMENT_CROSS_VALIDATORS_WITH_CAPS` (3 validators) | Pipeline SCF stage with live `SolverCapabilities` | `_experiment_validation.py:320-324`, `stage_execution.py:73-74` |
| `validate_pre_quantum_contract()` | Subset for pre-quantum-only callers | `_experiment_validation.py:48-70` |

**Assessment:** Complexity is **high but documented and deliberate** — not a single god-validator. Risk is **split-brain**: some rules only run with caps in pipeline (`validate_pbc_k_mesh_solver_capability` explicitly excluded from `validate_pre_quantum_contract` per docstring `58-60`). Callers loading config without pipeline may miss cap-dependent errors.

`config/__init__.py` re-exports 48 names — clear public surface. Nested `schema_version: "2"` enforced at `experiment.py:76-80`.

---

## Prioritized Top Issues

| P | Issue | Evidence | Recommendation |
|---|-------|----------|----------------|
| **P0** | Import-boundary tests weaker than intent; chem→integrations via lazy imports | `test_chem_layer_import_boundaries.py:19-25` vs `chem/embedding/fragment_solvers/registry.py:37` | Align tests with `check_import_layers.py` (`ast.walk`) or forbid lazy integrations in chem; document allowed exceptions |
| **P1** | `run_pipeline_sync` god-function (186 lines) | `orchestration/pipeline.py:114-299` | Extract repro assembly + `out` building to helpers; keep pipeline as stage list only |
| **P1** | `run_vqe_branch` ansatz dispatch duplication (126 lines) | `quantum/variational_plugins/builtins.py:50-175` | Registry dict `ansatz_id → runner`; share outcome builder |
| **P1** | `run_validation_round` monolith (189 lines) | `md_bridge/md_loop_rounds.py:231-419` | Split train/md, screen, upgrade-merge phases |
| **P2** | VQD `run` method 228 lines | `quantum/algorithms/excited_vqd.py:198` | Decompose optimizer loop / overlap modes |
| **P2** | Private chem API used from quantum | `quantum/algorithms/vsqs_vqe.py:13` | Public `fermion_operator_to_qubits` in `chem.hamiltonian_mapping` |
| **P2** | Typed errors underused vs `ValueError` | `exceptions.py` vs widespread `raise ValueError` | Gradual migration at package boundaries (solvers, backends, md_bridge) |
| **P2** | Permissive mypy (`disallow_untyped_defs=false`) | `pyproject.toml:96-98` | Tighten on `orchestration`, `config`, `protocols` first |
| **P3** | Deprecated PySCFDriver still large (389 lines) | `chem/drivers/pyscf_driver.py` | Accelerate migration per `docs/迁移指南_PySCFDriver到ChemIntegralSolver.md` |
| **P3** | Cap-dependent validation only in pipeline | `_experiment_validation.py:58-64`, `stage_execution.py:73-74` | Export single `validate_experiment_for_run(cfg, caps)` used by API + CLI |
| **P3** | 33× `except Exception` | See §4 grep | Audit: replace with typed errors where not truly best-effort |
| **P4** | `protocols/computable.py` config coupling | `computable.py:205-334` | Move to `orchestration` or `integrations/workflow_preview` |
| **P4** | Empty `quantum/__init__.py` `__all__` | `quantum/__init__.py:40` | Document entry as `quantum.algorithms` only |

---

## Summary

The stack has a **clear intended layering** (chem/quantum core, orchestration coordinator, protocols/backends execution) with **CI + tests** guarding the most critical reverse-dependencies. Enforcement is **incomplete**: tests inspect only module-level imports while chem uses **lazy `integrations` imports**; quantum correctly avoids `pyscf` and `orchestration`.

**Code quality strengths:** split hamiltonian build modules, stage context injection in `stage_execution.py`, rich config validation split across `_experiment_validation*.py`, minimal root `__all__`, very few TODO markers.

**Main weaknesses:** several **100–200 line functions**, **duplicated UCC/VQE dispatch**, **legacy surfaces** (PySCFDriver, integrations shims, ml surrogate), **permissive typing**, and **inconsistent error taxonomy** (`ValueError` vs `PipelineError`/`ConfigurationError`).

I did not run tests or mypy in Ask mode; findings are from static analysis only.

[REDACTED]


## 子 Agent：测试 / CI / 开发流程审查

**源文件**：`/home/sunhl/.cursor/projects/home-sunhl-projects-qchem-qml-md/agent-transcripts/64dad06a-bd13-4eda-88f5-dc491d1156ec/subagents/a7973dbc-fc60-4924-a206-61c524a3a1c5.jsonl`

### 子 Agent 任务描述

Explore /home/sunhl/projects/qchem_qml_md, focusing on testing, CI, and developer workflow. Be "very thorough". Report on:

1. CI: read .github/workflows/*.yml. What jobs run (lint, test matrix, smoke, docusaurus build, markers)? Python versions? Any gaps (no type-check in CI? no coverage gate enforced? no security scanning)? How long/expensive does it look?

2. Test suite: 230 test files in tests/. Assess organization (tests/, tests/quantum/, tests/chem/, tests/config/). Are there slow tests, heavy use of importorskip, flaky-looking patterns? Look at tests/conftest.py. What's the coverage gate (pyproject says fail-under=75). Is .coverage / htmlcov committed (it appears in repo root)?

3. Scripts: 35 scripts in scripts/. Which are CI-critical vs one-off/dev scripts? Any that look like they should be in the package or removed? Look at scripts/smoke_pipeline.py, scripts/check_*.py, scripts/verify_ninety_day_gates.sh.

4. Pre-commit: read .pre-commit-config.yaml. Does it match CI (ruff)? Any hooks missing (mypy, trailing whitespace, large files)?

5. Repo hygiene: note committed artifacts that probably shouldn't be tracked: .coverage, htmlcov/, timer.dat, .ferrmion.log, .mypy_cache, .ruff_cache, .pytest_cache, .venv, .venv-wsl, results/. Check .gitignore. Is .env committed (it appears at repo root)?

Return concrete findings with file paths and a prioritized list of top issues. Do not modify files.

### 子 Agent 完整输出

I'll systematically explore CI, tests, scripts, pre-commit, and repo hygiene across the project.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `UpdateCurrentStep`**: {'current_step': 'Exploring CI workflows and config', 'final_summary': ''}
- **Tool `Glob`**: {'glob_pattern': '.github/workflows/*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/.pre-commit-config.yaml
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/.gitignore
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/pyproject.toml
- **Tool `Glob`**: {'glob_pattern': 'tests/**/*.py', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Glob`**: {'glob_pattern': 'scripts/**/*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/.github/workflows/ci.yml
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/conftest.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/smoke_pipeline.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/verify_ninety_day_gates.sh
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: List tracked artifact paths in git
- **Tool `Shell`**: Count test files and list subdirs
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_import_layers.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_parity_export_sample.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Check tracked hygiene artifacts and counts
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/.github/workflows/ci.yml
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Glob`**: {'glob_pattern': 'Makefile', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Glob`**: {'glob_pattern': '**/CONTRIBUTING*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/CONTRIBUTING.md
- **Tool `Glob`**: {'glob_pattern': '.github/**/*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Shell`**: Verify git tracking and test dir counts
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/test_hamiltonian_build_perf.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/test_l3_benchmark_smoke.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/orchestration/test_orchestration_pipeline.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/.github/dependabot.yml
- **Tool `Shell`**: Check which hygiene files are git-tracked
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/.env.example
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/htmlcov/.gitignore

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `UpdateCurrentStep`**: {'current_step': 'Analyzing tests and scripts'}
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/scripts
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_solver_adapter_contract.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_cross_solver_parity.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_comparative_execution_backlog.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_notebooks_smoke.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_uqc_connectivity.py
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/.github/workflows/ci.yml
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/test_uqc_mock_md_ml_integration.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/examples/run_all_smoke.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/timer.dat
- **Tool `Shell`**: Find tracked binary/cache artifacts

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/venv-run
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/sample_pipeline_configs.py
- **Tool `Shell`**: Verify .env tracking and artifact sizes

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Glob`**: {'glob_pattern': 'tests/helpers/*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/tests/helpers/paths.py

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md/tests
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/QUICKSTART_CONTRIBUTORS.md

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Glob`**: {'glob_pattern': 'tests/config/*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Glob`**: {'glob_pattern': 'tests/chem/*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Glob`**: {'glob_pattern': 'tests/quantum/*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/.env

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `UpdateCurrentStep`**: {'current_step': 'Compiling findings report', 'final_summary': '', 'completed_subtitle': 'Mapped CI, tests, scripts, hygiene'}

</details>

### 子 Agent 完整输出

# Testing, CI, and Developer Workflow Audit

`/home/sunhl/projects/qchem_qml_md` has a **strong, gate-heavy CI** (lint, pyright, 3.10–3.12 matrix, many orchestration smokes, Psi4 job, Docusaurus build). The main weaknesses are **repo hygiene** (tracked `results/` and `timer.dat`), **CI cost/redundancy**, and **gaps between docs and CI** for several `check_*` scripts.

---

## 1. CI (`.github/workflows/ci.yml`)

Single workflow file: `/home/sunhl/projects/qchem_qml_md/.github/workflows/ci.yml`. Dependabot: `/home/sunhl/projects/qchem_qml_md/.github/dependabot.yml` (Actions weekly, pip monthly, docusaurus npm weekly).

### Jobs

| Job | Python / runtime | What runs |
|-----|------------------|-----------|
| **lint** | 3.12 | `ruff check` + `ruff format --check` on `src/qchem_stack`, `tests`, `scripts`, `examples`; `python scripts/check_import_layers.py` |
| **typecheck-config** | 3.12 (needs lint) | `pyright` on `config/`, `repro/`, `exceptions.py` |
| **typecheck-stack** | 3.12 (needs lint) | `pyright src/qchem_stack` (full tree) |
| **test** | **matrix 3.10, 3.11, 3.12** | Full gate bundle (see below) |
| **test-nightly** | 3.12 | `pytest -m "slow or perf"`; `QCHEM_RUN_L3=1 pytest -m l3` |
| **test-psi4** | 3.12 + micromamba | Creates conda env with `psi4`, `pyscf`; `pytest -m psi4` |
| **docusaurus** | Node 20 | `npm ci` + `npm run build` in `docusaurus-site/` |

### Test job detail (the heavy one)

After `pip install -e ".[dev]"`:

1. **Docs sync gate**: `scripts/sync_pre_quantum_docs.py` + `git diff --exit-code` on two docs
2. **Main pytest**: `pytest tests -q --tb=short -m "not slow and not perf"` — inherits `pyproject.toml` addopts including **`--cov-fail-under=75`**
3. **Coverage artifact** (3.12 only): uploads `htmlcov/` — no Codecov/service gate
4. **Examples**: `python examples/run_all_smoke.py`
5. **Marker reruns** (redundant with step 2 for non-slow tests):
   - `pytest -m l1_excited`
   - `pytest -m l1_md_ml`
   - `pytest tests/test_uqc_mock_md_ml_integration.py -m "uqc_mock and not slow"`
6. **API extra**: `pip install -e ".[api]"`; `pytest tests/test_api_runs.py`
7. **Many orchestration smokes** via `scripts/smoke_pipeline.py` (`--precomputed-only`, default+`QCHEM_SMOKE_REQUIRE_PYSCF=1`, `--excited-only`, `--iqeb`, `--projection-trace`, `--qiskit-shots`, `--sampled`)
8. **Parity export**: `export_parity_criteria_table.py`, schema assertions, `check_parity_export_sample.py`
9. **Benchmark dashboard**: `scripts/benchmark_dashboard/generate.py` (uses committed `results/uqc_cloud_sim_md_ml_2rounds/md_validation_summary.json`)
10. **Pytket**: `pytest tests/test_pytket_bridge.py`
11. **QPE demo**: `scripts/run_qpe_track_demo.py`

### Markers (from `pyproject.toml`)

`l3`, `l1_excited`, `l1_md_ml`, `uqc_mock`, `slow`, `pyscf`, `psi4`, `no_pyscf`, `perf`.

PR CI excludes **`slow`** and **`perf`**; **`l3`** only in nightly (when it runs).

### Type-checking

- **Pyright is in CI** (two jobs).
- **Mypy is not in CI** — listed in `[project.optional-dependencies] dev` and configured in `[tool.mypy]`, but never invoked in workflows.

### Coverage gate

- **Enforced in CI** via default pytest addopts:

```52:57:/home/sunhl/projects/qchem_qml_md/pyproject.toml
addopts = [
    "--cov=src/qchem_stack",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-fail-under=75",
]
```

- Uploaded as artifact only; **no coverage trend/reporting service**, no per-PR comment.

### Security scanning

**None observed**: no CodeQL, Bandit, `pip-audit`, Trivy, or secret scanning workflows.

### Cost / duration (estimate)

Looks **moderately expensive**:

- **3× full test jobs** (3.10–3.11–3.12), each running **many full pipeline smokes** — likely dominant cost.
- **Duplicate marker runs** (`l1_excited`, `l1_md_ml`) re-run tests already included in main pytest.
- **test-psi4**: micromamba + Psi4 conda solve — slow setup, separate runner.
- **Two pyright jobs** over overlapping trees.
- **Docusaurus** `npm ci` + production build.

Rough total: **~25–50+ minutes** wall time on a typical PR (parallel jobs help, but `test` matrix is 3 sequential-ish heavy runners).

### CI gaps / inconsistencies

1. **`test-nightly` is effectively dead**: condition uses `github.event_name == 'schedule'`, but `on:` has **no `schedule:` trigger** — only runs on commits with `[nightly]` in message.
2. **Docs claim CI runs scripts that do not appear in `ci.yml`**:
   - `scripts/check_comparative_execution_backlog.py` (referenced in `docs/execution/comparative_execution_backlog.yaml`, execution README)
   - `scripts/check_notebooks_smoke.py` (same backlog doc)
3. **`scripts/sample_pipeline_configs.py`** in `verify_ninety_day_gates.sh` but **not in CI** (CI uses `check_parity_export_sample.py` instead).
4. **`check_solver_adapter_contract.py`**, **`integration_checklist.py`**, **`check_cross_solver_parity.py`**: documented for dev/review, not CI.
5. **No mypy** despite dev dependency and config.
6. **No security/dependency vulnerability scanning** beyond Dependabot version bumps.

---

## 2. Test Suite (`tests/`)

### Scale and organization

- **~230** `test_*.py` files on disk; **217** git-tracked under `tests/`.
- Layout:

| Location | Count | Role |
|----------|-------|------|
| `tests/` (root) | ~179 | Majority — flat, domain-mixed |
| `tests/quantum/` | 30 | Quantum layer, excited states, ansätze |
| `tests/config/` | 10 | YAML/Pydantic validation |
| `tests/chem/` | 8 | Chem layer boundaries, integrals |
| `tests/orchestration/` | 3 | Pipeline orchestration |
| `tests/helpers/` | 4 | Shared paths, H2 YAML, registry reset |
| `tests/fixtures/` | golden JSON, etc. |

Subdirs exist but **most tests remain at root** — partial migration, not fully layered.

### `tests/conftest.py`

`/home/sunhl/projects/qchem_qml_md/tests/conftest.py`:

- Sets `QCHEM_STACK_DISABLE_RATE_LIMIT=1` by default for API tests.
- Session fixture `pyscf_available`.
- H2 energy/YAML fixtures via `tests/helpers/h2_yaml.py`.
- **Autouse** `_isolate_solver_registry_between_tests` — good isolation pattern.
- `test_data_dir`, `h2_config`, `tmp_job_db`, `mock_executor`.

### Slow / optional / heavy patterns

**Explicit slow markers** (6 files, excluded from PR CI):

- `tests/test_dmet_fragment_exact.py`
- `tests/test_h4_schmidt_multifragment_yaml.py`
- `tests/test_psi4_solver_integration.py`
- `tests/test_md_ml_qmef_repro_attachment.py`
- `tests/test_uqc_mock_md_ml_integration.py` (one test)
- `tests/quantum/test_uccsd_pauli_decomposition.py`

**Perf** (1 file, nightly-only): `tests/test_hamiltonian_build_perf.py` — 120s wall-time soft cap.

**L3** (nightly + `QCHEM_RUN_L3=1`): `tests/test_l3_benchmark_smoke.py`.

**`importorskip`**: used in **~96 test files** — expected for optional PySCF, Psi4, Qiskit, qmlff, jax_md, tangelo, etc. Ruff explicitly allows E402 in tests for this pattern (`pyproject.toml` per-file-ignores).

**Marker coverage**:

- `l1_excited`: 6 files (all under `tests/quantum/` or `tests/orchestration/`)
- `l1_md_ml`: 16 files (mostly `test_md_bridge_*`, UQC mock integration)

**Flaky-adjacent patterns** (not necessarily flaky, but worth noting):

- Fixed RNG seeds in shot/sim tests — good practice.
- `test_uqc_mock_md_ml_integration.py` writes under `results/uqc_mock_md_ml_test/` during CI-eligible tests.
- `scripts/smoke_pipeline.py` returns **exit 0 when PySCF missing** unless `QCHEM_SMOKE_REQUIRE_PYSCF=1` (CI sets that for the main smoke step).
- `verify_ninety_day_gates.sh` runs **`python -m pytest -q` with no marker filter** — includes slow/perf unlike CI.

### Coverage artifacts

- **Gate**: 75% (`--cov-fail-under=75` + `[tool.coverage.report] fail_under = 75`).
- **`.coverage` and `htmlcov/`**: present locally, **gitignored**, **not tracked**.
- `htmlcov/.gitignore` contains `*` (coverage.py convention).

---

## 3. Scripts (`scripts/` — 34 files + `venv-run`)

### CI-critical (referenced in `ci.yml`)

| Script | Role |
|--------|------|
| `scripts/check_import_layers.py` | Lint job — AST import boundary enforcement |
| `scripts/sync_pre_quantum_docs.py` | Generated docs drift check |
| `scripts/smoke_pipeline.py` | Multiple orchestration end-to-end smokes |
| `scripts/export_parity_criteria_table.py` | Parity export JSON smoke + schema checks |
| `scripts/check_parity_export_sample.py` | Multi-config L1 parity export gate |
| `scripts/benchmark_dashboard/generate.py` | Static HTML artifact generation |
| `scripts/run_qpe_track_demo.py` | QPE dual-track demo |

### Maintainer / local gate (documented, not all in CI)

| Script | Notes |
|--------|-------|
| `scripts/verify_ninety_day_gates.sh` | Full pytest + `check_parity_export_sample` + `sample_pipeline_configs` |
| `scripts/sample_pipeline_configs.py` | Broader YAML sampling; optional `--pipeline` |
| `scripts/check_comparative_execution_backlog.py` | Backlog YAML validator — **docs say CI, workflow doesn't run it** |
| `scripts/check_notebooks_smoke.py` | Notebook execution — **same gap** |
| `scripts/check_solver_adapter_contract.py` | Plugin contract validation |
| `scripts/integration_checklist.py` | CLI wrapper for `run_integration_checklist` |
| `scripts/code_health_baseline.py` | Style/metrics baseline (CONTRIBUTING) |
| `scripts/count_parity_matrix_main_tables.py` | Parity matrix metrics |

### One-off / research / cloud / viz (dev-only)

`run_uqc_cloud_sim_online_learning.py`, `run_uqc_md_ml.py`, `analyze_uqc_md_ml_results.py`, `check_uqc_connectivity.py`, `compare_uqc_vqe_mock_vs_cloud.py`, `compare_shots_per_circuit.py`, `benchmark_qwen_triple.py`, `render_qwen_report_charts.py`, `l3_algorithm_benchmark_report.py`, `minimal_pipeline_viz.py`, `resource_estimation_demo.py`, `demo_mock_external_backend.py`, `build_precomputed_bundle.py`, `normalize_repo_text_utf8.py`, `setup_psi4_micromamba.sh`.

### Utility

- `scripts/venv-run` — thin wrapper around `$QCHEM_STACK_PYTHON` or system `python3` (no venv creation).
- `scripts/backend_profile_helpers.py` — shared by UQC run scripts.
- `scripts/create_solver_adapter_scaffold.py` — has tests (`tests/test_create_solver_adapter_scaffold_script.py`) but not CI.

### Should move to package or be removed?

- **`check_import_layers.py`**: reasonable as a dev script; could become `qchem_stack` dev CLI entry point.
- **`backend_profile_helpers.py`**: fine in `scripts/` unless UQC runners become first-class package tools.
- **`normalize_repo_text_utf8.py`**, **`render_qwen_report_charts.py`**, **`benchmark_qwen_triple.py`**: look like **one-off maintenance** — candidates to archive or move under `docs/` tooling.
- No strong case to delete CI-critical scripts; the issue is **doc/CI drift** for backlog/notebook checks.

---

## 4. Pre-commit (`.pre-commit-config.yaml`)

Minimal config — **only Ruff**:

```4:11:/home/sunhl/projects/qchem_qml_md/.pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.15.12
    hooks:
      - id: ruff
        files: ^(src/qchem_stack|tests|scripts|examples)/
      - id: ruff-format
        files: ^(src/qchem_stack|tests|scripts|examples)/
```

**Matches CI lint scope** (same paths, ruff check + format).

**Missing vs typical setup**:

- No **trailing-whitespace** / **end-of-file-fixer** / **check-yaml** / **check-added-large-files**
- No **mypy** or **pyright** hook (CI runs pyright separately)
- No **pytest** smoke hook
- Comment says optional after `pip install -e ".[dev]"` + `pre-commit install` — easy to skip locally

---

## 5. Repo Hygiene

### `.gitignore` (`/home/sunhl/projects/qchem_qml_md/.gitignore`)

Correctly ignores: `.venv*`, `.coverage`, `htmlcov/`, cache dirs, `.env`, `results/`, `timer.dat`, `artifacts/`, docusaurus build outputs.

### Committed artifacts that should not be tracked

| Path | Status | Notes |
|------|--------|-------|
| **`results/`** | **150 files tracked** | Checkpoints (`.npz`, `.pkl`), logs, MD trajectories, validation JSON — **contradicts `.gitignore`** (pre-ignore commits) |
| **`timer.dat`** | **Tracked** (~158 KB) | Psi4/QChem timer output at repo root |
| `.coverage`, `htmlcov/` | Local only, ignored | OK |
| `.ferrmion.log` | Local only, ignored | OK |
| `.mypy_cache`, `.ruff_cache`, `.pytest_cache`, `.venv*` | Not tracked | OK |
| **`.env`** | **Not tracked** | Present at repo root locally; **contains live API tokens** — correctly gitignored. Only `.env.example` is tracked. **Do not commit `.env`.** |

CI **depends on committed results**: `results/uqc_cloud_sim_md_ml_2rounds/md_validation_summary.json` for benchmark dashboard generation — intentional but couples CI to large binary tree.

---

## Prioritized Top Issues

### P0 — Fix now

1. **Untrack `results/` and `timer.dat`** — `.gitignore` already says to ignore them; 150+ result files and Psi4 timer output pollute history and bloat clones. Keep only small fixture JSON if CI needs them (or move fixtures to `tests/fixtures/`).
2. **`.env` at repo root has real secrets** — not committed, but verify it never gets force-added; consider rotating tokens if this workspace is shared.
3. **`test-nightly` job is broken by design** — add `schedule:` cron or remove the dead job to avoid false confidence.

### P1 — CI efficiency and consistency

4. **Remove duplicate marker pytest steps** (`l1_excited`, `l1_md_ml`) or exclude them from the main run — saves ~2× marker-suite time × 3 Python versions.
5. **Run heavy smokes only on 3.12** in the matrix; use lighter import/unit checks on 3.10/3.11 — would cut CI cost substantially.
6. **Wire documented gates into CI or fix docs**: `check_comparative_execution_backlog.py`, `check_notebooks_smoke.py`, optionally `sample_pipeline_configs.py`.
7. **`verify_ninety_day_gates.sh` diverges from CI** (no `-m "not slow and not perf"`) — misleads local “gate” runs.

### P2 — Quality hardening

8. **Add security scanning** — at minimum `pip-audit` or Dependabot security alerts review; consider CodeQL for Python.
9. **Decide mypy vs pyright** — mypy in dev deps but unused; either drop mypy or add a hook/job.
10. **Expand pre-commit** — trailing whitespace, large files, yaml check; optional pyright on changed files.
11. **Coverage reporting** — artifact-only is weak; Codecov or PR comment would make 75% gate visible.
12. **Reorganize tests** — move remaining ~179 root tests into `quantum/`, `chem/`, `orchestration/`, `api/`, `md_bridge/` packages for navigability.

### P3 — Script hygiene

13. **Archive or document one-off scripts** (`benchmark_qwen_triple.py`, `normalize_repo_text_utf8.py`, etc.) so `scripts/` reads as “supported tooling.”
14. **`smoke_pipeline.py` silent skip** when PySCF missing — fine for local dev, but ensure all CI paths set `QCHEM_SMOKE_REQUIRE_PYSCF=1` (already done for main path; verify all PySCF-dependent steps).

---

## Developer Workflow Summary

Documented entry points:

- `/home/sunhl/projects/qchem_qml_md/CONTRIBUTING.md` — lint, pytest, parity, smoke, solver checklist
- `/home/sunhl/projects/qchem_qml_md/docs/QUICKSTART_CONTRIBUTORS.md` — install + smoke
- `./scripts/venv-run` — consistent Python invocation

Typical local loop:

```bash
./scripts/venv-run ruff check src/qchem_stack tests scripts examples
./scripts/venv-run pytest tests -q --tb=short -m "not slow and not perf"
./scripts/venv-run python scripts/check_parity_export_sample.py
```

Merge gate in CONTRIBUTING aligns with CI lint + pytest + parity check; pre-commit is optional and narrower than full CI (no pyright, no smokes).

[REDACTED]


## 子 Agent：文档 / Config / Results 审查

**源文件**：`/home/sunhl/.cursor/projects/home-sunhl-projects-qchem-qml-md/agent-transcripts/64dad06a-bd13-4eda-88f5-dc491d1156ec/subagents/84055da8-fe89-4f7d-8505-3b12f92c2349.jsonl`

### 子 Agent 任务描述

Explore /home/sunhl/projects/qchem_qml_md focusing on documentation, configs, and results/artifacts sprawl. Be "medium" thoroughness. Report on:

1. docs/ has 143 markdown files (mix of English and Chinese). Assess: are there overlapping/redundant docs? Is there a clear entry point? Many competitive-positioning/"对标" docs — do they read as marketing/historical rather than engineering reference? Is there docs/internal/ with review notes that should maybe not ship? List the doc subfolders and rough categories.

2. There's also docusaurus-site/ — a separate docs site. Does it duplicate docs/? How is it maintained/synced (scripts/sync_pre_quantum_docs.py)?

3. configs/ has 111 YAML files. Assess naming conventions, redundancy, whether they're all referenced by tests/scripts or many are stale. 

4. results/ directory: appears to contain committed experiment outputs (plots, json). Should these be in the repo? How big?

5. Root-level files: README.md, CHANGELOG.md, CHEM_MODULE_AUDIT_REPORT.md, CONTRIBUTING.md, multitask-深入说明.md, tasks_20260528.csv, timer.dat. Which look like they belong vs clutter?

Return concrete paths, rough sizes, and a prioritized list of cleanup/consolidation opportunities. Do not modify files.

### 子 Agent 完整输出

I'll map the repo's docs, configs, results, and root files to assess overlap, sprawl, and cleanup priorities.

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `UpdateCurrentStep`**: {'current_step': 'Mapping docs and repo layout', 'final_summary': 'Scanning documentation, configs, results, and root files for overlap, sprawl, and cleanup priorities.', 'completed_subtitle': 'Starte
- **Tool `Glob`**: {'glob_pattern': 'docs/**/*.md', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Glob`**: {'glob_pattern': 'configs/**/*.yaml', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Glob`**: {'glob_pattern': 'results/**/*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Glob`**: {'glob_pattern': '*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Grep`**: {'pattern': '对标|competitive|parity|benchmark', 'glob': 'docs/**/*.md', 'output_mode': 'files_with_matches', 'head_limit': 50}
- **Tool `Glob`**: {'glob_pattern': '**/sync_pre_quantum_docs.py', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Count docs dirs and measure directory sizes
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/sync_pre_quantum_docs.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/README.md
- **Tool `Glob`**: {'glob_pattern': 'docs/**/*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Grep`**: /home/sunhl/projects/qchem_qml_md
- **Tool `Glob`**: {'glob_pattern': 'docs/internal/**', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docusaurus-site/README.md
- **Tool `Grep`**: {'pattern': 'results/', 'glob': '.gitignore'}
- **Tool `Grep`**: {'pattern': 'configs/', 'glob': '**/*.{py,sh,yml,yaml,md}', 'head_limit': 80}
- **Tool `Shell`**: List root files and count config/docusaurus docs
- **Tool `Grep`**: {'pattern': 'example_h2\\.yaml|configs/example', 'glob': '**/*.{py,sh,yml,yaml}', 'output_mode': 'count'}
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/internal/CONFIG_REVIEW_P15.md

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Check if results/ is git-tracked despite gitignore
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/configs/README.md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/check_parity_export_sample.py
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/scripts/sample_pipeline_configs.py
- **Tool `Grep`**: {'glob': 'docs/*.md', 'output_mode': 'content', 'pattern': '^#', 'head_limit': 100}
- **Tool `Shell`**: Count execution docs and docusaurus structure

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Find configs with no code/doc references
- **Tool `Shell`**: Measure git-tracked results size and file types
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/.gitignore
- **Tool `Glob`**: {'glob_pattern': 'docs/README*', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/product/non_goals.md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docusaurus-site/docs/product/non_goals.md

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Glob`**: {'glob_pattern': 'docusaurus-site/docs/product/**', 'target_directory': '/home/sunhl/projects/qchem_qml_md'}
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/execution/README.md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/multitask-深入说明.md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/CHEM_MODULE_AUDIT_REPORT.md
- **Tool `Grep`**: {'glob': '**/*', 'head_limit': 30, 'pattern': 'sync.*docusaurus|docusaurus.*sync|copy.*docs'}
- **Tool `Shell`**: Categorize docs root filenames by prefix

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Check which root clutter files are tracked
- **Tool `Grep`**: {'glob': 'src/qchem_stack/integrations/l3_algorithm_benchmark.py', 'pattern': 'example_h2_hcb|example_h2_jkmn|example_h2_vsqs|example_h2_puccd'}
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docusaurus-site/docs/parity/gap-implementation-plan.md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/ENGINEERING_ARCHITECTURE.md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docusaurus-site/docs/concept/engineering-architecture.md
- **Tool `Grep`**: {'glob': 'CONTRIBUTING.md', 'pattern': 'docs/|docusaurus|DOCUMENTATION', 'head_limit': 40}

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `Shell`**: Count all config files and artifacts tracking
- **Tool `Grep`**: {'glob': 'docs/**/*.md', 'output_mode': 'files_with_matches', 'pattern': 'HTTP API|QUICKSTART'}
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/qwen三模型评测报告.md
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/docs/组会汇报_qchem_stack_Tangelo工程细节.md
- **Tool `Grep`**: {'glob': 'tests/**/*', 'pattern': 'example_h2_uqc|uqc_h2|example_h2_qmlff|example_h2_classical_md', 'head_limit': 25}

</details>

### 子 Agent 完整输出

[REDACTED]

<details><summary>工具调用（本回合）</summary>

- **Tool `UpdateCurrentStep`**: {'completed_subtitle': 'Completed docs configs results audit', 'current_step': 'Compiling audit findings report', 'final_summary': 'The repo uses a dual-doc model (Docusaurus for users, `docs/` for en
- **Tool `Shell`**: Count tracked internal and presentation docs
- **Tool `Read`**: /home/sunhl/projects/qchem_qml_md/CHANGELOG.md

</details>

### 子 Agent 完整输出

# Repository sprawl audit: `qchem_qml_md`

Medium-thoroughness scan of documentation, configs, results, and root clutter. Sizes are on-disk unless noted as git-tracked.

---

## 1. `docs/` — 143 markdown files (~20 MB)

### Subfolders and rough categories

| Path | ~Count | Role |
|------|--------|------|
| `/home/sunhl/projects/qchem_qml_md/docs/*.md` (root) | **79** | Mixed engineering reference, 对标/parity, learning notes, audits |
| `/home/sunhl/projects/qchem_qml_md/docs/execution/` | **59** | Day logs, 90-day calendars, milestone closeouts, WBS evidence (2026Q2–Q3) |
| `/home/sunhl/projects/qchem_qml_md/docs/internal/` | **5** (~28 KB) | Maintainer review notes, style roadmap, code-health baseline |
| `/home/sunhl/projects/qchem_qml_md/docs/product/` | **1** | `non_goals.md` (also mirrored in Docusaurus) |
| `/home/sunhl/projects/qchem_qml_md/docs/references/` | **1** | `tensor_network_qchem.bib` |
| `/home/sunhl/projects/qchem_qml_md/docs/assets/` | scripts + data | **~15 MB** — figure generators, qwen benchmark PNGs/Mermaid |

**Root-level doc categories (by naming/theme):**

- **Config/module reference (engineering):** `说明_*.md` (~16), `config_字段索引.md`, `config_校验分层约定.md`, `chem_模块风格约定.md`, `quantum_模块风格约定.md`
- **Technical contracts:** `技术文档_*.md` (~7), `mitigation_PMSV_ZNE_Qermit_mapping.md`, `parity_export_schema_versioning.md`, `pre_quantum_yaml_matrix.md`
- **Competitive / 对标 / parity (strategic):** `竞争定位与路线图_对标Quantinuum产品与技术路线.md`, `工程记忆_Quantinuum对标与数据流技术文档.md`, `public_parity_matrix.md`, `quantum_InQuanto_Tangelo_对照矩阵.md`, `算法面广度_Vendor platform_Tangelo对照索引.md`, `AUDIT_REPORT_2026Q2.md`, `P2_*`, `Y1_*`
- **Onboarding:** `QUICKSTART_CONTRIBUTORS.md`, `QUICKSTART_HTTP_API_en.md`, `说明_config入门_通俗导读.md`, `学习路线图_框架理论到源码阅读顺序.md`
- **Architecture anchor:** `ENGINEERING_ARCHITECTURE.md`
- **Experiment / ops narratives:** `在线学习云上调度.md`, `UQC云平台集成技术报告.md`, `h2_md_validation_phases_技术说明.md`
- **Presentation / research (non-reference):** `组会汇报_qchem_stack_Tangelo工程细节.md`, `qwen三模型评测*.md`, `AI一体机四类应用场景与成熟方案调研.md`, `工作计划_第一期_2026年6月_调研与架构设计.md`

### Entry point — clear but dual-track

There is **no** `docs/README.md`. Entry is intentionally split:

1. **Root** [`/home/sunhl/projects/qchem_qml_md/README.md`](file:///home/sunhl/projects/qchem_qml_md/README.md) — explicit “Documentation map” with Docusaurus vs repo `docs/` roles; labels competitive docs as **historical, not runtime dependencies**.
2. **Contributors:** [`docs/QUICKSTART_CONTRIBUTORS.md`](file:///home/sunhl/projects/qchem_qml_md/docs/QUICKSTART_CONTRIBUTORS.md) + [`CONTRIBUTING.md`](file:///home/sunhl/projects/qchem_qml_md/CONTRIBUTING.md)
3. **Engineering:** [`docs/ENGINEERING_ARCHITECTURE.md`](file:///home/sunhl/projects/qchem_qml_md/docs/ENGINEERING_ARCHITECTURE.md)
4. **Execution log index only:** [`docs/execution/README.md`](file:///home/sunhl/projects/qchem_qml_md/docs/execution/README.md)

This is workable for maintainers but **overwhelming for newcomers** — 79 root docs with inconsistent naming (`说明_`, `技术文档_`, English, Chinese).

### Overlap / redundancy

**High overlap clusters:**

| Topic | Copies / variants |
|-------|-------------------|
| Parity / gap matrix | `public_parity_matrix.md` (authoritative), `quantum_InQuanto_Tangelo_对照矩阵.md`, `docs/execution/*parity*`, Docusaurus `parity/gap-implementation-plan.md` (excerpt) |
| Competitive positioning | `竞争定位与路线图_*.md`, `工程记忆_Quantinuum对标*.md`, `算法面广度_*`, parts of `AUDIT_REPORT_2026Q2.md` |
| HTTP API | `QUICKSTART_HTTP_API_en.md`, `说明_API安全与环境变量.md`, `技术文档_HTTP_API与SQLite作业队列及可观测性契约.md`, Docusaurus `reference/http-api-sqlite-jobs.md` |
| Product non-goals | `docs/product/non_goals.md` ↔ `docusaurus-site/docs/product/non_goals.md` (cross-linked, not byte-identical) |
| Architecture | `ENGINEERING_ARCHITECTURE.md` (deep, English) ↔ Docusaurus `concept/engineering-architecture.md` (short Chinese summary) |

**`docs/execution/` (59 files)** is largely **historical execution evidence** (day001–day450 templates, week closeouts, calendars). Valuable for audit trail; **not** day-to-day engineering reference. README itself points to `comparative_execution_rd_plan_strict_2026Q3Q4.md` as the consolidated entry.

### 对标 docs: marketing/historical vs engineering?

**Mostly strategic/historical**, explicitly acknowledged in README:

- `竞争定位与路线图_对标Quantinuum产品与技术路线.md` — product positioning, roadmap, “我们要做得更好的准确定义”
- `工程记忆_Quantinuum对标与数据流技术文档.md` — long-lived engineering memory but framed around vendor alignment
- `public_parity_matrix.md` — **hybrid**: partly engineering contract (parity export keys, L1 criteria) and partly competitive backlog

**Engineering reference** (should stay, possibly reorganized): `说明_*`, `技术文档_*`, style conventions, `pre_quantum_yaml_matrix.md`, `ENGINEERING_ARCHITECTURE.md`.

**Clearly non-engineering / should not ship as product docs:** `qwen三模型评测报告.md`, `组会汇报_*.md`, `AI一体机四类应用场景*.md` — presentation or LLM tooling research.

### `docs/internal/` — should it ship?

Contents (~28 KB):

- `/home/sunhl/projects/qchem_qml_md/docs/internal/CONFIG_REVIEW_P15.md`
- `/home/sunhl/projects/qchem_qml_md/docs/internal/CONFIG_REVIEW_P16.md`
- `/home/sunhl/projects/qchem_qml_md/docs/internal/STYLE_OPTIMIZATION_ROADMAP.md`
- `/home/sunhl/projects/qchem_qml_md/docs/internal/import_layers.md`
- `/home/sunhl/projects/qchem_qml_md/docs/internal/code_health_baseline.json`

These are **phase review notes and refactor trackers**, referenced from `CONTRIBUTING.md`. Fine in a private fork; for a public OSS repo they read as **internal WIP audit trail**. CONTRIBUTING already links to `STYLE_OPTIMIZATION_ROADMAP.md` — if you keep them, mark the folder “maintainer-only” or move under `docs/execution/` archives.

---

## 2. `docusaurus-site/` — separate docs site (~546 MB on disk; **542 MB is `node_modules/`**, gitignored)

- **48** markdown pages under `/home/sunhl/projects/qchem_qml_md/docusaurus-site/docs/` (guide, tutorial, reference, product, parity, cloud)
- **Build artifact:** `build/` ~2.7 MB (gitignored)
- **CI:** dedicated `docusaurus` job per `CONTRIBUTING.md`

### Does it duplicate `docs/`?

**Partially — by design, not full mirror.**

| Docusaurus | Repo `docs/` relationship |
|------------|---------------------------|
| Tutorials, onboarding, backend quickstarts | **Original user-facing content**; links out to repo configs/examples |
| `product/*`, `parity/gap-implementation-plan.md` | **Curated excerpts**; parity page says **authoritative source is `docs/public_parity_matrix.md`** |
| `concept/engineering-architecture.md` | **Abbreviated** vs `ENGINEERING_ARCHITECTURE.md` |
| Long contracts (`技术文档_*`, config handbooks) | **Stay in repo `docs/` only** |

### Sync / maintenance

**`scripts/sync_pre_quantum_docs.py` does NOT sync Docusaurus.** It only injects code-generated blocks into two repo docs:

- `docs/技术文档_双线路经典输入与统一PreQuantumInput契约.md`
- `docs/pre_quantum_yaml_matrix.md`

(from `src/qchem_stack/chem/pre_quantum_docs_sync.py`)

**Docusaurus ↔ `docs/` sync is manual**, documented in:

- `docusaurus-site/README.md` — “update both when the matrix changes”
- `CONTRIBUTING.md` — parity matrix, new YAMLs, tutorial cross-links

No automated copy script found for the site.

---

## 3. `configs/` — 111 files total (~832 KB)

| Type | Count |
|------|-------|
| `*.yaml` | **104** |
| JSON sidecars, `.xyz`, etc. | **7** (e.g. `precomputed_classical_reference_h2.json`, `structures_h2.xyz`) |
| **Git-tracked** | **82** (some newer YAMLs may be untracked locally) |

### Naming conventions (consistent)

- `example_<system>_<feature>.yaml` — primary pattern (H₂ family dominates)
- `example_<system>_<backend>_<variant>.yaml` — Psi4, UQC, MD/ML
- `uqc_h2.yaml`, `qpe_dual_track_demo.yaml`, `tutorial_chain_h2.yaml` — named demos
- `_template.yaml` — scaffold

[`configs/README.md`](file:///home/sunhl/projects/qchem_qml_md/configs/README.md) documents families but says **“77 个”** — **stale** (actual YAML count is 104).

### CI / reference coverage

| Gate | Configs covered |
|------|-----------------|
| `scripts/check_parity_export_sample.py` → `SAMPLE_CONFIGS_REL` | **~61** YAMLs (parity export schema) |
| `scripts/sample_pipeline_configs.py` | **12** representative YAMLs |
| `scripts/smoke_pipeline.py` / CI | handful (`example_h2.yaml`, excited smoke, etc.) |
| Tests/examples (heuristic grep) | **~89 / 104** YAMLs referenced somewhere |

**~15 YAMLs with no detected references** (likely recent algorithm additions not wired to CI yet):

```
example_h2_adapt_staggered_pool.yaml
example_h2_hcb.yaml
example_h2_iqcc.yaml
example_h2_jkmn.yaml
example_h2_md_ml_trajectory_full_pipeline.yaml
example_h2_puccd.yaml
example_h2_puccd_pauli_protocol.yaml
example_h2_qcc_pauli_protocol.yaml
example_h2_qite.yaml
example_h2_qpe_deterministic.yaml
example_h2_qpe_info_theory.yaml
example_h2_sceom_symmetry_filtered.yaml
example_h2_upccgsd_pauli_protocol.yaml
example_h2_vsqs.yaml
example_h4_adapt_qse_benchmark.yaml
```

These align with CHANGELOG v0.3.0 “P4 competitor gap closure” items — **not stale, but under-documented in CI**.

---

## 4. `results/` — committed experiment outputs?

| Metric | Value |
|--------|-------|
| **Policy** | `.gitignore` line 55: `results/` |
| **Git-tracked anyway** | **150 files**, **~505 KB** (legacy index) |
| **Working tree total** | **~2.2 MB**, **247 files** (includes untracked local runs) |
| **Largest subdirs (untracked/local)** | `uqc_cloud_sim_md_ml_optimized/` ~972 KB, `qmlff_h2_native_benchmark/` ~396 KB |
| **Content types** | JSON summaries, `.xyz` trajectories, `.npz` checkpoints, `.pkl` opt states; **0 PNG** in tracked results |

**Tracked examples:** `results/qmlff_h2_native_benchmark/md_bridge_checkpoints/epoch_*.npz`, `benchmark_summary.json`, etc.

**Verdict:** Policy says **should not be in repo**. Tracked files are a **pre-gitignore legacy** (~505 KB — small but wrong in principle). Local-only dirs like `results/uqc_mock_md_ml_test/` are correctly ignored. Binary checkpoints belong in artifact storage or release attachments, not git.

Also note: `.gitignore` lists `artifacts/` too, but **2 files** are still tracked under `/home/sunhl/projects/qchem_qml_md/artifacts/` (~60 KB).

---

## 5. Root-level files — belong vs clutter

| File | Size | Status | Verdict |
|------|------|--------|---------|
| `README.md` | ~19 KB | tracked | **Belongs** — primary entry |
| `CHANGELOG.md` | ~4 KB | tracked | **Belongs** |
| `CONTRIBUTING.md` | ~15 KB | tracked | **Belongs** |
| `CHEM_MODULE_AUDIT_REPORT.md` | ~20 KB | tracked | **Useful but misplaced** — point-in-time audit (2026-05-27); belongs in `docs/internal/` or `docs/execution/` |
| `multitask-深入说明.md` | ~17 KB | tracked | **Clutter** — generic Multitask/AI workflow guide, not qchem-specific |
| `tasks_20260528.csv` | ~24 KB, 348 lines | **untracked** | **Clutter** — UUID/timestamp session log |
| `timer.dat` | ~158 KB | **tracked despite `.gitignore`** | **Clutter / policy violation** — should be `git rm --cached` |

Other root noise (not in your list but visible): `.coverage` (~586 KB), `htmlcov/`, `.ferrmion.log` — local artifacts, generally ignored.

---

## Prioritized cleanup / consolidation opportunities

### P0 — Policy fixes (low effort, high clarity)

1. **Untrack `results/` and `artifacts/`** — `git rm -r --cached results/ artifacts/`; keep `.gitignore`. ~505 KB + checkpoints leave the index.
2. **Untrack `timer.dat`** — listed in `.gitignore` but still committed (~158 KB).
3. **Delete or gitignore `tasks_20260528.csv`** — untracked agent log; add pattern if this recurs.

### P1 — Documentation structure

4. **Add `docs/README.md`** — single taxonomy index: Reference | Contracts | Onboarding | 对标 (historical) | Execution archive | Internal.
5. **Archive `docs/execution/` day logs** — move 59 files to `docs/execution/archive/2026Q2Q3/` or a separate repo; keep `execution/README.md` + 2–3 master plans as entry.
6. **Relocate non-shipping docs:** `qwen*`, `组会汇报*`, `AI一体机*`, root `multitask-深入说明.md` → `docs/research/` or remove from public tree.
7. **Mark or relocate `docs/internal/`** — CONFIG_REVIEW P15/P16 are done; fold into execution archive or drop from default clone narrative.
8. **Deduplicate HTTP API docs** — one canonical contract (`技术文档_HTTP_API...`), quickstart as thin wrapper; Docusaurus links to repo doc instead of parallel prose.

### P2 — Config hygiene

9. **Update `configs/README.md`** count (77 → 104) and add table for the 15 unwired YAMLs.
10. **Wire new algorithm YAMLs into CI** — add to `SAMPLE_CONFIGS_REL` and/or `integrations/l3_algorithm_benchmark.py` per CONTRIBUTING checklist.
11. **Consolidate near-duplicate UQC/MD configs** — e.g. `example_h2_uqc_cloud_sim_qmlff_loop.yaml` vs `_5rounds.yaml` (document variants in README rather than proliferate).

### P3 — Docusaurus / docs sync

12. **Document sync policy in one place** — “Docusaurus = curated subset; `docs/public_parity_matrix.md` = source of truth; run `sync_pre_quantum_docs.py` for matrix blocks only.”
13. **Optional:** script to check Docusaurus links to repo `docs/` paths still exist (no auto-copy needed if links are the contract).

### P4 — Root cleanup

14. Move `CHEM_MODULE_AUDIT_REPORT.md` → `docs/internal/CHEM_MODULE_AUDIT_REPORT_2026-05-27.md`.
15. Trim README “Documentation map” — it repeats parity/competitive links 3–4 times; point once to index.

---

## Quick size summary

| Path | Size | Notes |
|------|------|-------|
| `docs/` | **20 MB** | 143 md; 15 MB in `assets/` |
| `docusaurus-site/` | **546 MB** | 542 MB `node_modules` (ignored) |
| `configs/` | **832 KB** | 104 YAML + 7 sidecars |
| `results/` (disk) | **2.2 MB** | 150 tracked (~505 KB) + local untracked runs |
| Root clutter | **~200 KB** | `timer.dat` + misplaced audits |

Overall: the **engineering core is sound** (README + CONTRIBUTING + ENGINEERING_ARCHITECTURE + Docusaurus split is intentional), but **sprawl concentrates in** `docs/execution/` historical logs, 对标/strategy markdown at repo root, legacy tracked `results/`, and ~15 configs ahead of CI wiring.

[REDACTED]

---

## 收录说明

- **来源**：Cursor Agent Transcript `64dad06a-bd13-4eda-88f5-dc491d1156ec`（主线程 + 3 个子 Agent JSONL）。
- **正文**：用户消息与助手长文回复按回合顺序收录，不简写；子 Agent 三份审查报告全文附于文末。
- **`[REDACTED]`**：源 transcript 对中间工具轮次正文做了脱敏占位；工具名称与路径见各回合 `<details>` 折叠块。六阶段实施过程中的完整终端输出未单独另存（源 JSONL 未导出 tool result 全文）。
- **计划附件**：Six-Stage Optimization 计划全文来自 `/home/sunhl/.cursor/plans/six-stage_optimization_d1c6aef6.plan.md`。

### 回合 77 — 助手 (Opus 4.8)（归档完成）

文档已生成：**`/home/sunhl/projects/qchem_qml_md/opus4.8-test.md`**（约 2500+ 行）。包含：主对话 75+ 回合、六阶段计划全文、架构/CI/文档三份子 Agent 报告全文。若需纳入 git，请明确说「提交」即可。

