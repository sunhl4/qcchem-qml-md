---
title: 更新日志
description: 产品发布摘要（1.1.0 / 1.0.0）与文档站双轨更新记录。
keywords:
  - changelog
  - release notes
  - 文档更新
---

# 更新日志

双轨记录：**（A）产品包发布**摘要；**（B）文档站**迭代。完整产品变更见仓库 [CHANGELOG.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/CHANGELOG.md)。

---

## A. 产品发布摘要

### [1.1.0] — 2026-06-15

- Wheel 捆绑 configs（`config_paths.default_configs_dir()`）；GitHub Pages 文档部署
- Release 硬化：`check_doc_test_paths.py`、扩展 `release_precheck.sh`、覆盖率地板对齐
- Jobs / 可观测性：Postgres 协议 CI、OTel compose 示例、DMET/RHF 校验提示
- **移除** `integrations.compat.*` re-export shims
- 默认禁用未签名 legacy pickle；迁移脚本 + 临时 `QCHEM_ALLOW_LEGACY_PICKLE=1`

### [1.0.0] — 2026-06-05

- 稳定 integrator facade [`qchem_stack.sdk`](https://github.com/sunhl4/qcchem-qml-md/blob/main/src/qchem_stack/sdk/__init__.py)
- 控制台脚本 `qchem-run` / `qchem-export-parity`；HTTP `api_contract_version: "1.0"`
- P0–P3 工程波：StrEnum shim、parity 导出、ADAPT/IQEB/DMET L1 YAML、import-linter
- **破坏性移除**（自 v0.8）：Schmidt sidecar、`molecular_hamiltonian_from_pyscf` 等（详见完整 CHANGELOG）

完整条目与更早版本：[CHANGELOG.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/CHANGELOG.md)。

---

## B. 文档站笔记

### 2026-07-14

- **P0–P2 手册扩容**：FAQ、术语表、安装档位、Pre-quantum YAML 矩阵摘要、配置字段分节、English bridge、实用 API surface
- 配置参考页自仓库 `docs/config_reference_*.md` 迁入本站，并改写 GitHub 绝对链接

### 2026-05-28

- 新增 UQC backend、MD/ML 主动学习、Psi4 后端、configs 目录页
- 同步 HTTP API 文档至 `product-surface` / `capability_surface_v2`
- 新增 parity gap implementation plan 节选页
- 仓库侧：P0–P3 优化（模块拆分、UQC 单元测试、CI 硬化、迁移指南）

### 2026-04-30

- 新建 Docusaurus 版本文档站
- 完成产品、指南、教程、参考与云主结构迁移
- 完成首页与全局 UI 的第一轮和第二轮美化
- 新增发布级入口：更新日志、品牌资产与统计信息展示
- 首页指标改为自动统计，新增部署与验收清单
- 增补 SEO 元信息与可访问性（focus/reduced-motion）优化

---

## 维护约定

- 产品语义版本变更 → 更新 **A**（或链到根 CHANGELOG）
- 文档站结构调整 → 追加 **B**
- 重大变更应附带影响范围与迁移说明
