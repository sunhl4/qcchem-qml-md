/**
 * Validates inquanto-node-backlog.generated.json vs manifest flatten + mirror-data.
 * No external deps (light schema checks only).
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import yaml from "js-yaml";
import { flatten } from "./lib/inquanto-manifest-flatten.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoDocs = path.join(__dirname, "..", "..", "docs");
const manifestPath = path.join(__dirname, "inquanto-tree.yaml");
const backlogPath = path.join(repoDocs, "inquanto-node-backlog.generated.json");
const mirrorDataPath = path.join(__dirname, "..", "docs", ".vitepress", "mirror-data.json");

const FOCUS = new Set(["mirror_audit", "repro_contract", "cloud_tenant", "multi_backend", "parity_evidence"]);
const PLATFORM_KEYS = new Set([
  "cloud_tenant",
  "backend_observability",
  "security_compliance",
  "seo_url",
  "i18n",
  "ci",
]);

function loadFlattened() {
  const raw = fs.readFileSync(manifestPath, "utf8");
  const tree = yaml.load(raw);
  const { site_meta, ...sections } = tree;
  const entries = [];
  for (const [k, v] of Object.entries(sections)) {
    entries.push(...flatten(v, k));
  }
  return { entries, site_meta };
}

function validateNode(n, i) {
  const errs = [];
  const req = [
    "appendix_c_node_index",
    "breadcrumb",
    "slug",
    "mirror_site_path",
    "pillar",
    "status",
    "acceptance_checklist",
    "risks",
    "platform_dimensions",
    "open_questions",
    "differentiator_focus",
    "suggested_internal_routes",
    "parity_doc_hint",
  ];
  for (const k of req) {
    if (!(k in n)) errs.push(`node[${i}] missing ${k}`);
  }
  if (n.appendix_c_node_index !== i + 1) errs.push(`node[${i}] appendix_c_node_index ${n.appendix_c_node_index} !== ${i + 1}`);
  if (!Array.isArray(n.differentiator_focus) || n.differentiator_focus.length < 1)
    errs.push(`node[${i}] differentiator_focus invalid`);
  for (const f of n.differentiator_focus ?? []) {
    if (!FOCUS.has(f)) errs.push(`node[${i}] bad focus: ${f}`);
  }
  const pd = n.platform_dimensions;
  if (!pd || typeof pd !== "object") errs.push(`node[${i}] platform_dimensions missing`);
  else {
    for (const k of PLATFORM_KEYS) {
      if (typeof pd[k] !== "string") errs.push(`node[${i}] platform_dimensions.${k} not string`);
    }
  }
  return errs;
}

function main() {
  const violations = [];

  if (!fs.existsSync(backlogPath)) {
    console.error(`Missing ${backlogPath}; run npm run report:inquanto-backlog`);
    process.exit(2);
  }

  const doc = JSON.parse(fs.readFileSync(backlogPath, "utf8"));
  if (!doc.meta || !Array.isArray(doc.nodes)) {
    console.error("Backlog JSON must have meta + nodes");
    process.exit(1);
  }

  const { entries } = loadFlattened();

  if (doc.nodes.length !== entries.length) {
    violations.push(`nodes.length ${doc.nodes.length} !== manifest flatten ${entries.length}`);
  }
  if (doc.meta.node_count !== doc.nodes.length) {
    violations.push(`meta.node_count ${doc.meta.node_count} !== nodes.length ${doc.nodes.length}`);
  }

  if (fs.existsSync(mirrorDataPath)) {
    const mirror = JSON.parse(fs.readFileSync(mirrorDataPath, "utf8"));
    const mlen = mirror.entries?.length ?? 0;
    if (mlen !== doc.nodes.length) {
      violations.push(`mirror-data.json entries ${mlen} !== backlog nodes ${doc.nodes.length}`);
    }
  }

  const n = Math.min(doc.nodes.length, entries.length);
  for (let i = 0; i < n; i++) {
    const a = doc.nodes[i].breadcrumb.join("/");
    const b = entries[i].breadcrumb.join("/");
    if (a !== b) violations.push(`breadcrumb order mismatch at ${i + 1}: backlog "${a}" vs manifest "${b}"`);
    violations.push(...validateNode(doc.nodes[i], i));
  }

  if (violations.length) {
    console.error(`check-inquanto-node-backlog FAIL (${violations.length}):`);
    for (const v of violations.slice(0, 40)) console.error(`  - ${v}`);
    if (violations.length > 40) console.error(`  ... and ${violations.length - 40} more`);
    process.exit(1);
  }

  console.log(`node backlog OK: ${doc.nodes.length} nodes, meta schema_version=${doc.meta.schema_version}`);
  process.exit(0);
}

main();
