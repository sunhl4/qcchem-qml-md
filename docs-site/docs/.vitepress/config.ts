import { defineConfig } from "vitepress";
import { withMermaid } from "vitepress-plugin-mermaid";
import mirrorSidebar from "./sidebar-mirror.json" with { type: "json" };

const conceptItemsZh = [
  { text: "工程分层架构", link: "/concept/engineering-architecture" },
  { text: "竞争定位与路线图", link: "/concept/competitive-positioning" },
  { text: "架构边界（闭源对照）", link: "/concept/architecture-boundaries" },
  { text: "工程记忆（Quantinuum 对标）", link: "/concept/engineering-memory-quantinuum" },
  { text: "Launch / Retrieve（Nexus 类比）", link: "/concept/launch-retrieve-nexus-analog" },
  { text: "缓解映射（PMSV / ZNE / Qermit）", link: "/concept/mitigation-mapping" },
  { text: "HTTP API 维护记忆", link: "/concept/http-api-worker-memory" },
];

const referenceItemsZh = [
  { text: "HTTP API · SQLite 作业", link: "/reference/http-api-sqlite-jobs" },
  { text: "CircuitIR · TKET · 作业契约", link: "/reference/circuitir-tket-jobs" },
  { text: "Qiskit 比特串采样", link: "/reference/qiskit-shot-counts" },
  { text: "DMET · parity_snapshot", link: "/reference/dmet-parity-snapshot" },
];

const parityItemsZh = [
  { text: "公开契约矩阵", link: "/parity/public-matrix" },
  { text: "差距与实施计划", link: "/parity/gap-implementation-plan" },
  { text: "L1 签 off", link: "/parity/l1-signoff" },
  { text: "Y1 对标台账", link: "/parity/y1-alignment-ledger" },
  { text: "Y1 残余 SLA 模板", link: "/parity/y1-residual-sla-template" },
  { text: "L3 基准路线图", link: "/parity/l3-benchmark-roadmap" },
  { text: "开放栈记忆", link: "/parity/open-stack-memory" },
  { text: "迭代说明", link: "/parity/backlog-to-schedule" },
];

const guideItemsZh = [
  { text: "总览", link: "/guide/" },
  { text: "P1 化学与嵌入", link: "/guide/chemistry-and-embedding/" },
  { text: "P2 算法与协议", link: "/guide/algorithms-and-protocols/" },
  { text: "P3 执行与分析", link: "/guide/execution-and-analysis/" },
  { text: "P4 作业与可复现", link: "/guide/jobs-and-reproducibility/" },
];

const guideItemsEn = [
  { text: "Overview", link: "/en/guide/" },
  { text: "P1 Chemistry & embedding", link: "/en/guide/chemistry-and-embedding/" },
  { text: "P2 Algorithms & protocols", link: "/en/guide/algorithms-and-protocols/" },
  { text: "P3 Execution & analysis", link: "/en/guide/execution-and-analysis/" },
  { text: "P4 Jobs & reproducibility", link: "/en/guide/jobs-and-reproducibility/" },
];

const productItemsZh = [
  { text: "概述", link: "/product/" },
  { text: "路线图", link: "/product/roadmap" },
];
const productItemsEn = [
  { text: "Overview", link: "/en/product/" },
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
  { text: "安全与数据", link: "/meta/security-and-data" },
];

const metaItemsEn = [
  { text: "Site map", link: "/en/meta/ia-mapping" },
  { text: "Security & data", link: "/en/meta/security-and-data" },
];

export default withMermaid(defineConfig({
  title: "qchem-stack",
  /**
   * Always dark — avoids useDark + localStorage fighting SSR/initial paint (rapid light/dark "频闪").
   * To allow a light toggle again, use `appearance: "dark"` (may need clearing `vitepress-theme-appearance` in localStorage if you saw flicker).
   */
  appearance: "force-dark",
  description:
    "Open quantum-chemistry orchestration for audit-ready delivery: YAML contracts, pluggable backends, machine-readable parity, and a 295-node map against Quantinuum’s published InQuanto docs for Methods and diligence.",
  cleanUrls: true,
  ignoreDeadLinks: [
    /^\/en\/(?!mirror)/, // EN side is partial scaffolding; allow links to non-mirror EN pages
  ],
  srcDir: ".",

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
        "开放量子化学编排：YAML 契约、多后端、机读 parity；与公开 InQuanto 295 节点结构对照，便于 Methods 与尽调落档。",
      themeConfig: {
        nav: [
          { text: "首页", link: "/" },
          { text: "产品与方案", link: "/product/" },
          { text: "指南", items: guideItemsZh },
          { text: "教程", link: "/tutorial/quickstart" },
          {
            text: "Concept", items: conceptItemsZh,
          },
          {
            text: "Reference", items: referenceItemsZh,
          },
          {
            text: "Parity", items: parityItemsZh,
          },
          { text: "模拟器云", link: "/cloud/" },
          { text: "公开文档对照", link: "/mirror/" },
          { text: "Meta", items: metaItemsZh },
        ],
        sidebar: {
          "/product/": [{ text: "产品与方案", items: productItemsZh }],
          "/guide/": [{ text: "指南", items: guideItemsZh }],
          "/tutorial/": [{ text: "Tutorial", items: [{ text: "15 分钟上手", link: "/tutorial/quickstart" }] }],
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
        editLink: {
          pattern: "https://github.com/your-org/qchem-stack/edit/main/docs-site/docs/:path",
          text: "在 GitHub 编辑此页",
        },
      },
    },
    en: {
      label: "English",
      lang: "en",
      link: "/en/",
      title: "qchem-stack docs",
      description:
        "Open quantum-chemistry orchestration for audit-ready delivery: YAML contracts, pluggable backends, machine-readable parity, 295-node map vs Quantinuum’s published InQuanto docs.",
      themeConfig: {
        nav: [
          { text: "Home", link: "/en/" },
          { text: "Product", link: "/en/product/" },
          { text: "Guides", items: guideItemsEn },
          { text: "Tutorial", link: "/en/tutorial/quickstart" },
          { text: "Concept", link: "/en/concept/engineering-architecture" },
          { text: "Reference", link: "/en/reference/http-api-sqlite-jobs" },
          { text: "Parity", link: "/en/parity/public-matrix" },
          { text: "Simulator cloud", link: "/en/cloud/" },
          { text: "Public doc map", link: "/en/mirror/" },
          { text: "Meta", items: metaItemsEn },
        ],
        sidebar: {
          "/en/product/": [{ text: "Product", items: productItemsEn }],
          "/en/guide/": [{ text: "Guides", items: guideItemsEn }],
          "/en/cloud/": [{ text: "Simulator cloud", items: cloudItemsEn }],
          "/en/mirror/": (mirrorSidebar as any).en,
          "/en/meta/": [{ text: "Meta", items: metaItemsEn }],
        },
        outline: { level: [2, 3], label: "On this page" },
        docFooter: { prev: "Previous", next: "Next" },
        editLink: {
          pattern: "https://github.com/your-org/qchem-stack/edit/main/docs-site/docs/:path",
          text: "Edit this page on GitHub",
        },
      },
    },
  },

  themeConfig: {
    logo: "/favicon.svg",
    search: { provider: "local" },
    socialLinks: [],
    footer: {
      message:
        "qchem-stack — open product documentation. Claims tied to public docs cite Quantinuum’s published InQuanto site only; verifiable parity artifacts live in-repo.",
      copyright: "Documentation © qchem-stack contributors",
    },
  },

  // mermaid options forwarded to mermaid.initialize()
  // see https://mermaid.js.org/config/schema-docs/config.html
  mermaid: {
    securityLevel: "loose",
    theme: "neutral",
  },
}));
