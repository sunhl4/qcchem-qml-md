---
title: 配置字段索引
description: ExperimentConfig 各 section 字段参考页入口。
keywords:
  - ExperimentConfig
  - config fields
  - YAML
---

# 配置字段索引

`schema_version: "2"` 下各顶层块的字段速查。完整工程手册仍以仓库 `docs/说明_config模块技术参考手册.md` 为准；本站为迁移后的分节页。

| 页面 | Section | 说明 |
|------|---------|------|
| [molecule](./molecule) | `molecule` | 几何、电荷、多重度、基组 |
| [scf](./scf) | `scf` | driver / method / precomputed `bundle_path` |
| [active-space](./active-space) | `active_space` | `strategy`、CAS、映射 |
| [embedding](./embedding) | `embedding` | DMET / projection / plugin |
| [quantum](./quantum) | `quantum` | 算法、ansatz、Pauli、激发态 |
| [backend](./backend) | `backend` | provider、shots、CI 矩阵 |
| [mitigation](./mitigation) | `mitigation` | ZNE、PMSV、stubs |
| [compiler](./compiler) | `compiler` | 优化等级与 pass |
| [chemistry-extended](./chemistry-extended) | `chemistry_extended` | 溶剂、PBC、AVAS、CASSCF |
| [sidecars](./sidecars) | sidecars | nexus / parity / md_ml_export |

---

## 相关

- [config 模块](/modules/config) · [配置目录](/reference/configs-catalog)
- [Pre-quantum 矩阵](/reference/pre-quantum-yaml-matrix) · [FAQ](/faq/)
- 仓库索引：[说明_config模块技术参考手册.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/说明_config模块技术参考手册.md)
