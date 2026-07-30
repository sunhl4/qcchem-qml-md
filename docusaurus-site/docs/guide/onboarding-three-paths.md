---
title: 新用户三条路径
description: 根据你的目标选择上手路径：先跑通、先规划、先工程集成。
---

# 新用户三条路径

:::tip 模块手册
任务向阅读顺序 → [reading-paths](/modules/reading-paths) · FAQ / 导航 → [手册总览](/guide/) · [模块总览](/modules/)
:::

按目标选一条路径；每条都链到教程、指南与模块手册，避免只读 YAML 不读契约。

## 路径 A：先跑通一条量子化学管线

适合：先看到可运行结果，再回头补架构的同学。

1. [15 分钟上手](/tutorial/quickstart)
2. [工作流与 YAML 概览](/tutorial/workflow)
3. 继续：[案例：H2 家族](/tutorial/case-study-h2-family) 或 [UCCSD Trotter 导出](/tutorial/uccsd-trotter-export)
4. 选型回看：[P1 化学与嵌入](./chemistry-and-embedding) → [P2 程序构建](./program-construction)

**经典化学双后端（PySCF 默认 / Psi4 可选）**：仓库 `configs/` 下 H₂ 示例包括 `example_h2.yaml`（PySCF）、`example_h2_psi4_rhf_sto3g.yaml`（Psi4 canonical）、`example_h2_psi4_schmidt_dmet.yaml`、`example_h2_psi4_avas.yaml`、`example_h2_psi4_projection_mulliken.yaml`。Psi4 需本地 micromamba 环境；CI 用 `pytest -m psi4` 验证。见 [Psi4 后端](./psi4-backend)。

**进阶烟测教程**：

| 主题 | 教程 | 代表 YAML |
|------|------|-----------|
| ADAPT 池 | [adapt-pool-smoke](../tutorial/adapt-pool-smoke) | `example_h2_adapt_singles_pool.yaml` |
| QPE track | [qpe-track](../tutorial/qpe-track) | `example_h2_qpe_track.yaml` |
| DMET 自洽 | [dmet-self-consistent](../tutorial/dmet-self-consistent) | `example_h4_dmet_self_consistent.yaml` |
| GQE 变体 | [gqe-variants](../tutorial/gqe-variants) | `example_h2_gqe_*.yaml` |
| ONIOM | [oniom-smoke](../tutorial/oniom-smoke) | `example_oniom_toy.yaml` |

## 路径 B：先理解规划与契约

适合：需要维护导出键、验收文档与路线图的维护者。

1. [产品定位与路线](/product/positioning)
2. [工程架构](/concept/engineering-architecture)（含管线阶段图）
3. [parity / repro 契约](./parity-repro-contract)
4. [路线图](/product/roadmap)
5. 模块契约：[contracts](/modules/contracts) · [repro](/modules/repro)

## 路径 C：先做工程集成与自动化

适合：负责 API、作业队列、脚本集成的工程同学。

1. [P4 作业与可复现](/guide/jobs-and-reproducibility)
2. [HTTP API 与 SQLite 作业](/reference/http-api-sqlite-jobs)
3. [命令行与脚本](/reference/cli-and-scripts)
4. [HTTP 异步教程](/tutorial/async-run-via-http)
5. 模块：[jobs](/modules/jobs) · [api-sdk](/modules/api-sdk) · [云概览](/cloud/overview)

## 与「按任务阅读」的关系

| 你想… | 去 |
|-------|-----|
| 按**任务**选模块章 | [modules/reading-paths](/modules/reading-paths) |
| 按**角色**选指南 | [role-based-paths](./role-based-paths) |
| 看**全部指南地图** | [overview](./overview) · [手册总览](./) |
| 查 FAQ 式原理顺序 | [principles-and-reading](./principles-and-reading) |

## 验证你选对了路径

```bash
python3 -c "
from qchem_stack.config import load_experiment_config
c = load_experiment_config('configs/example_h2.yaml')
print('path-A-ok', c.experiment_id)
"
```

期望：打印 `path-A-ok` 与非空 experiment id（路径 A 最小门槛）。

## 路径对照表（避免走错）

| 如果你… | 优先路径 | 不要先读 |
|---------|----------|----------|
| 还没跑过任何 YAML | A | 云配额 / 路线图细节 |
| 要改 HTTP / worker | C | 深挖 ansatz 公式 |
| 要写 Methods / parity 表 | B → [parity-repro-contract](./parity-repro-contract) | 随机改后端 provider |
| 要选映射 / 嵌入 | A 跑通后 → [chemistry-and-embedding](./chemistry-and-embedding) | 同时开三种嵌入 |

## FAQ（短）

- **模块页和指南页有何区别？** 指南选型；模块给公式与 API。见 tip 中的 [reading-paths](/modules/reading-paths)。
- **教程缺验证块怎么办？** 见 [verify-block-template](../tutorial/verify-block-template)。
- **开源有没有强制多租户？** 没有；见 [cloud/overview](../cloud/overview) 警告框。
- **想一次看完所有指南页？** 打开 [overview](./overview) 四柱地图。
- **示例脚本在哪？** [示例馆](../examples/) → [gallery-body](../examples/gallery-body)。

## 建议收藏的五页

1. [getting-started](../getting-started)
2. [quickstart](../tutorial/quickstart)
3. [chemistry-and-embedding](./chemistry-and-embedding)
4. [algorithm-and-ansatz-menu](./algorithm-and-ansatz-menu)（短表）→ 深读进模块
5. [jobs-and-reproducibility](./jobs-and-reproducibility)（需要服务化时）

---

维护建议：每次新增教程或参考页时，同步检查本页三条路径与 [reading-paths](/modules/reading-paths) 是否需要补链。
