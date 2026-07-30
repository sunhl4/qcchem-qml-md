---
title: 文档信息架构（设计依据）
description: 对标主流 SDK 的手册分层，以及本站双导航（选型 P1–P4 + 源码包模块）落地方式。
---

# 文档信息架构

本站按 **Diátaxis**（教程 / 指南 / 参考 / 解释）组织，并采用 **双导航手册**：

1. **选型 · P1–P4**（读者路径）：何时用什么映射 / 算法 / 后端  
2. **模块手册**（开发者路径）：按 `qchem_stack.*` 包讲理论、API、参数与示例  

## 主流产品怎么做

| 产品 | 手册 | 示例 / 教程 | 参考 |
|------|------|-------------|------|
| **InQuanto** | Introduction → How to use → Algorithms / Protocols 分章 | Core tutorials + Examples overview | 自动生成 API |
| **PennyLane** | Using PennyLane（概念游历） | Demos library | Sphinx API |
| **Qiskit Nature** | Getting started → Tutorials | Migration / how-to | API reference |
| **GitHub docs 模板**（Docusaurus classic） | Guides | Tutorials | Reference + Changelog |

共性规律：

1. **安装 / 5 分钟成功** 永远是第一入口。  
2. **选型手册** = 决策（何时用什么）。  
3. **模块手册** = 包级操作说明（公式 + 调用 + 参数 + 跑通）。  
4. **教程 / 示例** = 可运行任务。  
5. **参考** = 契约（CLI、HTTP、SDK、配置目录）。

## 本站映射

| Diátaxis / 扩展 | 本站路径 | 读者问的问题 |
|-----------------|----------|--------------|
| 教程 | `/tutorial/*` | 我怎么跟着做完？ |
| 示例馆 | `/examples/` | 有没有现成脚本 / YAML？ |
| 选型指南 | `/guide/*`（P1–P4） | 该选什么能力？ |
| **模块手册** | `/modules/*` | 这个包怎么用、公式是什么？ |
| 参考 | `/reference/*` | 参数 / 返回值是什么？ |
| 解释 | `/concept/*`、`/product/*` | 为什么这样设计？ |

## 模块手册页模板（强制）

每页须含：

1. **定位** — 管线阶段与上下游包  
2. **理论** — KaTeX（`$...$` / `$$...$$`；本站 MDX 请用美元符，避免 `\(...\)` 被当成 JSX）  
3. **公开 API** — 可复制 import / 调用  
4. **参数** — YAML 关键字段 + Python 参数（全表链参考）  
5. **示例运行** — 验证命令 + 期望输出（对齐 [验证块模板](../tutorial/verify-block-template)）  
6. **边界与相关** — 选型页与其他模块交叉链  

### 算法深读页额外强制

对每个用户可运行算法（VQE/UCCSD/ADAPT/…），另须：

1. **文献表** — 原始论文 / 关键综述（DOI 或 arXiv 可点链接）  
2. **理论思想** — 解决什么问题、核心假设（非「我们实现了某某」一句带过）  
3. **数学实现** — 与源码步骤对齐的公式  
4. **参数 + 函数调用** — YAML 与类/注册表 API 对照  

入口：[算法深读索引](/modules/quantum/algorithms/)。

## 维护约定

- 新增 `configs/*.yaml` 或 `examples/*.py` 时，同步更新 [示例馆](../examples/) 与 [教程索引](../tutorial/)。  
- 改 `examples/README.md` 后运行：`python scripts/generate_examples_gallery.py`。  
- 教程页必须含：**验证命令** + **期望输出**；CI：`python scripts/check_tutorial_verify_blocks.py`。  
- 新增/变更公开包 API 时，更新对应 `/modules/*` 页，并在相关 `/guide/*` 选型页顶部保留「详见模块手册」链。  
- 参考页优先链到 SDK / OpenAPI / configs catalog，避免与指南、模块手册重复长文。  
- 站内搜索：`@easyops-cn/docusaurus-search-local`（导航栏放大镜）。
