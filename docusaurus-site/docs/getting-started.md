---
title: 快速开始
description: qchem-stack 文档站快速启动指南，包含本地运行、信息架构与推荐阅读路径。
keywords:
  - qchem-stack
  - docusaurus
  - 快速开始
  - 文档站
---

# 快速开始

这个站点用于承载 `qchem_qml_md` 的产品文档，采用 Docusaurus 构建，可扩展为用户文档、教程、参考手册与对标评估的一体化门户。

## 安装与运行文档站

```bash
cd qchem_qml_md/docusaurus-site
npm install
npm start
```

## 站点结构

- `docs/product`：产品能力与定位
- `docs/guide`：三层架构的主线指南
- `docs/tutorial`：上手与工作流教程
- `docs/reference`：命令、接口与工程契约
- `docs/cloud`：作业队列与模拟器云
- `docs/parity`：与 InQuanto 的能力对标页

## 建议阅读顺序

1. 先看 [产品能力](./product/features)
2. 再看 [教程快速上手](./tutorial/quickstart)
3. 然后进入 [三层架构指南](./guide/overview)
4. 最后补齐 [P4 作业与可复现](./guide/jobs-and-reproducibility) 与 [HTTP API](./reference/http-api-sqlite-jobs)

## 外部参考

产品信息架构可参考 Quantinuum 的 InQuanto 文档分层（Chemical Specification / Program Construction / Execution and Analysis）：

- [Quantinuum InQuanto 文档](https://docs.quantinuum.com/inquanto/)
