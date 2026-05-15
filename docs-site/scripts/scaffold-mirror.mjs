/**
 * scaffold-mirror.mjs
 *
 * Reads scripts/mirror-doc-tree.yaml (the single source of truth) and writes:
 *
 *   1. docs/mirror/**\/index.md and docs/en/mirror/**\/index.md placeholder pages
 *      (idempotent: only created when target file does not yet exist; existing
 *      pages keep their authored body, frontmatter is regenerated).
 *   2. docs/.vitepress/mirror-data.json with the flattened tree + status counts,
 *      consumed by MirrorTree.vue and the /mirror/ index page.
 *   3. docs/.vitepress/sidebar-mirror.json — sidebar entries for the Mirror
 *      view, imported by config.ts.
 *
 * Status palette: shipped | partial | placeholder | not-applicable
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import yaml from "js-yaml";
import { flatten } from "./lib/inquanto-manifest-flatten.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.join(__dirname, "..");
const docsRoot = path.join(repoRoot, "docs");
const manifestPath = path.join(__dirname, "mirror-doc-tree.yaml");

const STATUS_LABELS = {
  shipped: { zh: "已落地", en: "Shipped" },
  partial: { zh: "部分实现", en: "Partial" },
  placeholder: { zh: "占位", en: "Placeholder" },
  "not-applicable": { zh: "刻意不做", en: "Not applicable" },
};

const PILLAR_LABELS = {
  P1: { zh: "P1 化学与嵌入", en: "P1 Chemistry & embedding" },
  P2: { zh: "P2 算法与协议", en: "P2 Algorithms & protocols" },
  P3: { zh: "P3 执行与分析", en: "P3 Execution & analysis" },
  P4: { zh: "P4 作业与可复现", en: "P4 Jobs & reproducibility" },
  meta: { zh: "Meta（导航/元）", en: "Meta (navigation)" },
};

const DIATAXIS_LABELS = {
  concept: { zh: "Concept", en: "Concept" },
  tutorial: { zh: "Tutorial", en: "Tutorial" },
  reference: { zh: "Reference", en: "Reference" },
  parity: { zh: "产品计划", en: "Product planning" },
};

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function inheritStatus(node, parent) {
  if (!node || typeof node !== "object") return parent;
  return node.status ?? parent ?? "placeholder";
}

function nodePath(entry) {
  return path.posix.join("/mirror", ...entry.breadcrumb) + "/";
}

function mdEscape(s) {
  if (s == null) return "";
  return String(s).replace(/\|/g, "\\|");
}

function renderPage(entry, locale, descendantsCount = 0) {
  const title = locale === "zh" ? entry.title_zh : entry.title_en;
  const fm = {
    title,
    reference_doc_url: entry.reference_url || "",
    diataxis: entry.diataxis,
    pillar: entry.pillar,
    status: entry.status,
    qchem_module: entry.qchem || "",
    milestone: entry.milestone || "",
    i18n_key: entry.breadcrumb.join("."),
  };
  const fmYaml = Object.entries(fm)
    .map(([k, v]) => `${k}: ${typeof v === "string" && (v.includes(":") || v === "") ? JSON.stringify(v) : v}`)
    .join("\n");

  const statusLabel = STATUS_LABELS[entry.status]?.[locale] ?? entry.status;
  const pillarLabel = PILLAR_LABELS[entry.pillar]?.[locale] ?? entry.pillar;
  const diataxisLabel = DIATAXIS_LABELS[entry.diataxis]?.[locale] ?? entry.diataxis;
  const summary = locale === "zh" ? entry.summary_zh : entry.summary_en;
  const reason = locale === "zh" ? entry.reason_zh : entry.reason_en;

  const breadcrumbZh = entry.breadcrumb.join(" / ");

  const localePrefix = locale === "zh" ? "" : "/en";
  const text =
    locale === "zh"
      ? {
          h_meta: "镜像元信息",
          h_what: "它是什么",
          h_ours: "我们的实现",
          h_related: "相关",
          status: "状态",
          pillar: "四柱归属",
          diataxis: "Diátaxis",
          module: "对应模块",
          milestone: "里程碑",
          ref_doc: "参考文档 URL",
          reason: "口径说明",
          fallback_what:
            "本节与第三方公开文档目录中的对应条目同构。点击下方参考锚点可查阅外部原始定义；本仓库实现见「我们的实现」。",
          fallback_module: "（占位，未实现 — 见里程碑）",
          related_parity: "能力概览与路线图",
          related_engineering: "工程分层架构",
          related_competitive: "产品路线图",
          related_quickstart: "教程：15 分钟上手",
          breadcrumb_label: "手册镜像节点路径",
          en_link_label: "English version",
        }
      : {
          h_meta: "Mirror metadata",
          h_what: "What it is",
          h_ours: "Our implementation",
          h_related: "Related",
          status: "Status",
          pillar: "Pillar",
          diataxis: "Diátaxis",
          module: "Module",
          milestone: "Milestone",
          ref_doc: "Reference doc URL",
          reason: "Scope note",
          fallback_what:
            "This page mirrors a third-party public documentation entry. Use the reference anchor for upstream wording; see \"Our implementation\" for this repository.",
          fallback_module: "(placeholder, not yet implemented — see milestone)",
          related_parity: "Capabilities & roadmap",
          related_engineering: "Engineering architecture",
          related_competitive: "Product roadmap",
          related_quickstart: "Tutorial: 15-minute quickstart",
          breadcrumb_label: "Manual mirror node path",
          en_link_label: "中文版",
        };

  const otherLocaleHref = locale === "zh"
    ? `/en${nodePath(entry)}`
    : nodePath(entry);

  const refDocLink = entry.reference_url
    ? `[${entry.reference_url}](${entry.reference_url})`
    : "—";

  const moduleLine = entry.qchem
    ? "`" + entry.qchem + "`"
    : `*${text.fallback_module}*`;

  const reasonBlock = reason ? `\n> ${text.reason}: ${reason}` : "";

  const summaryBlock = summary ? summary : text.fallback_what;

  const parityHref = `${localePrefix}/product/roadmap`;
  let ourBody;
  if (entry.status === "shipped") {
    ourBody = `**${statusLabel}** — ${text.module}: ${moduleLine}`;
  } else if (entry.status === "partial") {
    const partialNote = locale === "zh"
      ? `字段或行为已落地，但与参考文档公开语义可能不完全一致；说明见 [能力概览与路线图](${parityHref})。`
      : `Fields or behavior may differ from the public reference text; see [Capabilities & roadmap](${parityHref}).`;
    ourBody = `**${statusLabel}** — ${text.module}: ${moduleLine}\n\n${partialNote}`;
  } else if (entry.status === "placeholder") {
    const placeholderNote = locale === "zh"
      ? `尚未实现，预计在 ${entry.milestone || "下个里程碑"} 落地。在站点保留位置以便未来直接填充内容。`
      : `Not yet implemented; planned for ${entry.milestone || "the next milestone"}. The page is kept here so future content can drop in without breaking links.`;
    ourBody = `**${statusLabel}** — ${placeholderNote}`;
  } else {
    const naNote = reason || (locale === "zh"
      ? "本仓库刻意不实现，但说明边界以保信任。"
      : "Intentionally not implemented; we keep this page to be transparent about boundaries.");
    ourBody = `**${statusLabel}** — ${naNote}`;
  }

  const relatedLinks = locale === "zh"
    ? [
        ["能力概览与路线图", "/product/roadmap"],
        ["工程分层架构", "/concept/engineering-architecture"],
        ["产品路线图", "/product/roadmap"],
        ["15 分钟上手", "/tutorial/quickstart"],
        ["IA slug 映射", "/meta/ia-mapping"],
      ]
    : [
        ["Capabilities & roadmap", "/en/product/roadmap"],
        ["Engineering architecture", "/en/concept/engineering-architecture"],
        ["Product roadmap", "/en/product/roadmap"],
        ["15-minute quickstart", "/en/tutorial/quickstart"],
        ["IA slug map", "/en/meta/ia-mapping"],
      ];

  // Section / sub-section pages get an auto-generated child listing so
  // visitors see the branch immediately on landing — no hand-maintained
  // child indices needed.
  const branchHeading = locale === "zh" ? "本节子树" : "Children in this branch";
  const branchPrefixJson = JSON.stringify(entry.breadcrumb);
  const branchBlock =
    descendantsCount > 0 && entry.breadcrumb.length <= 2
      ? `\n\n## ${branchHeading}\n\n<MirrorBranch :prefix='${branchPrefixJson}' :grouped='${entry.breadcrumb.length === 1}' locale="${locale}" />\n`
      : "";

  return `---
${fmYaml}
---

# ${title} <StatusBadge :status="$frontmatter.status" />

<p class="mirror-breadcrumb">${text.breadcrumb_label}: <code>${breadcrumbZh}</code> · <a href="${otherLocaleHref}">${text.en_link_label}</a></p>

::: info ${text.h_meta}
- **${text.status}**: ${statusLabel}
- **${text.pillar}**: ${pillarLabel}
- **${text.diataxis}**: ${diataxisLabel}
- **${text.module}**: ${moduleLine}
- **${text.milestone}**: ${entry.milestone || "—"}
- **${text.ref_doc}**: ${refDocLink}${reasonBlock}
:::

## ${text.h_what}

${summaryBlock}

## ${text.h_ours}

${ourBody}${branchBlock}

## ${text.h_related}

${relatedLinks.map(([t, u]) => `- [${t}](${u})`).join("\n")}
`;
}

function writeIfMissingOrSimple(filePath, contents) {
  ensureDir(path.dirname(filePath));
  if (fs.existsSync(filePath)) {
    const existing = fs.readFileSync(filePath, "utf8");
    if (existing.includes("<!-- generated:keep -->")) {
      return { kept: true };
    }
  }
  fs.writeFileSync(filePath, contents, "utf8");
  return { kept: false };
}

function buildSidebar(entries, locale) {
  // Group by top-level (entry.breadcrumb[0]); within each section, list direct
  // children and class leaves under a collapsible group.
  const sections = {};
  for (const e of entries) {
    const top = e.breadcrumb[0];
    if (!sections[top]) sections[top] = { items: [] };
    sections[top].items.push(e);
  }

  const sectionTitles = {
    introduction: { zh: "介绍", en: "Introduction" },
    manual: { zh: "用户手册", en: "Manual" },
    tutorials: { zh: "教程", en: "Tutorials" },
    extensions: { zh: "扩展", en: "Extensions" },
    api: { zh: "API 参考", en: "API reference" },
    misc: { zh: "杂项", en: "Misc" },
  };

  const sidebar = [];
  for (const [topKey, group] of Object.entries(sections)) {
    const items = group.items
      .filter((e) => e.breadcrumb.length === 1 || e.breadcrumb.length === 2 || (e.isClassLeaf && e.breadcrumb.length === 4))
      .map((e) => ({
        text: locale === "zh" ? e.title_zh : e.title_en,
        link: nodePath(e),
        depth: e.breadcrumb.length,
      }));
    sidebar.push({
      text: sectionTitles[topKey]?.[locale] ?? topKey,
      collapsed: topKey !== "introduction",
      items: items.map(({ text, link }) => ({ text, link })),
    });
  }
  return sidebar;
}

function buildTreeData(entries) {
  // Hierarchical structure for MirrorTree.vue
  const root = {};
  for (const e of entries) {
    let cursor = root;
    for (const seg of e.breadcrumb) {
      cursor.children = cursor.children || {};
      cursor.children[seg] = cursor.children[seg] || {};
      cursor = cursor.children[seg];
    }
    cursor.entry = {
      title_zh: e.title_zh,
      title_en: e.title_en,
      status: e.status,
      pillar: e.pillar,
      qchem: e.qchem,
      milestone: e.milestone,
      reference_url: e.reference_url,
      isClassLeaf: e.isClassLeaf,
      slug: nodePath(e),
    };
  }
  return root;
}

function summarizeStatuses(entries) {
  const counts = { shipped: 0, partial: 0, placeholder: 0, "not-applicable": 0 };
  for (const e of entries) {
    if (counts[e.status] !== undefined) counts[e.status] += 1;
  }
  counts.total = entries.length;
  return counts;
}

function main() {
  const raw = fs.readFileSync(manifestPath, "utf8");
  const tree = yaml.load(raw);
  const { site_meta, ...sections } = tree;

  const entries = [];
  for (const [k, v] of Object.entries(sections)) {
    entries.push(...flatten(v, k));
  }

  // For each entry, count how many descendants it has so renderPage can decide
  // whether to inject a <MirrorBranch> child listing on section pages.
  const descendantCounts = new Map();
  for (const e of entries) {
    const key = e.breadcrumb.join("/");
    descendantCounts.set(key, descendantCounts.get(key) ?? 0);
    for (let i = 1; i < e.breadcrumb.length; i++) {
      const ancestor = e.breadcrumb.slice(0, i).join("/");
      descendantCounts.set(ancestor, (descendantCounts.get(ancestor) ?? 0) + 1);
    }
  }

  let createdZh = 0;
  let createdEn = 0;
  for (const entry of entries) {
    const zhFile = path.join(docsRoot, "mirror", ...entry.breadcrumb, "index.md");
    const enFile = path.join(docsRoot, "en", "mirror", ...entry.breadcrumb, "index.md");
    const dc = descendantCounts.get(entry.breadcrumb.join("/")) ?? 0;
    if (writeIfMissingOrSimple(zhFile, renderPage(entry, "zh", dc)).kept === false) createdZh += 1;
    if (writeIfMissingOrSimple(enFile, renderPage(entry, "en", dc)).kept === false) createdEn += 1;
  }

  const treeData = buildTreeData(entries);
  const counts = summarizeStatuses(entries);
  const sidebarZh = buildSidebar(entries, "zh");
  const sidebarEn = buildSidebar(entries, "en");

  const dataDir = path.join(docsRoot, ".vitepress");
  ensureDir(dataDir);
  fs.writeFileSync(
    path.join(dataDir, "mirror-data.json"),
    JSON.stringify({ site_meta, counts, tree: treeData, entries }, null, 2),
    "utf8"
  );
  fs.writeFileSync(
    path.join(dataDir, "sidebar-mirror.json"),
    JSON.stringify({ zh: sidebarZh, en: sidebarEn }, null, 2),
    "utf8"
  );

  console.log(
    `scaffold-mirror: ${entries.length} mirror entries; wrote ${createdZh} zh + ${createdEn} en pages.`
  );
  console.log(`  status summary:`, counts);
}

main();
