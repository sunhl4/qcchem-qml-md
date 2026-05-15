/**
 * One-shot replacement of repo-relative .md links to VitePress routes (run after copying docs).
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const docsRoot = path.join(__dirname, "..", "docs");

const MAP = [
  ["ENGINEERING_ARCHITECTURE.md", "/concept/engineering-architecture"],
  ["技术文档_HTTP_API与SQLite作业队列及可观测性契约.md", "/reference/http-api-sqlite-jobs"],
  ["技术文档_CircuitIR与TKET桥接及作业契约.md", "/reference/circuitir-tket-jobs"],
  ["技术文档_设备比特串与Qiskit采样路径.md", "/reference/qiskit-shot-counts"],
  ["技术文档_DMET与parity_snapshot开放契约.md", "/reference/dmet-parity-snapshot"],
  ["launch_retrieve_nexus_analog.md", "/concept/launch-retrieve-nexus-analog"],
  ["mitigation_PMSV_ZNE_Qermit_mapping.md", "/concept/mitigation-mapping"],
  ["inquanto_public_parity_matrix.md", "/product/roadmap"],
  ["L1_InQuanto_alignment_signoff.md", "/product/roadmap"],
  ["InQuanto_Y1_public_alignment_ledger.md", "/product/roadmap"],
  ["Y1_residual_partial_SLA_template.md", "/product/roadmap#y1-residual-partial-sla-template"],
  ["与InQuanto能力差距与实施计划.md", "/product/roadmap"],
  ["与Inquanto能力差距与实施计划.md", "/product/roadmap"],
  ["竞争定位与路线图_对标Quantinuum产品与技术路线.md", "/product/roadmap"],
  ["工程记忆_Quantinuum对标与数据流技术文档.md", "/concept/engineering-architecture"],
  ["L3_benchmark_suite_roadmap.md", "/product/roadmap#l3-benchmark-suite-roadmap"],
  ["记忆_开放栈对标完成度与待闭合项.md", "/concept/engineering-architecture#13-开放栈对标完成度与待闭合项原独立记忆合并"],
  ["记忆_HTTP_API与作业队列_工程记忆.md", "/reference/http-api-sqlite-jobs#9-工程决策与范围原独立http-工程记忆合并"],
  ["不排期项_转排期与实现说明.md", "/product/roadmap"],
  ["架构_InQuanto闭源能力闭合与可复现边界.md", "/concept/architecture-boundaries"],
  ["ADR_P2_decomposition_scope.md", "/product/roadmap#adr-p2-w2-decomposition-scope"],
  ["P2_W3_classical_avas_casscf_boundary.md", "/product/roadmap#p2-w3-avas-casscf-boundary"],
  ["P2_W5_algorithm_registry_alignment.md", "/product/roadmap#p2-w5-algorithm-registry-alignment"],
  ["P2_详细实施计划.md", "/product/roadmap#appendix-a"],
  ["P1_completion_audit.md", "/product/roadmap#appendix-e"],
  ["InQuanto_B_J_逐项闭合计划.md", "/product/roadmap#appendix-d"],
  ["InQuanto_manual_howto_与_qchem_stack_映射.md", "/concept/engineering-architecture"],
];

// Skip auto-generated trees so this one-shot fixer never overwrites them.
const SKIP_DIRS = new Set([".vitepress", "mirror", "en"]);

function walk(dir, out = []) {
  for (const name of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, name.name);
    if (name.isDirectory()) {
      if (SKIP_DIRS.has(name.name)) continue;
      walk(p, out);
    } else if (name.name.endsWith(".md")) out.push(p);
  }
  return out;
}

for (const file of walk(docsRoot)) {
  let n = fs.readFileSync(file, "utf8");
  const s = n;
  for (const [from, to] of MAP) {
    const escaped = from.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const re = new RegExp(`\\]\\(${escaped}(#[^)]+)?\\)`, "g");
    n = n.replace(re, (_, anchor) => `](${to}${anchor || ""})`);
  }
  n = n.replace(/\]\(\.\.\/README\.md\)/g, "](/tutorial/quickstart)");
  n = n.replace(
    /\[`docs\/inquanto_public_parity_matrix\.md`\]\([^)]*\)/g,
    "[公开 parity 矩阵](/product/roadmap)"
  );
  if (n !== s) fs.writeFileSync(file, n, "utf8");
}

console.log("patched internal links in", walk(docsRoot).length, "markdown files");
