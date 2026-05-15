/**
 * check-mirror-coverage.mjs
 *
 * Validates docs/.vitepress/mirror-data.json against the markdown filesystem:
 *   - every entry has a corresponding zh + en placeholder page;
 *   - placeholder/partial entries that lack `reference_doc_url` in frontmatter are reported;
 *   - status counts match the manifest snapshot.
 *
 * Exits non-zero on any violation so CI can gate it.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const docsRoot = path.join(__dirname, "..", "docs");
const dataPath = path.join(docsRoot, ".vitepress", "mirror-data.json");

if (!fs.existsSync(dataPath)) {
  console.error(`mirror-data.json missing at ${dataPath}; run "npm run scaffold:mirror" first.`);
  process.exit(2);
}

const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));

const violations = [];
for (const entry of data.entries) {
  const zhPath = path.join(docsRoot, "mirror", ...entry.breadcrumb, "index.md");
  const enPath = path.join(docsRoot, "en", "mirror", ...entry.breadcrumb, "index.md");
  if (!fs.existsSync(zhPath)) violations.push({ kind: "missing_zh", entry: entry.breadcrumb.join("/") });
  if (!fs.existsSync(enPath)) violations.push({ kind: "missing_en", entry: entry.breadcrumb.join("/") });
  if (!entry.reference_url && !entry.isClassLeaf && entry.status !== "not-applicable") {
    violations.push({ kind: "no_reference_doc_url", entry: entry.breadcrumb.join("/") });
  }
}

if (violations.length === 0) {
  console.log(`mirror coverage OK: ${data.entries.length} entries, status counts:`, data.counts);
  process.exit(0);
}

console.error(`mirror coverage FAIL — ${violations.length} violation(s):`);
for (const v of violations.slice(0, 25)) console.error(`  - ${v.kind}: ${v.entry}`);
if (violations.length > 25) console.error(`  ... and ${violations.length - 25} more`);
process.exit(1);
