/**
 * Writes machine-readable Y1 node backlog (295 rows) from inquanto-tree.yaml,
 * aligned with appendix C contract fields + differentiator extensions.
 *
 * Default: ../../docs/inquanto-node-backlog.generated.{json,md}
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import yaml from "js-yaml";
import { flatten, mirrorSitePath } from "./lib/inquanto-manifest-flatten.mjs";
import {
  acceptanceChecklist,
  differentiatorFocus,
  openQuestionsDefault,
  parityDocHint,
  platformDimensions,
  risksMarkdown,
  suggestedInternalRoutes,
} from "./lib/inquanto-manifest-node-contract.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const manifestPath = path.join(__dirname, "inquanto-tree.yaml");
const defaultDocsRoot = path.join(__dirname, "..", "..", "docs");

function main() {
  const outDir = path.resolve(process.argv[2] || defaultDocsRoot);
  fs.mkdirSync(outDir, { recursive: true });

  const raw = fs.readFileSync(manifestPath, "utf8");
  const tree = yaml.load(raw);
  const { site_meta, ...sections } = tree;

  const entries = [];
  for (const [k, v] of Object.entries(sections)) {
    entries.push(...flatten(v, k));
  }

  const nodes = entries.map((e, i) => ({
    appendix_c_node_index: i + 1,
    breadcrumb: e.breadcrumb,
    slug: e.slug,
    title_zh: e.title_zh,
    title_en: e.title_en,
    inquanto_anchor: e.inquanto,
    mirror_site_path: mirrorSitePath(e),
    pillar: e.pillar,
    diataxis: e.diataxis,
    status: e.status,
    is_class_leaf: e.isClassLeaf,
    milestone: e.milestone,
    qchem_module: e.qchem,
    reason_zh: e.reason_zh,
    reason_en: e.reason_en,
    summary_zh: e.summary_zh,
    summary_en: e.summary_en,
    acceptance_checklist: acceptanceChecklist(e),
    risks: risksMarkdown(e),
    platform_dimensions: platformDimensions(e),
    open_questions: openQuestionsDefault(),
    differentiator_focus: differentiatorFocus(e),
    suggested_internal_routes: suggestedInternalRoutes(e),
    parity_doc_hint: parityDocHint(e),
    source_pin_date: site_meta?.source_pin_date ?? null,
    inquanto_version_seen: site_meta?.inquanto_version_seen ?? null,
  }));

  const doc = {
    meta: {
      schema_version: 1,
      source_pin_date: site_meta?.source_pin_date ?? null,
      inquanto_version_seen: site_meta?.inquanto_version_seen ?? null,
      source_root: site_meta?.source_root ?? null,
      node_count: nodes.length,
      manifest_path: "docs-site/scripts/inquanto-tree.yaml",
      appendix_c_relative:
        "docs/architecture-report-quantinuum-inquanto-web/appendix-C-deep-node-architecture.generated.md",
    },
    nodes,
  };

  const jsonPath = path.join(outDir, "inquanto-node-backlog.generated.json");
  fs.writeFileSync(jsonPath, JSON.stringify(doc, null, 2), "utf8");

  const mdLines = [
    "---",
    "title: InQuanto node backlog index (generated)",
    `description: ${nodes.length} manifest nodes — machine JSON sibling; waves / CI see Y1 ledger.`,
    "edit: false",
    "---",
    "",
    "> **Do not hand-edit.** Regenerate: `npm run report:inquanto-backlog` from `docs-site/`.",
    "",
    `- **JSON**: [inquanto-node-backlog.generated.json](./inquanto-node-backlog.generated.json)`,
    `- **Schema**: [inquanto-node-backlog.schema.json](./inquanto-node-backlog.schema.json)`,
    `- **Deep narrative**: [architecture-report-quantinuum-inquanto-web/appendix-C-deep-node-architecture.generated.md](./architecture-report-quantinuum-inquanto-web/appendix-C-deep-node-architecture.generated.md)`,
    "",
    "## Index (compact)",
    "",
    "| # | breadcrumb | status | pillar | mirror | differentiator_focus |",
    "|---|------------|--------|--------|--------|----------------------|",
  ];

  for (const n of nodes) {
    const bc = n.breadcrumb.join("/");
    const df = n.differentiator_focus.join(", ");
    mdLines.push(
      `| ${n.appendix_c_node_index} | \`${bc}\` | ${n.status} | ${n.pillar} | \`${n.mirror_site_path}\` | ${df} |`
    );
  }

  fs.writeFileSync(path.join(outDir, "inquanto-node-backlog.generated.md"), mdLines.join("\n") + "\n", "utf8");

  console.log(`export-inquanto-node-backlog: wrote ${nodes.length} nodes to`);
  console.log(`  ${jsonPath}`);
  console.log(`  ${path.join(outDir, "inquanto-node-backlog.generated.md")}`);
}

main();
