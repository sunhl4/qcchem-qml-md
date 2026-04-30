# 首页与 Guides 线框（Wireframe）

本文描述对标文档站的 **区块结构与信息流**，供实现与迭代对齐；像素稿可选后续补充。

## 1. 全局壳（所有页面）

```
┌─────────────────────────────────────────────────────────────────┐
│ [Logo] qchem-stack docs    Guides ▾  Reference ▾  Parity ▾     │
│                    [搜索……]              [深色模式] [GitHub]      │
├─────────────────────────────────────────────────────────────────┤
│ (正文区；移动端汉堡菜单收起左侧栏)                                │
└─────────────────────────────────────────────────────────────────┘
```

- **主导航**：Guides（四柱下拉）、Reference（HTTP / CircuitIR / DMET 契约）、Parity（矩阵 / L1 / Y1 台账）。
- **搜索**：本地索引（VitePress Local Search）；后续可换 Algolia。
- **GitHub**：指向仓库根 README 或 issue（配置项）。

## 2. 首页（`/`）— 区块自上而下

### 2.1 Hero

```
┌─────────────────────────────────────────────────────────────────┐
│  开放编排 · InQuanto 风格管线                                      │
│  化学输入 → 降阶 → 量子核 → 协议状态机 → 作业 → 可复现导出              │
│                                                                  │
│  [15 分钟上手]          [按角色进入]                               │
│                                                                  │
│  诚实边界：独立开源实现；能力对照公开文献与 API，非闭源 wheel 等价。      │
└─────────────────────────────────────────────────────────────────┘
```

- **主标题 + 副标题**：一句话价值 + 管线短语（与 README 一致）。
- **双 CTA**：主按钮 → Quickstart；次按钮 → 锚点到「按角色」或 `/guide/#personas`。
- **一行合规文案**：替代空洞营销，建立信任。

### 2.2 Quickstart（摘要条）

三步骤横向卡片（桌面）或纵向堆叠（移动）：

1. `pip install -e ".[dev]"` → 2. 选用 `configs/example_h2.yaml` → 3. `run_pipeline_from_config` / 可选 `uvicorn`。

### 2.3 Choose your path（按角色）

| 区块 ID | 标题 | 跳转 |
|---------|------|------|
| researcher | 研究者：算法与激发态 | `/guide/algorithms-and-protocols/` + parity 激发态行 |
| integrator | 集成方：HTTP API 与 repro | `/reference/http-api-sqlite-jobs` |
| chem | 经典化学与嵌入 | `/guide/chemistry-and-embedding/` |

每项：**图标 + 一句描述 + 链接**。

### 2.4 四柱能力卡片（对齐 InQuanto 三柱 + 第四柱）

四列网格（移动端一列）：

```
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ P1 化学与嵌入 │ │ P2 算法与协议 │ │ P3 执行与分析 │ │ P4 作业与可复现 │
│ PySCF/JW…    │ │ VQE/Protocol │ │ 后端/缓解    │ │ SQLite/runs  │
│ [进入指南]    │ │ [进入指南]    │ │ [进入指南]    │ │ [进入指南]    │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

每卡片单一主 CTA：`进入指南` → 对应 `/guide/{pillar-slug}/`。

### 2.5 信任块（Trust）

- **公开对标矩阵** → `/parity/public-matrix`
- **L1 签 off** → `/parity/l1-signoff`
- **工程架构分层** → `/concept/engineering-architecture`

简短说明：`yes` / `partial` / `n/a` 图例一眼可见（图标或色条）。

### 2.6 页脚

Copyright · [parity](/parity/public-matrix) · [Architecture](/concept/engineering-architecture)

## 3. Guides 枢纽（`/guide/`）

```
标题：指南总览

简介段（2–4 句）：四柱与 Diátaxis（概念 / 教程 / 参考 / 对标）关系。

┌─ P1 chemistry-and-embedding ─────────────────────────────────┐
│ 摘要 + 列表链接（concept/reference 条目）                      │
└──────────────────────────────────────────────────────────────┘
… P2–P4 同理

底部：[返回首页] [完整索引](/parity/public-matrix)
```

## 4. 四柱子页（`/guide/{pillar-slug}/`）

统一模板：

1. **一句话定义**（与 IA_MAPPING 英文 label 一致）。
2. **你将学到**（3 条 bullet）。
3. **相关文档**（手列链接到 `/concept|`/tutorial|`/reference`）。
4. **下一步**（相邻柱或 Quickstart）。

## 5. 与 InQuanto 枢纽的差异（UX）

| InQuanto | 本站 |
|----------|------|
| 三柱并列、教程/手册混排 | 四柱 + 角色分流 + Diátaxis 前缀 |
| 枢纽偏列表 | 首页 Hero + Quickstart + 信任块 |
| Nexus 能力分散 | P4 聚合 jobs / repro / launch-retrieve |
