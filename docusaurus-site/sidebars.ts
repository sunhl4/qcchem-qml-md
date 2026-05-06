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
      items: ['product/features', 'product/positioning', 'product/roadmap'],
    },
    {
      type: 'category',
      label: '指南',
      items: [
        'guide/overview',
        'guide/chemistry-and-embedding',
        'guide/program-construction',
        'guide/execution-and-analysis',
        'guide/jobs-and-reproducibility',
      ],
    },
    {
      type: 'category',
      label: '教程',
      items: [
        'tutorial/quickstart',
        'tutorial/workflow',
        'tutorial/async-run-via-http',
        'tutorial/read-repro-keys',
        'tutorial/switch-backend-compare',
        'tutorial/uccsd-trotter-export',
        'tutorial/zne-qiskit-repro',
        'tutorial/projection-embedding-deep-dive',
        'tutorial/case-study-h2-family',
      ],
    },
    {
      type: 'category',
      label: '参考',
      items: [
        'reference/cli-http',
        'reference/http-api-sqlite-jobs',
        'reference/circuitir-tket-jobs',
        'reference/qiskit-shot-counts',
        'reference/dmet-parity-snapshot',
      ],
    },
    {
      type: 'category',
      label: '产品战略',
      items: [
        'concept/competitive-positioning',
        'concept/inquanto-ia-architecture-report',
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
      ],
    },
    {
      type: 'category',
      label: '对标',
      items: [
        'parity/competitor-benchmark',
        'parity/public-matrix',
        'parity/gap-implementation-plan',
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
