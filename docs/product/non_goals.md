# 未承诺项（Non-goals）

本页列出 **qchem-stack 刻意不对齐、不立项、不宣称等价** 的能力。若 issue 或 PR 涉及下列范围，请先阅读本页再讨论是否属于社区贡献范围。

## 商业云与身份

| 范围 | 说明 |
|------|------|
| **Quantinuum Nexus / qnexus** | 不实现厂商云 SDK、项目 IAM、OAuth 或真队列 SLA |
| **HQC 计价与合同配额** | 可提供 `nexus_analog` 本地账本 sidecar，**不**伪造 HQC 货币或计费 API |
| **H-Series 原生生态** | 不对齐专有校准、原生门集、拓扑专优或硬件 SLA |

本地 **FastAPI + SQLite** 作业类比见 [launch/retrieve Nexus 类比](../launch_retrieve_nexus_analog.md) 与 [HTTP API 契约](../技术文档_HTTP_API与SQLite作业队列及可观测性契约.md)；语义参考，非 1:1 替代。

## 闭源 L0 与 vendor bundle

| 范围 | 说明 |
|------|------|
| **商业 Qermit** | 不打包闭源 error-mitigation wheel；ZNE / 分组等开放路径见 parity 矩阵 |
| **cuTensorNet L0** | 不对标 NVIDIA cuTensorNet 闭源 L0 等价或默认启发式 |
| **闭源 InQuanto / Tangelo wheel parity** | 矩阵行保持 `n/a` 或 `partial + caveat`，不声称二进制等价 |

## 算法与经典后端（当前不排期）

- **BK / SCBK UCCSD Trotter 电路**：保持 `n/a`（见 Docusaurus [UCCSD Trotter 导出](../../docusaurus-site/docs/tutorial/uccsd-trotter-export.md)）
- **ORCA / Gaussian 驱动**：除非社区 PR 自带维护者与 CI 策略，否则不立项

## 我们仍承诺什么

- 开放 YAML 编排、`repro` 键与 parity 导出
- 多经典后端插件（PySCF 默认、Psi4 可选、entry-point solver）
- 本地可审计的作业状态机与 Methods 对齐字段

相关入口：[产品定位](../../docusaurus-site/docs/product/positioning.md) · [parity 矩阵](../public_parity_matrix.md) · [竞争定位母稿](../竞争定位与路线图_对标Quantinuum产品与技术路线.md)
