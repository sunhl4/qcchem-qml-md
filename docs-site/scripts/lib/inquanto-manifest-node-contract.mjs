/**
 * Appendix-C–aligned contract fields for machine-readable backlog (JSON).
 * Keeps checklist prose in sync with export-inquanto-report-appendix.mjs intent.
 */

import { topBucket } from "./inquanto-manifest-flatten.mjs";

export function acceptanceChecklist(e) {
  const lines = acceptanceBlockRaw(e);
  return lines.split("\n").filter(Boolean);
}

/** One bullet per line (markdown), same as appendix §4 risks. */
export function risksMarkdown(e) {
  return riskBlockRaw(e).split("\n").filter(Boolean);
}

/** Structured §11 platform checklist (Vol.08 /cloud/ alignment). */
export function platformDimensions(e) {
  const p4 =
    e.pillar === "P4"
      ? "`GET/POST /v1/runs`、`repro` 须有 **API 表或控制台等价说明**。"
      : null;
  return {
    cloud_tenant:
      "`launch/retrieve`、Nexus、远程设备 — `n/a` 者写清 **SQLite+FastAPI 类比**；其余在 `/cloud/` 文档化 **workspace_label、配额、公平队列**。",
    backend_observability: "P3 对照 **BackendSpec**；作业 **trace/request id** 对齐 HTTP 契约。",
    security_compliance: "禁止示例 YAML 写生产密钥；PII 保留与审计日志策略进 `/cloud/`。",
    seo_url: "厂商锚点变更回写 manifest；本站 slug 以 IA_MAPPING 为真源。",
    i18n: "shipped/partial 优先 `/en/` 叙事；mirror 为审计入口。",
    ci: "外链存活巡检；教程命令可选 smoke。",
    ...(p4 ? { p4_jobs_api: p4 } : {}),
  };
}

export function openQuestionsDefault() {
  return [
    "公开页自 `source_pin_date` 以来是否结构重排？",
    "是否纳入 **L3 数值基准** 或云平台 **配额/成本** 默认策略？",
  ];
}

function acceptanceBlockRaw(e) {
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

function riskBlockRaw(e) {
  const risks = [];
  if (e.status === "partial") risks.push("- **R1（语义漂移）**: 公开文档更新导致我们 `partial` 说明过时 — 需版本钉扎 + CI 文档检查。");
  if (e.status === "placeholder") risks.push("- **R2（期望管理）**: 读者从 InQuanto 跳转时期望已实现 — Mirror 页必须醒目展示 **占位** 徽章与里程碑。");
  if (e.isClassLeaf) risks.push("- **R3（API 巨石页）**: 上游单 HTML 过大 — 我们已拆类叶 URL；注意同步锚点若上游改符号名。");
  if (topBucket(e) === "extensions" && e.status !== "not-applicable")
    risks.push("- **R4（依赖地狱）**: 扩展版本与 core 不兼容 — 文档需锁定 **受支持版本矩阵**。");
  if (risks.length === 0) risks.push("- **R0**: 无 manifest 级特有风险标记 — 仍建议每季度做一次链接存活检查。");
  return risks.join("\n");
}

/** @returns {("mirror_audit"|"repro_contract"|"cloud_tenant"|"multi_backend"|"parity_evidence")[]} */
export function differentiatorFocus(e) {
  const f = new Set();
  const top = topBucket(e);
  const bc = e.breadcrumb.join("/");

  if (["introduction", "misc", "extensions"].includes(top) || (top === "api" && !e.isClassLeaf && String(e.slug).includes("intro")))
    f.add("mirror_audit");
  if (e.pillar === "P4" || bc.includes("async") || /nexus/i.test(bc)) f.add("cloud_tenant");
  if (e.pillar === "P3" || (top === "tutorials" && bc.includes("backend"))) f.add("multi_backend");
  if ((e.status === "shipped" || e.status === "partial") && e.qchem) f.add("parity_evidence");
  if (
    e.pillar === "P2" &&
    (top === "manual" || top === "api") &&
    (bc.includes("protocols") || bc.includes("computables") || bc.includes("algorithms"))
  )
    f.add("repro_contract");
  if (e.isClassLeaf) f.add("mirror_audit");

  if (f.size === 0) f.add("mirror_audit");
  return [...f];
}

export function suggestedInternalRoutes(e) {
  const mp = "/mirror/" + e.breadcrumb.join("/") + "/";
  const routes = new Set([mp]);
  const focus = differentiatorFocus(e);
  if (focus.includes("cloud_tenant")) {
    routes.add("/cloud/");
    routes.add("/cloud/tenant-and-quotas");
    routes.add("/cloud/jobs-and-logs");
  }
  if (focus.includes("parity_evidence") || e.status === "partial") routes.add("/parity/public-matrix");
  if (focus.includes("repro_contract")) routes.add("/guide/jobs-and-reproducibility/");
  if (e.pillar === "P1") routes.add("/guide/chemistry-and-embedding/");
  else if (e.pillar === "P2") routes.add("/guide/algorithms-and-protocols/");
  else if (e.pillar === "P3") routes.add("/guide/execution-and-analysis/");
  else if (e.pillar === "P4") routes.add("/guide/jobs-and-reproducibility/");
  else {
    routes.add("/guide/");
    routes.add("/product/");
  }
  routes.add("/concept/engineering-architecture");
  return [...routes];
}

export function parityDocHint(e) {
  if (e.status === "not-applicable")
    return "优先阅读 `docs/inquanto_public_parity_matrix.md` 与 `docs/concept/architecture-boundaries` 中的 n/a 口径。";
  if (e.status === "partial" || e.status === "shipped")
    return "`docs/inquanto_public_parity_matrix.md` — 按 `qchem_module` 或能力名检索对应行；无行则开新 gap 行。";
  return "`docs/inquanto_public_parity_matrix.md` — placeholder 能力在矩阵中保持诚实未宣称。";
}
