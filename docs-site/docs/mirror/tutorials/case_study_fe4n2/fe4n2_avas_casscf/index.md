---
title: Fe4N2：AVAS + CASSCF
inquanto_anchor: "https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_fe4n2_1.html"
diataxis: tutorial
pillar: P1
status: placeholder
qchem_module: ""
milestone: ""
i18n_key: tutorials.case_study_fe4n2.fe4n2_avas_casscf
---

# Fe4N2：AVAS + CASSCF <StatusBadge :status="$frontmatter.status" />

<p class="mirror-breadcrumb">InQuanto 镜像路径: <code>tutorials / case_study_fe4n2 / fe4n2_avas_casscf</code> · <a href="/en/mirror/tutorials/case_study_fe4n2/fe4n2_avas_casscf/">English version</a></p>

::: info 镜像元信息
- **状态**: 占位
- **四柱归属**: P1 化学与嵌入
- **Diátaxis**: Tutorial
- **对应模块**: *（占位，未实现 — 见里程碑）*
- **里程碑**: —
- **InQuanto 锚点**: [https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_fe4n2_1.html](https://docs.quantinuum.com/inquanto/tutorials/InQ_tut_fe4n2_1.html)
:::

## 它是什么

本节为 InQuanto 公开树的对应位置。点开下面 InQuanto 锚点查看官方原始定义；本仓库的对应实现见「我们的实现」。

## 我们的实现

**占位（Fe4N2 全教程链仍为占位）**。开放栈可提供 **最小 CASSCF 轨道优化审计**（PySCF `mcscf.CASSCF` 能量写入 `hamiltonian_meta.pyscf_driver.casscf_orbital_audit_v1`，与差距表「无 AVAS / 全 CASSCF 产品深度」叙述一致）：见仓库 `configs/example_h2_casscf_audit.yaml` 与 [差距总表 § 经典化学](/parity/gap-implementation-plan)。

## 相关

- [公开 parity 矩阵](/parity/public-matrix)
- [工程分层架构](/concept/engineering-architecture)
- [竞争定位与路线图](/concept/competitive-positioning)
- [15 分钟上手](/tutorial/quickstart)
- [IA slug 映射](/meta/ia-mapping)
