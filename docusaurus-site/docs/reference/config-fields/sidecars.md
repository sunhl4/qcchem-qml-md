---
title: sidecars 配置字段
description: nexus、parity_integrations、md_ml_export 等非核心 sidecar。
---

# 集成类 sidecar（不影响核心化学计算）

> **返回索引：** [配置字段](./) · 仓库 [说明_config模块技术参考手册.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/说明_config模块技术参考手册.md)

## `nexus_analog` / `nexus_cloud`

本地资源账本、可选云提交；不参与核心计算。

## `parity_integrations`

控制复现快照里要附带哪些 parity sidecar。

## `md_ml_export`

管线结束后附加 MD/ML 相关数据（单帧、轨迹、能量参考等）。

**详细说明：** [说明_md_ml_export配置.md](https://github.com/sunhl4/qcchem-qml-md/blob/main/docs/说明_md_ml_export配置.md)

相关：[md-bridge](/modules/md-bridge) · [MD/ML 指南](/guide/md-ml-active-learning)。
