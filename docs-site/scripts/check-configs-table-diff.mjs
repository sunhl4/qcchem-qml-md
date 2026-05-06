/**
 * Fails if generated config index pages differ from git HEAD (run after sync:configs-table).
 */
import { execSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const docsSiteRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(docsSiteRoot, "..");

const rel = [
  "docs-site/docs/product/configs-packaged-list.md",
  "docs-site/docs/en/product/configs-packaged-list.md",
];

execSync(`git diff --exit-code -- ${rel.map((r) => JSON.stringify(r)).join(" ")}`, {
  cwd: repoRoot,
  stdio: "inherit",
});
