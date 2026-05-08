import { defineConfig } from "vitepress";
import { withMermaid } from "vitepress-plugin-mermaid";
import mirrorSidebar from "./sidebar-mirror.json" with { type: "json" };

const conceptItemsZh = [
  { text: "工程分层架构", link: "/concept/engineering-architecture" },
  { text: "竞争定位与路线图", link: "/concept/competitive-positioning" },
  { text: "工程记忆（Quantinuum · 物化链）", link: "/concept/engineering-memory-quantinuum" },
  { text: "P2 详细实施计划", link: "/concept/p2-detailed-plan" },
  { text: "架构边界（闭源对照）", link: "/concept/architecture-boundaries" },
  { text: "Launch / Retrieve（Nexus 类比）", link: "/concept/launch-retrieve-nexus-analog" },
  { text: "缓解映射（PMSV / ZNE / Qermit）", link: "/concept/mitigation-mapping" },
];

const referenceItemsZh = [
  { text: "命令行与脚本", link: "/reference/cli-and-scripts" },
  { text: "HTTP API · SQLite 作业", link: "/reference/http-api-sqlite-jobs" },
  { text: "CircuitIR · TKET · 作业契约", link: "/reference/circuitir-tket-jobs" },
  { text: "Qiskit 比特串采样", link: "/reference/qiskit-shot-counts" },
  { text: "DMET · parity_snapshot", link: "/reference/dmet-parity-snapshot" },
];

const referenceItemsEn = [
  { text: "CLI & scripts", link: "/en/reference/cli-and-scripts" },
  { text: "HTTP API · SQLite jobs", link: "/en/reference/http-api-sqlite-jobs" },
  { text: "CircuitIR · TKET · jobs", link: "/en/reference/circuitir-tket-jobs" },
  { text: "Qiskit shot counts", link: "/en/reference/qiskit-shot-counts" },
  { text: "DMET · parity_snapshot", link: "/en/reference/dmet-parity-snapshot" },
];

const conceptItemsEn = [
  { text: "Engineering architecture", link: "/en/concept/engineering-architecture" },
  { text: "Competitive positioning", link: "/en/concept/competitive-positioning" },
  { text: "P2 implementation plan", link: "/en/concept/p2-detailed-plan" },
  { text: "Architecture boundaries", link: "/en/concept/architecture-boundaries" },
  { text: "Engineering memory (Quantinuum)", link: "/en/concept/engineering-memory-quantinuum" },
  { text: "Launch / Retrieve (Nexus analog)", link: "/en/concept/launch-retrieve-nexus-analog" },
  { text: "Mitigation mapping", link: "/en/concept/mitigation-mapping" },
  { text: "HTTP API worker memory", link: "/en/concept/http-api-worker-memory" },
];

const parityItemsZh = [
  { text: "公开契约矩阵", link: "/parity/public-matrix" },
  { text: "差距与实施计划", link: "/parity/gap-implementation-plan" },
  { text: "L1 签 off", link: "/parity/l1-signoff" },
  { text: "Y1 对标台账", link: "/parity/y1-alignment-ledger" },
  { text: "Y1 残余 SLA 模板", link: "/parity/y1-alignment-ledger#y1-residual-partial-sla-template" },
  { text: "L3 基准路线图", link: "/parity/y1-alignment-ledger#l3-benchmark-suite-roadmap" },
  { text: "开放栈记忆", link: "/parity/open-stack-memory" },
  { text: "迭代说明", link: "/parity/backlog-to-schedule" },
];

const parityItemsEn = [
  { text: "Parity matrix", link: "/en/parity/public-matrix" },
  { text: "L1 sign-off", link: "/en/parity/l1-signoff" },
  { text: "Gap plan (ZH)", link: "/parity/gap-implementation-plan" },
  { text: "Y1 ledger (ZH)", link: "/parity/y1-alignment-ledger" },
  { text: "Y1 SLA template (ZH)", link: "/parity/y1-alignment-ledger#y1-residual-partial-sla-template" },
  { text: "L3 benchmark (ZH)", link: "/parity/y1-alignment-ledger#l3-benchmark-suite-roadmap" },
  { text: "Open-stack memory (ZH)", link: "/parity/open-stack-memory" },
  { text: "Backlog to schedule (ZH)", link: "/parity/backlog-to-schedule" },
];

const guideItemsZh = [
  { text: "总览", link: "/guide/" },
  { text: "新用户三条路径", link: "/guide/onboarding-three-paths" },
  { text: "原理与阅读建议", link: "/guide/principles-and-reading" },
  { text: "P1 化学与嵌入", link: "/guide/chemistry-and-embedding/" },
  { text: "多后端统一适配合同", link: "/guide/chemistry-and-embedding/backend-adapter-unified-io" },
  { text: "后端适配快速接入", link: "/guide/chemistry-and-embedding/backend-adapter-quickstart" },
  { text: "InQuanto-PySCF 量子问题对照", link: "/guide/chemistry-and-embedding/inquanto-pyscf-problem-analog" },
  { text: "二次量子化读表（Fock / Hamiltonian）", link: "/guide/chemistry-and-embedding/second-quantization-fock-hamiltonian-readout" },
  { text: "P2 算法与协议", link: "/guide/algorithms-and-protocols/" },
  { text: "P3 执行与分析", link: "/guide/execution-and-analysis/" },
  { text: "P4 作业与可复现", link: "/guide/jobs-and-reproducibility/" },
];

const guideItemsEn = [
  { text: "Overview", link: "/en/guide/" },
  { text: "Three onboarding paths", link: "/en/guide/onboarding-three-paths" },
  { text: "Principles & reading", link: "/en/guide/principles-and-reading" },
  { text: "P1 Chemistry & embedding", link: "/en/guide/chemistry-and-embedding/" },
  { text: "Unified backend adapter I/O contract", link: "/en/guide/chemistry-and-embedding/backend-adapter-unified-io" },
  { text: "Backend adapter quickstart", link: "/en/guide/chemistry-and-embedding/backend-adapter-quickstart" },
  { text: "InQuanto-PySCF analog (quantum problem)", link: "/en/guide/chemistry-and-embedding/inquanto-pyscf-problem-analog" },
  { text: "Second quantization (Fock & Hamiltonian)", link: "/en/guide/chemistry-and-embedding/second-quantization-fock-hamiltonian-readout" },
  { text: "P2 Algorithms & protocols", link: "/en/guide/algorithms-and-protocols/" },
  { text: "P3 Execution & analysis", link: "/en/guide/execution-and-analysis/" },
  { text: "P4 Jobs & reproducibility", link: "/en/guide/jobs-and-reproducibility/" },
];

const productItemsZh = [
  { text: "产品功能", link: "/product/features" },
  { text: "configs 索引（自动生成）", link: "/product/configs-packaged-list" },
  { text: "定位与路线", link: "/product/" },
  { text: "路线图", link: "/product/roadmap" },
];
const productItemsEn = [
  { text: "Product features", link: "/en/product/features" },
  { text: "Configs index (generated)", link: "/en/product/configs-packaged-list" },
  { text: "Positioning & roadmap", link: "/en/product/" },
  { text: "Roadmap", link: "/en/product/roadmap" },
];

const productNavZh = [
  { text: "产品功能", link: "/product/features" },
  { text: "定位与路线", link: "/product/" },
  { text: "路线图", link: "/product/roadmap" },
];
const productNavEn = [
  { text: "Features", link: "/en/product/features" },
  { text: "Positioning", link: "/en/product/" },
  { text: "Roadmap", link: "/en/product/roadmap" },
];

const cloudItemsZh = [
  { text: "概述", link: "/cloud/" },
  { text: "租户与配额", link: "/cloud/tenant-and-quotas" },
  { text: "后端注册表", link: "/cloud/backend-registry" },
  { text: "作业与日志", link: "/cloud/jobs-and-logs" },
];

const cloudItemsEn = [
  { text: "Overview", link: "/en/cloud/" },
  { text: "Tenant & quotas", link: "/en/cloud/tenant-and-quotas" },
  { text: "Backend registry", link: "/en/cloud/backend-registry" },
  { text: "Jobs & logs", link: "/en/cloud/jobs-and-logs" },
];

const metaItemsZh = [
  { text: "站点地图（IA）", link: "/meta/ia-mapping" },
  { text: "首页与指南线框", link: "/meta/wireframe-home-and-guides" },
  { text: "SSG 与搜索策略", link: "/meta/ssg-search-strategy" },
  { text: "Diátaxis 文档类型索引", link: "/meta/diataxis-index" },
  { text: "InQuanto 模块复现骨架", link: "/meta/inquanto-module-scaffold" },
  { text: "安全与数据", link: "/meta/security-and-data" },
];

const metaItemsEn = [
  { text: "Site map (IA)", link: "/en/meta/ia-mapping" },
  { text: "Home & guides wireframe", link: "/en/meta/wireframe-home-and-guides" },
  { text: "SSG & search strategy", link: "/en/meta/ssg-search-strategy" },
  { text: "Diátaxis index", link: "/en/meta/diataxis-index" },
  { text: "InQuanto module scaffold", link: "/en/meta/inquanto-module-scaffold" },
  { text: "Security & data", link: "/en/meta/security-and-data" },
];

/** Mirror routes — same L1 keys as public InQuanto Manual (`inquanto-tree.yaml`). */
const introductionNavZh = [
  { text: "概览", link: "/mirror/introduction/overview/" },
  { text: "安装", link: "/mirror/introduction/installation/" },
  { text: "快速上手（镜像）", link: "/mirror/introduction/quickstart/" },
  { text: "本站教程 · 快速上手", link: "/tutorial/quickstart" },
];
const introductionNavEn = [
  { text: "Overview", link: "/en/mirror/introduction/overview/" },
  { text: "Installation", link: "/en/mirror/introduction/installation/" },
  { text: "Quick-start (mirror)", link: "/en/mirror/introduction/quickstart/" },
  { text: "Quickstart (site)", link: "/en/tutorial/quickstart" },
];

const manualMirrorNavZh = [
  { text: "如何使用 InQuanto", link: "/mirror/manual/howto/" },
  { text: "几何", link: "/mirror/manual/geometry/" },
  { text: "Express 数据集", link: "/mirror/manual/express/" },
  { text: "对称性", link: "/mirror/manual/symmetry/" },
  { text: "空间 / 算符 / 状态 / 映射", link: "/mirror/manual/spaces_operators/" },
  { text: "Ansatze", link: "/mirror/manual/ansatze/" },
  { text: "极小化器", link: "/mirror/manual/minimizers/" },
  { text: "Computables", link: "/mirror/manual/computables/" },
  { text: "Protocols", link: "/mirror/manual/protocols/" },
  { text: "Algorithms", link: "/mirror/manual/algorithms/" },
  { text: "嵌入与 DMET", link: "/mirror/manual/embedding/" },
  { text: "噪声缓解", link: "/mirror/manual/noise_mitigation/" },
];
const manualMirrorNavEn = [
  { text: "How to use InQuanto", link: "/en/mirror/manual/howto/" },
  { text: "Geometry", link: "/en/mirror/manual/geometry/" },
  { text: "Express data sets", link: "/en/mirror/manual/express/" },
  { text: "Symmetry", link: "/en/mirror/manual/symmetry/" },
  { text: "Spaces, operators, states", link: "/en/mirror/manual/spaces_operators/" },
  { text: "Ansatze", link: "/en/mirror/manual/ansatze/" },
  { text: "Minimizers", link: "/en/mirror/manual/minimizers/" },
  { text: "Computables", link: "/en/mirror/manual/computables/" },
  { text: "Protocols", link: "/en/mirror/manual/protocols/" },
  { text: "Algorithms", link: "/en/mirror/manual/algorithms/" },
  { text: "Embedding & DMET", link: "/en/mirror/manual/embedding/" },
  { text: "Noise mitigation", link: "/en/mirror/manual/noise_mitigation/" },
];

const tutorialsNavZh = [
  { text: "教程索引（镜像）", link: "/mirror/tutorials/" },
  { text: "15 分钟上手", link: "/tutorial/quickstart" },
  { text: "工作流与 YAML", link: "/tutorial/workflow-overview" },
  { text: "UCCSD Trotter + export", link: "/tutorial/uccsd-trotter-export" },
  { text: "ZNE × Qiskit repro", link: "/tutorial/zne-qiskit-repro" },
  { text: "Projection 嵌入深入", link: "/tutorial/projection-embedding-deep-dive" },
  { text: "HTTP 异步运行", link: "/tutorial/async-run-via-http" },
  { text: "repro 键速览", link: "/tutorial/read-repro-keys" },
  { text: "切换 backend", link: "/tutorial/switch-backend-compare" },
];
const tutorialsNavEn = [
  { text: "Tutorials (mirror)", link: "/en/mirror/tutorials/" },
  { text: "Quickstart", link: "/en/tutorial/quickstart" },
  { text: "Workflow & YAML", link: "/en/tutorial/workflow-overview" },
  { text: "UCCSD Trotter + export", link: "/en/tutorial/uccsd-trotter-export" },
  { text: "ZNE × Qiskit repro", link: "/en/tutorial/zne-qiskit-repro" },
  { text: "Projection embedding deep dive", link: "/en/tutorial/projection-embedding-deep-dive" },
  { text: "Async run via HTTP", link: "/en/tutorial/async-run-via-http" },
  { text: "Ten repro keys", link: "/en/tutorial/read-repro-keys" },
  { text: "Compare backends", link: "/en/tutorial/switch-backend-compare" },
];

const apiNavZh = [
  { text: "API 索引（镜像）", link: "/mirror/api/" },
  ...referenceItemsZh,
];
const apiNavEn = [
  { text: "API index (mirror)", link: "/en/mirror/api/" },
  ...referenceItemsEn,
];

const siteHubZh = [
  { text: "指南总览", link: "/guide/" },
  { text: "产品功能", link: "/product/features" },
  { text: "定位与路线", link: "/product/" },
  { text: "路线图", link: "/product/roadmap" },
  { text: "契约矩阵", link: "/parity/public-matrix" },
  { text: "模块复现骨架", link: "/meta/inquanto-module-scaffold" },
  { text: "站点地图", link: "/meta/ia-mapping" },
  { text: "模拟器云", link: "/cloud/" },
];
const siteHubEn = [
  { text: "Guides hub", link: "/en/guide/" },
  { text: "Product features", link: "/en/product/features" },
  { text: "Positioning", link: "/en/product/" },
  { text: "Roadmap", link: "/en/product/roadmap" },
  { text: "Parity matrix", link: "/en/parity/public-matrix" },
  { text: "Module scaffold", link: "/en/meta/inquanto-module-scaffold" },
  { text: "Site map", link: "/en/meta/ia-mapping" },
  { text: "Simulator cloud", link: "/en/cloud/" },
];

export default withMermaid(defineConfig({
  title: "qchem-stack",
  /**
   * Light docs chrome — closer to public Quantinuum / InQuanto documentation rhythm.
   * For dark-only again: `appearance: "force-dark"` and tune `custom.css`.
   */
  appearance: "light",
  description:
    "qchem-stack documentation: product features, user interfaces, tutorials, guides, CLI and HTTP API; InQuanto benchmark under positioning (internal).",
  cleanUrls: true,
  srcDir: ".",
  /**
   * This package’s VitePress root is `docs-site/docs/`. Many pages intentionally
   * link to repo root (`docs/`, `src/`, `CONTRIBUTING.md`, …) which is outside
   * `srcDir`. Keep those hrefs correct for clones; exempt them from the checker.
   */
  ignoreDeadLinks: [
    /^https?:\/\//,
    // Three hops `../../../` or `./../../../` → repo root from `docs/parity`, `docs/concept`, …
    /^(?:\.\/)?(?:\.\.\/){3}(?:docs\/|src\/|tests\/|configs\/|\.github\/)/,
    /^(?:\.\/)?(?:\.\.\/){3}CONTRIBUTING(?:\.md)?$/,
    // Four hops from `docs/en/concept`, `docs/guide/**/`, … → `docs/`
    /^(?:\.\/)?(?:\.\.\/){4}docs\//,
  ],

  vite: {
    server: {
      fs: {
        // some node_modules referenced by VitePress live above docs/
        allow: [".."],
      },
    },
  },

  markdown: {
    math: true,
  },

  locales: {
    root: {
      label: "中文",
      lang: "zh-CN",
      title: "qchem-stack 文档",
      description:
        "qchem-stack：产品功能与接口、教程与工作流 YAML、四柱指南与原理阅读；定位与 InQuanto 对标为内部研发页。",
      themeConfig: {
        nav: [
          { text: "首页", link: "/" },
          { text: "介绍", items: introductionNavZh },
          { text: "手册", items: manualMirrorNavZh },
          { text: "教程", items: tutorialsNavZh },
          { text: "API", items: apiNavZh },
          { text: "扩展", link: "/mirror/extensions/" },
          { text: "杂项", link: "/mirror/misc/" },
          { text: "作业 API", link: "/reference/http-api-sqlite-jobs" },
          { text: "路线图", link: "/product/roadmap" },
          { text: "能力总览", link: "/#inq-doc-home" },
          { text: "本站", items: siteHubZh },
        ],
        sidebar: {
          "/product/": [{ text: "产品", items: productItemsZh }],
          "/guide/": [{ text: "指南", items: guideItemsZh }],
          "/tutorial/": [
            {
              text: "教程",
              items: [
                { text: "15 分钟上手", link: "/tutorial/quickstart" },
                { text: "工作流与 YAML 概览", link: "/tutorial/workflow-overview" },
                { text: "HTTP 异步提交运行", link: "/tutorial/async-run-via-http" },
                { text: "repro 键速览", link: "/tutorial/read-repro-keys" },
                { text: "切换 backend 对比", link: "/tutorial/switch-backend-compare" },
                { text: "UCCSD Trotter 与 export", link: "/tutorial/uccsd-trotter-export" },
                { text: "ZNE × Qiskit repro", link: "/tutorial/zne-qiskit-repro" },
                { text: "Projection 嵌入深入", link: "/tutorial/projection-embedding-deep-dive" },
                { text: "案例：H₂ 家族链式改配", link: "/tutorial/case-study-h2-family" },
                { text: "命令行与脚本", link: "/reference/cli-and-scripts" },
              ],
            },
          ],
          "/concept/": [{ text: "Concept", items: conceptItemsZh }],
          "/reference/": [{ text: "Reference", items: referenceItemsZh }],
          "/parity/": [{ text: "Parity", items: parityItemsZh }],
          "/cloud/": [{ text: "模拟器云", items: cloudItemsZh }],
          "/meta/": [{ text: "Meta", items: metaItemsZh }],
          "/design/": [{ text: "Design", items: [{ text: "首页与 Guides 线框", link: "/design/wireframe-home-guides" }] }],
          "/mirror/": (mirrorSidebar as any).zh,
        },
        outline: { level: [2, 3], label: "本页目录" },
        docFooter: { prev: "上一页", next: "下一页" },
        darkModeSwitchLabel: "深色模式",
        sidebarMenuLabel: "菜单",
        returnToTopLabel: "回到顶部",
        lastUpdatedText: "最后更新",
      },
    },
    en: {
      label: "English",
      lang: "en",
      link: "/en/",
      title: "qchem-stack docs",
      description:
        "qchem-stack: product features & interfaces, tutorials and workflow YAML, guides and principles; positioning vs InQuanto is internal engineering.",
      themeConfig: {
        nav: [
          { text: "Home", link: "/en/" },
          { text: "Introduction", items: introductionNavEn },
          { text: "Manual", items: manualMirrorNavEn },
          { text: "Tutorials", items: tutorialsNavEn },
          { text: "API", items: apiNavEn },
          { text: "Extensions", link: "/en/mirror/extensions/" },
          { text: "Misc", link: "/en/mirror/misc/" },
          { text: "Runs API", link: "/en/reference/http-api-sqlite-jobs" },
          { text: "Roadmap", link: "/en/product/roadmap" },
          { text: "Hub", link: "/en/#inq-doc-home" },
          { text: "Site", items: siteHubEn },
        ],
        sidebar: {
          "/en/product/": [{ text: "Product", items: productItemsEn }],
          "/en/guide/": [{ text: "Guides", items: guideItemsEn }],
          "/en/tutorial/": [
            {
              text: "Tutorial",
              items: [
                { text: "15-minute quickstart", link: "/en/tutorial/quickstart" },
                { text: "Workflow & YAML", link: "/en/tutorial/workflow-overview" },
                { text: "Async run via HTTP", link: "/en/tutorial/async-run-via-http" },
                { text: "Ten repro keys", link: "/en/tutorial/read-repro-keys" },
                { text: "Compare backends", link: "/en/tutorial/switch-backend-compare" },
                { text: "UCCSD Trotter + export", link: "/en/tutorial/uccsd-trotter-export" },
                { text: "ZNE × Qiskit repro", link: "/en/tutorial/zne-qiskit-repro" },
                { text: "Projection embedding deep dive", link: "/en/tutorial/projection-embedding-deep-dive" },
                { text: "Case study: H₂ family", link: "/en/tutorial/case-study-h2-family" },
                { text: "CLI & scripts", link: "/en/reference/cli-and-scripts" },
              ],
            },
          ],
          "/en/concept/": [{ text: "Concept", items: conceptItemsEn }],
          "/en/reference/": [{ text: "Reference", items: referenceItemsEn }],
          "/en/parity/": [{ text: "Parity", items: parityItemsEn }],
          "/en/cloud/": [{ text: "Simulator cloud", items: cloudItemsEn }],
          "/en/mirror/": (mirrorSidebar as any).en,
          "/en/meta/": [{ text: "Meta", items: metaItemsEn }],
        },
        outline: { level: [2, 3], label: "On this page" },
        docFooter: { prev: "Previous", next: "Next" },
      },
    },
  },

  themeConfig: {
    logo: "/favicon.svg",
    // Local search scales with page count; optional upgrade: Algolia DocSearch — see docs-site/README.md.
    search: { provider: "local" },
    socialLinks: [],
    /* Full-width mega footer: `theme/components/SiteMegaFooter.vue` via `layout-bottom` (VPFooter only supports message+copyright and is hidden on doc pages with sidebar). */
  },

  // mermaid options forwarded to mermaid.initialize()
  // see https://mermaid.js.org/config/schema-docs/config.html
  mermaid: {
    securityLevel: "loose",
    theme: "neutral",
  },
}));
