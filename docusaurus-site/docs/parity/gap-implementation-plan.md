---
title: 能力差距与实施计划
description: 摘自仓库 docs/public_parity_matrix.md 的公开差距摘要与维护约定。
---

# 能力差距与实施计划

本文是 [`docs/public_parity_matrix.md`](https://github.com/yaozheng/qchem-stack/blob/main/docs/public_parity_matrix.md) 的 Docusaurus 节选。**权威母稿**以仓库 `docs/public_parity_matrix.md` 为准。

## 维护约定

- 新增或重命名 YAML 能力字段时，同步 `qchem_stack.protocols.product_contract` 中的 `PARITY_EXPORT_V3_STABLE_KEYS` 与 `scripts/check_parity_export_sample.py`。
- HTTP **`GET /v1/meta/capability-surface`** 返回 `schema: capability_surface_v2`，与 `tests/test_api_runs.py::test_capability_surface_matches_product_contract` 同源对拍。
- **`GET /v1/meta/parity-gaps`** 返回 `capability_gap_export_v1`（仅 gaps 列表）。

## 差距类别（摘要）

| 类别 | 状态 | 说明 |
|------|------|------|
| 经典化学多后端 | partial | PySCF 为 CI 数值主路径；Psi4 可选 |
| UCCSD BK/SCBK 电路 | n/a | JW 路径完整；BK/SCBK UCCSD Trotter 未包装 |
| 激发态 (VQD/QSE/SCEOM) | partial→yes | statevector + Qiskit shot 路径可测 |
| Pauli 协议五阶段 | yes | `PauliAveragingProtocol` + shot modes |
| UQC 云平台 | partial | mock + cloud sim；见 [UQC 集成报告](https://github.com/yaozheng/qchem-stack/blob/main/docs/UQC云平台集成技术报告.md) |
| MD/ML 闭环 | partial | `md_bridge` + QML-FF 可选 sibling 安装 |
| Nexus / 商业云 parity | n/a | 开放栈不对标闭源 bundle |

完整表格、L1 判据与 YAML 示例索引见仓库 [`docs/public_parity_matrix.md`](https://github.com/yaozheng/qchem-stack/blob/main/docs/public_parity_matrix.md)。
