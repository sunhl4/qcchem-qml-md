import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */
const sidebars: SidebarsConfig = {
  mainSidebar: [
    'getting-started',
    {
      type: 'category',
      label: '产品',
      items: ['product/features', 'product/roadmap', 'product/positioning', 'product/non-goals'],
    },
    {
      type: 'category',
      label: '指南',
      items: [
        'guide/index',
        'guide/role-based-paths',
        'guide/onboarding-three-paths',
        'guide/overview',
        'guide/chemistry-and-embedding',
        'guide/avas-casscf-workflow',
        'guide/backend-adapter-quickstart',
        'guide/program-construction',
        'guide/execution-and-analysis',
        'guide/jobs-and-reproducibility',
        'guide/principles-and-reading',
        'guide/psi4-backend',
      ],
    },
    {
      type: 'category',
      label: '教程',
      items: [
        'tutorial/index',
        'tutorial/quickstart',
        'tutorial/workflow',
        'tutorial/async-run-via-http',
        'tutorial/read-repro-keys',
        'tutorial/switch-backend-compare',
        'tutorial/uccsd-trotter-export',
        'tutorial/zne-qiskit-repro',
        'tutorial/projection-embedding-deep-dive',
        'tutorial/case-study-h2-family',
        'tutorial/md-ml-active-learning',
      ],
    },
    {
      type: 'category',
      label: '参考',
      items: [
        'reference/cli-and-scripts',
        'reference/http-api-sqlite-jobs',
        'reference/circuitir-tket-jobs',
        'reference/qiskit-shot-counts',
        'reference/dmet-parity-snapshot',
        'reference/parity-contract-import-paths',
        'reference/configs-catalog',
        'parity/gap-implementation-plan',
        'parity/gaps',
        'parity/public-matrix',
        'reference/cli-http',
      ],
    },
    {
      type: 'category',
      label: '概念与架构',
      items: [
        'concept/engineering-architecture',
      ],
    },
    {
      type: 'category',
      label: '云与运维',
      items: [
        'cloud/overview',
        'cloud/tenant-and-quotas',
        'cloud/backend-registry',
        'cloud/jobs-and-logs',
        'cloud/uqc-backend',
      ],
    },
    {
      type: 'category',
      label: '发布',
      items: ['changelog/index', 'release/deployment-checklist'],
    },
  ],
};

export default sidebars;
