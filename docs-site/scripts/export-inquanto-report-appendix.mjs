/**
 * Reads scripts/inquanto-tree.yaml and writes:
 *   - appendix-A-full-node-list.generated.md (compact audit block per node)
 *   - appendix-B-url-inventory.generated.tsv
 *   - appendix-C-deep-node-architecture.generated.md (~2w lines: per-node IA decomposition)
 *
 * Default output dir: ../../docs/architecture-report-quantinuum-inquanto-web/
 * Override: node export-inquanto-report-appendix.mjs /absolute/path/to/outDir
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import yaml from "js-yaml";
import { buildSiblingsIndex, flatten, mirrorSitePath, topBucket } from "./lib/inquanto-manifest-flatten.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const manifestPath = path.join(__dirname, "inquanto-tree.yaml");

const defaultOut = path.join(__dirname, "..", "..", "docs", "architecture-report-quantinuum-inquanto-web");

function tsvEscape(s) {
  if (s == null) return "";
  const t = String(s).replace(/\t/g, " ").replace(/\r?\n/g, " ");
  if (/["\t\n,]/.test(t)) return `"${t.replace(/"/g, '""')}"`;
  return t;
}

function siblingSection(e, byParent) {
  if (e.breadcrumb.length < 2) return "_（根段无同级兄弟；见 manifest 顶层键）_";
  const parent = e.breadcrumb.slice(0, -1).join("/");
  const sibs = byParent.get(parent) ?? [];
  const others = sibs.filter((s) => s.slug !== e.slug);
  if (others.length === 0) return "_（manifest 中此父节点下无其它兄弟项）_";
  return others
    .map((s) => `- \`${s.slug}\` — ${s.title_en}（${s.title_zh}）· \`${s.status}\`${s.isClassLeaf ? " · class-leaf" : ""}`)
    .join("\n");
}

function personaBlock(pillar) {
  const m = {
    P1: "- **Primary**: 量子化学 / 电子结构研究者（驱动、活性空间、嵌入、周期体系）\n- **Secondary**: 方法开发者（DMET / projection / Schmidt 钩子）",
    P2: "- **Primary**: 量子算法与可编程工作流作者（Ansatz、Algorithm、Computable、Protocol）\n- **Secondary**: 应用数学家（优化器、激发态、QPE）",
    P3: "- **Primary**: 执行与噪声工程师（后端、编译 passes、shots、缓解）\n- **Secondary**: 资源估计与硬件集成者",
    P4: "- **Primary**: 平台与 DevOps（作业队列、API、可复现导出）\n- **Secondary**: 合作方尽调 / 合规读者",
    meta: "- **Primary**: 信息架构与导航读者（总览、书目、许可）\n- **Secondary**: 首次到访者（introduction）",
  };
  return m[pillar] ?? m.meta;
}

function taskIntentBlock(e) {
  const top = topBucket(e);
  const parts = [];
  parts.push(`- **顶层分区（manifest）**: \`${top}\``);
  parts.push(`- **Diátaxis 标签（manifest）**: \`${e.diataxis}\` — 对应我们站内 Tutorial / Concept / Reference / Parity 的映射见 vol-06。`);
  if (e.summary_zh && e.summary_zh !== "—") {
    parts.push(`- **Manifest 摘要（zh）**: ${e.summary_zh}`);
  }
  if (e.summary_en && e.summary_en !== "—") {
    parts.push(`- **Manifest 摘要（en）**: ${e.summary_en}`);
  }
  if (e.isClassLeaf) {
    parts.push("- **节点类型**: API **类叶** — 在 Sphinx 风格站点上通常锚定到同一 HTML 页内的符号；我们 `/mirror/` 为其保留 **独立 URL** 以便状态徽章与分享。");
  } else if (top === "api") {
    parts.push("- **节点类型**: API **模块或分组页** — 承载 autosummary / 模块 docstring。");
  } else if (top === "manual") {
    parts.push("- **节点类型**: **用户手册** — 解释 + 操作混合；常链向 `api/inquanto/*` 与 TKET 外链。");
  } else if (top === "tutorials") {
    parts.push("- **节点类型**: **教程** — 以可执行步骤为主；可能与 Manual 重复部分公式以降低跳出。");
  } else if (top === "extensions") {
    parts.push("- **节点类型**: **扩展说明** — 安装、版本、与 core 的边界；常伴独立 PyPI 包。");
  } else if (top === "introduction") {
    parts.push("- **节点类型**: **入门 / 介绍** — 最短路径与心智模型。");
  } else {
    parts.push("- **节点类型**: **杂项或元信息** — 许可、联系、书目等。");
  }
  return parts.join("\n");
}

function prereqBlock(e) {
  const top = topBucket(e);
  const lines = [];
  if (top === "manual" && e.breadcrumb.includes("algorithms")) {
    lines.push("- 熟悉变分量子算法与线性代数记号。");
    lines.push("- 若涉及 Protocol：需理解五阶段与 pytket Circuit 抽象。");
  } else if (top === "manual" && e.breadcrumb.includes("protocols")) {
    lines.push("- 熟悉测量电路、Pauli 分解与 shots 语义。");
    lines.push("- 需能阅读 `compile_circuits` 与 backend gateset 相关 TKET 文档。");
  } else if (
    top === "manual" &&
    (e.breadcrumb.includes("embedding") || e.breadcrumb.includes("geometry"))
  ) {
    lines.push("- 经典量子化学基础（HF、活性空间、分子几何）。");
  } else if (top === "api") {
    lines.push("- Python 类型注解与包导入路径阅读经验。");
    lines.push("- 若类叶：需结合 Manual 同名概念阅读，否则易误解默认行为。");
  } else if (top === "tutorials") {
    lines.push("- 可运行 Python 环境；部分教程依赖 pytket 扩展或（厂商）Nexus — manifest 已标 `not-applicable` 者我们侧以本地 API 类比。");
  } else {
    lines.push("- 依赖随分区变化；以 InQuanto 公开页前置说明为准。");
  }
  lines.push("- **我们栈前置**: [`ENGINEERING_ARCHITECTURE.md`](../../ENGINEERING_ARCHITECTURE.md) 对齐 `pillar` 章节。");
  return lines.join("\n");
}

function vendorCrossLinkPattern(top) {
  if (top === "manual")
    return "- **典型出链**: `api/inquanto/*` 模块锚点；`docs.quantinuum.com/tket/*` 编译与后端；`computables_overview` / `protocols_overview` 枢纽互链。\n- **典型入链**: introduction quickstart；tutorials 对应主题。";
  if (top === "api")
    return "- **典型出链**: Manual 概念页（解释语义）；Extensions（可选依赖）。\n- **典型入链**: Manual 正文内联类引用；IDE 自动跳转。";
  if (top === "tutorials")
    return "- **典型出链**: Manual 深度章节；API 具体方法；Extensions 安装页。\n- **典型入链**: 官方 hub 三柱 CTA；教程索引 `tutorial_overview`。";
  if (top === "extensions")
    return "- **典型出链**: PyPI / Nexus 控制台；API `extensions.*`。\n- **典型入链**: manual「驱动」叙事；quickstart。";
  return "- **典型出链**: 全站页脚 Support / Publications。\n- **典型入链**: 根 hub。";
}

function qchemSurfaceBlock(e) {
  if (e.qchem) {
    return [
      "- **已绑定模块（manifest `qchem`）**:",
      `  - \`${e.qchem}\``,
      "- **工程动作**: 在 Python 包内定位该符号；更新 parity 矩阵行；为 `/reference/` 或 `/guide/` 写 Methods 段落时引用此路径。",
    ].join("\n");
  }
  return [
    "- **已绑定模块**: _manifest 未填 `qchem`_。",
    "- **工程动作**: 在 parity 评审中决定是 **占位** 还是 **刻意不做**；若占位，指定里程碑与最小可交付 API 面。",
  ].join("\n");
}

function parityPostureBlock(e) {
  const lines = [
    `- **status（manifest）**: \`${e.status}\``,
    e.milestone ? `- **milestone**: ${e.milestone}` : "- **milestone**: —",
  ];
  if (e.reason_zh) lines.push(`- **reason_zh**: ${e.reason_zh}`);
  if (e.reason_en) lines.push(`- **reason_en**: ${e.reason_en}`);
  lines.push("- **解读规则**: `shipped` = 我们声称公开语义可对齐的实现；`partial` = 需读 parity caveat；`placeholder` = 路由保留；`not-applicable` = 边界声明（常见于云/硬件）。");
  return lines.join("\n");
}

function ourIABlock(e) {
  const mp = mirrorSitePath(e);
  const lines = [
    "- **Mirror（审计）**: 必选 — " + `\`${mp}\``,
    "- **四柱指南**: " +
      (e.pillar === "P1"
        ? "`/guide/chemistry-and-embedding/`"
        : e.pillar === "P2"
          ? "`/guide/algorithms-and-protocols/`"
          : e.pillar === "P3"
            ? "`/guide/execution-and-analysis/`"
            : e.pillar === "P4"
              ? "`/guide/jobs-and-reproducibility/`"
              : "`/guide/` 总览 + `/product/`"),
  ];
  if (e.diataxis === "reference" || e.isClassLeaf) lines.push("- **Reference 区**: 若涉及 HTTP / 契约 / 字段表 — 在 `/reference/` 增加或链接机读表。");
  if (e.status === "not-applicable") lines.push("- **Product 叙事**: 在 `/product/` 或 `/concept/architecture-boundaries` 保持 **不做假对等** 的显式声明。");
  return lines.join("\n");
}

function platformEngineeringBlock(e) {
  const lines = [
    "### 平台与工程化检查单（云 · 安全 · SEO · i18n · CI）",
    "",
    "- **云 / 租户**: `launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。",
    "- **后端 / 可观测**: P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。",
    "- **安全 / 合规**: 禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。",
    "- **SEO / URL**: 厂商锚点变更回写 manifest；本站 slug 以 IA_MAPPING 为真源。",
    "- **i18n**: shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。",
    "- **CI**: 外链存活巡检；教程命令可选 smoke。",
  ];
  if (e.pillar === "P4") {
    lines.push("- **P4**: `GET/POST /v1/runs`、`repro` 须有 **API 表或控制台等价说明**。");
  }
  return lines.join("\n");
}

function riskBlock(e) {
  const risks = [];
  if (e.status === "partial") risks.push("- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。");
  if (e.status === "placeholder") risks.push("- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。");
  if (e.isClassLeaf) risks.push("- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。");
  if (topBucket(e) === "extensions" && e.status !== "not-applicable")
    risks.push("- **R4（依赖地狱）**: 扩展版本与 core 不兼容 — 文档需锁定 **受支持版本矩阵**。");
  if (risks.length === 0) risks.push("- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。");
  return risks.join("\n");
}

function acceptanceBlock(e) {
  if (e.status === "shipped") {
    return [
      "- [ ] 公开 InQuanto 页与 `qchem` 模块行为有可引用对照实验或 parity 行。",
      "- [ ] `npm run check:mirror` 通过且 Mirror 页 `StatusBadge` 为 shipped。",
      "- [ ] `repro` 或 `parity_snapshot` 中含本能力相关键（若适用）。",
    ].join("\n");
  }
  if (e.status === "partial") {
    return [
      "- [ ] `docs/inquanto_public_parity_matrix.md` 中 caveat 段落与代码一致。",
      "- [ ] Mirror 页 partial 说明链接到 parity 矩阵对应行。",
    ].join("\n");
  }
  if (e.status === "placeholder") {
    return [
      `- [ ] 里程碑 ${e.milestone ?? "TBD"} 前：最小 API / YAML 样例落地。`,
      "- [ ] 占位页禁止被搜索引擎当作「已完成」— `noindex` 策略按站点配置评估。",
    ].join("\n");
  }
  return [
    "- [ ] `reason_*` 与法务/产品口径一致。",
    "- [ ] 不在营销材料中暗示已实现 Nexus/H 系等价能力。",
  ].join("\n");
}

function siblingSectionTrimmed(e, byParent) {
  const raw = siblingSection(e, byParent);
  if (raw.startsWith("_")) return raw;
  const lines = raw.split("\n").filter(Boolean);
  const max = 10;
  if (lines.length <= max) return raw;
  const more = lines.length - max;
  return lines.slice(0, max).join("\n") + `\n- _… 另有 ${more} 个兄弟项（见 appendix-B TSV 同父路径）_`;
}

function renderDeepArchitectureBlock(e, index, byParent, totalNodes) {
  const bcPath = e.breadcrumb.join(" / ");
  const bcDot = e.breadcrumb.join(".");
  const lines = [];
  lines.push(`# 节点 ${index + 1} / ${totalNodes} — \`${bcDot}\``);
  lines.push("");
  lines.push("## 1. 标识、InQuanto IA 位置、读者与阅读路径");
  lines.push("");
  lines.push("| 字段 | 值 |");
  lines.push("| --- | --- |");
  lines.push(`| breadcrumb | \`${bcPath}\` |`);
  lines.push(`| slug | \`${e.slug}\` |`);
  lines.push(`| title_zh / en | ${e.title_zh} / ${e.title_en} |`);
  lines.push(`| inquanto_anchor | ${e.inquanto ?? "—"} |`);
  lines.push(`| pillar / diataxis / class_leaf | ${e.pillar} / ${e.diataxis} / ${e.isClassLeaf ? "yes" : "no"} |`);
  lines.push(`| mirror_path | \`${mirrorSitePath(e)}\` |`);
  lines.push("");
  lines.push(
    `- **L1 分区**: \`${topBucket(e)}\` → **L2..n**: ${e.breadcrumb.slice(1).map((s) => "`" + s + "`").join(" → ") || "_根_"}`,
  );
  lines.push(personaBlock(e.pillar));
  lines.push(taskIntentBlock(e));
  lines.push(prereqBlock(e));
  lines.push(vendorCrossLinkPattern(topBucket(e)));
  lines.push("");
  lines.push("## 2. 同级兄弟（manifest 同父）");
  lines.push("");
  lines.push(siblingSectionTrimmed(e, byParent));
  lines.push("");
  lines.push("## 3. qchem_stack 映射、Parity、自有站 IA");
  lines.push("");
  lines.push(qchemSurfaceBlock(e));
  lines.push("");
  lines.push(parityPostureBlock(e));
  lines.push("");
  lines.push(ourIABlock(e));
  lines.push("");
  lines.push(platformEngineeringBlock(e));
  lines.push("");
  lines.push("## 4. 风险与验收");
  lines.push("");
  lines.push(riskBlock(e));
  lines.push("");
  lines.push(acceptanceBlock(e));
  lines.push("");
  lines.push("## 5. 开放问题");
  lines.push("");
  lines.push("- [ ] 公开页自 `source_pin_date` 以来是否结构重排？");
  lines.push("- [ ] 是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？");
  lines.push("");
  lines.push("---");
  lines.push("");
  return lines.join("\n");
}

function renderAppendixBlock(e, index) {
  const bc = e.breadcrumb.join(".");
  const lines = [];
  lines.push(`## ${index + 1}. \`${bc}\``);
  lines.push("");
  lines.push("| Field | Value |");
  lines.push("| --- | --- |");
  lines.push(`| **breadcrumb** | \`${e.breadcrumb.join(" / ")}\` |`);
  lines.push(`| **title_zh** | ${String(e.title_zh).replace(/\|/g, "\\|")} |`);
  lines.push(`| **title_en** | ${String(e.title_en).replace(/\|/g, "\\|")} |`);
  lines.push(`| **inquanto_anchor** | ${e.inquanto ?? "—"} |`);
  lines.push(`| **pillar** | ${e.pillar} |`);
  lines.push(`| **diataxis** | ${e.diataxis} |`);
  lines.push(`| **status** | ${e.status} |`);
  lines.push(`| **qchem_module** | ${e.qchem ?? "—"} |`);
  lines.push(`| **milestone** | ${e.milestone ?? "—"} |`);
  lines.push(`| **summary_zh** | ${(e.summary_zh ?? "—").replace(/\|/g, "\\|")} |`);
  lines.push(`| **summary_en** | ${(e.summary_en ?? "—").replace(/\|/g, "\\|")} |`);
  lines.push(`| **reason_zh** | ${(e.reason_zh ?? "—").replace(/\|/g, "\\|")} |`);
  lines.push(`| **reason_en** | ${(e.reason_en ?? "—").replace(/\|/g, "\\|")} |`);
  lines.push(`| **is_class_leaf** | ${e.isClassLeaf ? "yes" : "no"} |`);
  lines.push(`| **qchem_stack_docs_site_path** | \`${mirrorSitePath(e)}\` |`);
  lines.push("");
  lines.push("### Audit prompts (copy to design review)");
  lines.push("");
  lines.push("- [ ] Does the InQuanto public page at the anchor still match this summary?");
  lines.push("- [ ] Is `status` still accurate against `qchem_stack`?");
  lines.push("- [ ] Should this node surface in **Product**, **Pillar guide**, **Mirror only**, or **API ref**?");
  lines.push("- [ ] Does simulator-cloud UX need a **tenant-facing** alias for this capability?");
  lines.push("- [ ] Is there a runnable **tutorial** or **YAML recipe** on our side?");
  lines.push("- [ ] Are **repro** / **parity_snapshot** keys documented for this node?");
  lines.push("- [ ] Cross-links: Manual ↔ API ↔ Tutorials — all present on vendor site?");
  lines.push("- [ ] i18n: do we need a dedicated EN narrative page beyond the mirror stub?");
  lines.push("");
  lines.push("---");
  lines.push("");
  return lines.join("\n");
}

function lineCountOf(filePath) {
  return fs.readFileSync(filePath, "utf8").split(/\r?\n/).length;
}

function main() {
  const outDir = path.resolve(process.argv[2] || defaultOut);
  fs.mkdirSync(outDir, { recursive: true });

  const raw = fs.readFileSync(manifestPath, "utf8");
  const tree = yaml.load(raw);
  const { site_meta, ...sections } = tree;

  const entries = [];
  for (const [k, v] of Object.entries(sections)) {
    entries.push(...flatten(v, k));
  }

  const byParent = buildSiblingsIndex(entries);

  const header = [
    "---",
    "title: Appendix A — Full node list (generated)",
    `description: Auto-generated from inquanto-tree.yaml; ${entries.length} entries.`,
    "edit: false",
    "---",
    "",
    "> **Do not hand-edit.** Regenerate with `npm run report:inquanto-appendix` from `docs-site/`.",
    "",
    `**Source pin**: ${site_meta?.source_pin_date ?? "—"} · **InQuanto version (manifest)**: ${site_meta?.inquanto_version_seen ?? "—"}`,
    "",
    "**姊妹附录**: 更深拆解见 [appendix-C-deep-node-architecture.generated.md](./appendix-C-deep-node-architecture.generated.md)（约 2 万行量级，规则生成）。",
    "",
    "---",
    "",
  ].join("\n");

  const body = entries.map((e, i) => renderAppendixBlock(e, i)).join("\n");

  const appendixPath = path.join(outDir, "appendix-A-full-node-list.generated.md");
  fs.writeFileSync(appendixPath, header + body, "utf8");

  const cHeader = [
    "---",
    "title: Appendix C — Per-node architecture decomposition (generated)",
    `description: Rule-based IA/security/cloud/test checklist per manifest node (${entries.length} nodes). Not hand prose.`,
    "edit: false",
    "---",
    "",
    "> **Do not hand-edit.** 由 `inquanto-tree.yaml` **全量扁平节点** 规则生成；每一节结构相同，便于 diff 与评审。",
    "> 非「编造功能」，未在 manifest 出现的字段一律写 **—** 或 **推断** 模板句。",
    "",
    `**Source pin**: ${site_meta?.source_pin_date ?? "—"} · **InQuanto version**: ${site_meta?.inquanto_version_seen ?? "—"} · **Nodes**: ${entries.length}`,
    "",
    "## 本附录的阅读方法",
    "",
    "- 按 **breadcrumb** 与 InQuanto 公开 URL 对照。",
    "- **§7 兄弟节点** 来自 manifest 树结构，用于发现 **遗漏交叉链接**。",
    "- **§11** 合并云/安全/SEO/i18n/CI 检查单；不适用项仍保留以证明 **已评审**。",
    "",
    "---",
    "",
  ].join("\n");

  const cBody = entries.map((e, i) => renderDeepArchitectureBlock(e, i, byParent, entries.length)).join("\n");
  const appendixCPath = path.join(outDir, "appendix-C-deep-node-architecture.generated.md");
  fs.writeFileSync(appendixCPath, cHeader + cBody, "utf8");

  const tsvLines = [
    [
      "index",
      "breadcrumb",
      "title_zh",
      "title_en",
      "inquanto_anchor",
      "pillar",
      "diataxis",
      "status",
      "qchem_module",
      "milestone",
      "is_class_leaf",
      "mirror_site_path",
    ].join("\t"),
  ];
  entries.forEach((e, i) => {
    tsvLines.push(
      [
        i + 1,
        e.breadcrumb.join("/"),
        tsvEscape(e.title_zh),
        tsvEscape(e.title_en),
        tsvEscape(e.inquanto),
        e.pillar,
        e.diataxis,
        e.status,
        tsvEscape(e.qchem),
        tsvEscape(e.milestone),
        e.isClassLeaf ? "1" : "0",
        mirrorSitePath(e),
      ].join("\t")
    );
  });
  const appendixBTsv = path.join(outDir, "appendix-B-url-inventory.generated.tsv");
  fs.writeFileSync(appendixBTsv, tsvLines.join("\n"), "utf8");

  const linesA = lineCountOf(appendixPath);
  const linesC = lineCountOf(appendixCPath);
  console.log(`export-inquanto-report-appendix: wrote ${entries.length} entries to`);
  console.log(`  ${appendixPath}  (lines: ${linesA})`);
  console.log(`  ${appendixCPath}  (lines: ${linesC})`);
  console.log(`  ${appendixBTsv}`);
}

main();
