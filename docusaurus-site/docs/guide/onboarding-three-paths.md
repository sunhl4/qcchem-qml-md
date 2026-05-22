---
title: 新用户三条路径
description: 根据你的目标选择上手路径：先跑通、先规划、先工程集成。
---

# 新用户三条路径

## 路径 A：先跑通一条量子化学管线

适合：先看到可运行结果，再回头补架构的同学。

1. [15 分钟上手](/tutorial/quickstart)  
2. [工作流与 YAML 概览](/tutorial/workflow)  
3. 继续阅读 [案例：H2 家族](/tutorial/case-study-h2-family) 或 [UCCSD Trotter 导出](/tutorial/uccsd-trotter-export)

**经典化学双后端（PySCF 默认 / Psi4 可选）**：仓库 `configs/` 下 H₂ 示例包括 `example_h2.yaml`（PySCF）、`example_h2_psi4_rhf_sto3g.yaml`（Psi4 canonical）、`example_h2_psi4_schmidt_dmet.yaml`、`example_h2_psi4_avas.yaml`、`example_h2_psi4_projection_mulliken.yaml`。Psi4 需本地 micromamba 环境；CI 用 `pytest -m psi4` 验证。

## 路径 B：先理解规划与契约

适合：需要维护导出键、验收文档与路线图的维护者。

1. [产品定位与路线](/product/positioning)  
2. [工程架构](/concept/engineering-architecture)  
3. [路线图](/product/roadmap)

## 路径 C：先做工程集成与自动化

适合：负责 API、作业队列、脚本集成的工程同学。

1. [P4 作业与可复现](/guide/jobs-and-reproducibility)  
2. [HTTP API 与 SQLite 作业](/reference/http-api-sqlite-jobs)  
3. [命令行与脚本](/reference/cli-and-scripts)

---

维护建议：每次新增教程或参考页时，同步检查本页三条路径是否需要补链。
