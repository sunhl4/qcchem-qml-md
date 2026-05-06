---
title: 部署与验收清单
description: qchem-stack 文档站发布前后的标准检查步骤，覆盖构建、SEO、导航与回滚策略。
keywords:
  - deployment
  - checklist
  - release
  - 验收
---

# 部署与验收清单

## 发布前检查

- `npm install` 与 `npm run build` 均成功
- 主页、导航、侧边栏、页脚链接全部可访问
- 关键页面 `title/description` 已设置
- favicon 与 social card 已在配置中生效
- 404 与断链检查通过

## 发布执行

1. 固定待发布 commit/tag
2. 产出静态文件（`build/`）
3. 上传到目标静态托管环境
4. 执行线上 smoke 检查

## 发布后验收

- 首页加载、导航跳转、搜索功能正常
- 核心页（产品/教程/参考/云/对标）可打开
- 社交分享预览图正确
- 移动端布局无明显错位

## 回滚策略

- 保留上一版静态产物
- 回滚到上一个稳定 tag
- 回滚后重复执行 smoke 检查
