/**
 * Regenerates packaged-config index pages from qchem_qml_md/configs/*.yaml.
 * Run from docs-site: npm run sync:configs-table
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const docsSiteRoot = path.resolve(__dirname, "..");
const repoRoot = path.resolve(docsSiteRoot, "..");
const configsDir = path.join(repoRoot, "configs");

const files = fs.existsSync(configsDir)
  ? fs.readdirSync(configsDir).filter((f) => f.endsWith(".yaml")).sort()
  : [];

const rows = files.map((f) => `| \`configs/${f}\` |`).join("\n");

const zhBody = `---
title: 仓库 configs 索引
description: 由 sync-configs-table 自动生成；与 qchem_qml_md/configs/*.yaml 同步
---

<!-- @generated: scripts/sync-configs-table.mjs — do not edit the table by hand -->

与 [产品功能 · 示例配置](/product/features) 中的**主题导读**互补：下表为当前仓库内全部打包 YAML 的**机械清单**（改 \`configs/\` 后请运行 \`npm run sync:configs-table\`）。

| 文件（相对仓库根 \`qchem_qml_md/\`） |
| --- |
${rows || "| （未找到 configs/*.yaml） |"}
`;

const enBody = `---
title: Packaged configs index
description: Auto-generated from qchem_qml_md/configs/*.yaml via sync-configs-table
---

<!-- @generated: scripts/sync-configs-table.mjs — do not edit the table by hand -->

Companion to the **curated** table on [Product features](/en/product/features): this is the **machine** list of every \`configs/*.yaml\` on disk (re-run \`npm run sync:configs-table\` after adding files).

| File (relative to \`qchem_qml_md/\` repo root) |
| --- |
${rows || "| (no configs/*.yaml found) |"}
`;

const zhOut = path.join(docsSiteRoot, "docs", "product", "configs-packaged-list.md");
const enOut = path.join(docsSiteRoot, "docs", "en", "product", "configs-packaged-list.md");

fs.mkdirSync(path.dirname(zhOut), { recursive: true });
fs.mkdirSync(path.dirname(enOut), { recursive: true });
fs.writeFileSync(zhOut, zhBody, "utf8");
fs.writeFileSync(enOut, enBody, "utf8");

console.log(`Wrote ${files.length} rows → ${path.relative(docsSiteRoot, zhOut)}, ${path.relative(docsSiteRoot, enOut)}`);
