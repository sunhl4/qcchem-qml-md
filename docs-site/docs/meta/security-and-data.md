---
title: 安全与数据
description: 默认部署、数据驻留与合规非声称（简要）
---

面向采购 / 安全的**简要说明**：默认在您自管环境运行，分子与 YAML、**SQLite 作业库**均在您控制的存储上；不默认接入 Quantinuum 商业云或 Nexus。HTTP 监听、TLS、认证由部署方配置，见 [HTTP API](/reference/http-api-sqlite-jobs)。

本站与仓库**未**宣称 SOC 2、ISO 27001 等认证。技术对表见 [契约矩阵](/parity/public-matrix) 与 `repro` / CI，不替代贵司安全评估。

另见：[站点地图](/meta/ia-mapping) · [架构边界](/concept/architecture-boundaries)。

## 默认无认证意味着什么

内置 HTTP 作业网关**不自带**登录、RBAC 或 API Key；设计上假定绑定 **本机或受信内网**，由你在反向代理或网关层做鉴权。面向公网暴露前必须补齐 TLS、速率限制与身份验证。

## 日志与 SQLite 落盘位置

作业行、时间线 JSON 等写入你在配置中指定的 **SQLite 路径**（见 HTTP API 与 worker 文档）；应用日志由部署方式（systemd、容器日志驱动等）决定。备份与留痕策略由运维方定义，本站不规定具体目录名。

## 威胁模型（一句话）

攻击面主要来自**能访问 HTTP 绑定地址与作业库文件**的主体；缓解重点是网络隔离、文件权限与依赖更新，而非依赖文档站自身做安全声称。
