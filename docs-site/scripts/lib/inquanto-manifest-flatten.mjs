/**
 * Single source for manifest → flat entries (breadcrumb, URLs, class leaves).
 * Used by: scaffold-mirror.mjs, export-inquanto-report-appendix.mjs,
 * export-inquanto-node-backlog.mjs, check-mirror-coverage (via mirror-data).
 */

export const INQUANTO_BASE = "https://docs.quantinuum.com/inquanto/";

/**
 * @param {object} node
 * @param {string} key
 * @param {string[]} parents
 * @param {string} inheritedPillar
 * @param {string} inheritedDiataxis
 * @returns {Array<{
 *   slug: string,
 *   breadcrumb: string[],
 *   title_zh: string,
 *   title_en: string,
 *   inquanto: string | null,
 *   diataxis: string,
 *   pillar: string,
 *   status: string,
 *   qchem: string | null,
 *   milestone: string | null,
 *   reason_zh: string | null,
 *   reason_en: string | null,
 *   summary_zh: string | null,
 *   summary_en: string | null,
 *   isClassLeaf: boolean
 * }>}
 */
export function flatten(
  node,
  key,
  parents = [],
  inheritedPillar = "meta",
  inheritedDiataxis = "reference"
) {
  if (!node || typeof node !== "object") return [];
  const out = [];
  const slug = key;
  const breadcrumb = [...parents, slug];
  const pillar = node.pillar ?? inheritedPillar;
  const diataxis = node.diataxis ?? inheritedDiataxis;

  if (slug !== "__root__" && slug !== "site_meta") {
    out.push({
      slug,
      breadcrumb,
      title_zh: node.title_zh ?? slug,
      title_en: node.title_en ?? slug,
      inquanto: node.inquanto
        ? node.inquanto.startsWith("http")
          ? node.inquanto
          : INQUANTO_BASE + node.inquanto
        : null,
      diataxis,
      pillar,
      status: node.status ?? "placeholder",
      qchem: node.qchem ?? null,
      milestone: node.milestone ?? null,
      reason_zh: node.reason_zh ?? null,
      reason_en: node.reason_en ?? null,
      summary_zh: node.summary_zh ?? null,
      summary_en: node.summary_en ?? null,
      isClassLeaf: false,
    });
  }

  if (node.children && typeof node.children === "object") {
    for (const [childKey, childNode] of Object.entries(node.children)) {
      out.push(...flatten(childNode, childKey, breadcrumb, pillar, diataxis));
    }
  }

  if (node.classes && typeof node.classes === "object") {
    for (const [className, classNode] of Object.entries(node.classes)) {
      const status = (classNode && classNode.status) ?? "placeholder";
      const qchem = (classNode && classNode.qchem) ?? null;
      const milestone = (classNode && classNode.milestone) ?? null;
      const reason_zh = (classNode && classNode.reason_zh) ?? null;
      const reason_en = (classNode && classNode.reason_en) ?? null;
      out.push({
        slug: className,
        breadcrumb: [...breadcrumb, "classes", className],
        title_zh: className,
        title_en: className,
        inquanto: node.inquanto
          ? (node.inquanto.startsWith("http") ? node.inquanto : INQUANTO_BASE + node.inquanto) +
            `#inquanto.${slug.replace(/^extensions_/, "extensions.")}.${className}`
          : null,
        diataxis,
        pillar,
        status,
        qchem,
        milestone,
        reason_zh,
        reason_en,
        summary_zh: null,
        summary_en: null,
        isClassLeaf: true,
      });
    }
  }

  return out;
}

export function mirrorSitePath(e) {
  return "/mirror/" + e.breadcrumb.join("/") + "/";
}

/** Top-level IA bucket from first breadcrumb segment. */
export function topBucket(e) {
  return e.breadcrumb[0] ?? "unknown";
}

/** Index: parent path "a/b/c" -> list of child display lines for sibling navigation. */
export function buildSiblingsIndex(entries) {
  const byParent = new Map();
  for (const e of entries) {
    if (e.breadcrumb.length < 2) continue;
    const parent = e.breadcrumb.slice(0, -1).join("/");
    if (!byParent.has(parent)) byParent.set(parent, []);
    byParent.get(parent).push({
      slug: e.slug,
      title_en: e.title_en,
      title_zh: e.title_zh,
      status: e.status,
      isClassLeaf: e.isClassLeaf,
    });
  }
  return byParent;
}
