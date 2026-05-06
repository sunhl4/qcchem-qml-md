---
title: CASSCF
inquanto_anchor: "https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.CASSCF"
diataxis: reference
pillar: P1
status: partial
qchem_module: ""
milestone: ""
i18n_key: api.extensions_pyscf.classes.CASSCF
---

# CASSCF <StatusBadge :status="$frontmatter.status" />

<p class="mirror-breadcrumb">InQuanto 镜像路径: <code>api / extensions_pyscf / classes / CASSCF</code> · <a href="/en/mirror/api/extensions_pyscf/classes/CASSCF/">English version</a></p>

::: info 镜像元信息
- **状态**: 部分对齐
- **四柱归属**: P1 化学与嵌入
- **Diátaxis**: Reference
- **对应模块**: `chemistry_extended.casscf_orbital_optimization_audit`（最小审计 YAML：`configs/example_h2_casscf_audit.yaml`）
- **里程碑**: —
- **InQuanto 锚点**: [https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.CASSCF](https://docs.quantinuum.com/inquanto/api/extensions/inquanto-pyscf_api.html#inquanto.extensions.pyscf.CASSCF)
:::

## 它是什么

本节为 InQuanto 公开树的对应位置。点开下面 InQuanto 锚点查看官方原始定义；本仓库的对应实现见「我们的实现」。

## 我们的实现

**部分对齐** — 主线路仍用 **CASCI 型活性空间积分** 变到 qubit；与 InQuanto **CASSCF 产品类** 非 L0 等价。开放栈提供可选 **CASSCF 轨道优化一步审计**（见 frontmatter「对应模块」与 [公开 parity 矩阵](/parity/public-matrix) §3）。

## 相关

- [公开 parity 矩阵](/parity/public-matrix)
- [工程分层架构](/concept/engineering-architecture)
- [竞争定位与路线图](/concept/competitive-positioning)
- [15 分钟上手](/tutorial/quickstart)
- [IA slug 映射](/meta/ia-mapping)
