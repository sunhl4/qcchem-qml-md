---
title: Protocols 概览（五阶段）
inquanto_anchor: "https://docs.quantinuum.com/inquanto/manual/protocols_overview.html"
diataxis: concept
pillar: P2
status: partial
qchem_module: qchem_stack.protocols.PauliAveragingProtocol
milestone: ""
i18n_key: manual.protocols
---

# Protocols 概览（五阶段） <StatusBadge :status="$frontmatter.status" />

<p class="mirror-breadcrumb">InQuanto 镜像路径: <code>manual / protocols</code> · <a href="/en/mirror/manual/protocols/">English version</a></p>

::: info 镜像元信息
- **状态**: 部分对齐
- **四柱归属**: P2 算法与协议
- **Diátaxis**: Concept
- **对应模块**: `qchem_stack.protocols.PauliAveragingProtocol`
- **里程碑**: —
- **InQuanto 锚点**: [https://docs.quantinuum.com/inquanto/manual/protocols_overview.html](https://docs.quantinuum.com/inquanto/manual/protocols_overview.html)
:::

## 它是什么

instantiate → build → compile → run → evaluate 五阶段；可挂噪声缓解、资源估计、测量优化。

## 我们的实现

**部分对齐** — 对应模块: `qchem_stack.protocols.PauliAveragingProtocol`

字段或行为已落地但与 InQuanto 公开语义不完全等价；详细 caveat 见 [公开 parity 矩阵](/parity/public-matrix)。

## 本节子树

<MirrorBranch :prefix='["manual","protocols"]' :grouped='false' locale="zh" />


## 相关

- [公开 parity 矩阵](/parity/public-matrix)
- [工程分层架构](/concept/engineering-architecture)
- [竞争定位与路线图](/concept/competitive-positioning)
- [15 分钟上手](/tutorial/quickstart)
- [IA slug 映射](/meta/ia-mapping)
