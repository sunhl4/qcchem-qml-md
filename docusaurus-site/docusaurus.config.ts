import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'qchem-stack Docs',
  tagline: 'Quantum chemistry workflows for open and reproducible execution',
  favicon: 'img/favicon.svg',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
    // Rspack (@docusaurus/faster) can panic on Windows with React 19 paths; use webpack dev server.
    faster: false,
  },

  // Set the production url of your site here
  url: 'https://example.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'qchem-stack',
  projectName: 'qchem_qml_md',

  onBrokenLinks: 'throw',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: '/',
          editUrl:
            'https://github.com/your-org/qchem_qml_md/tree/main/docusaurus-site/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/social-card-qchem.svg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'qchem-stack',
      logo: {
        alt: 'qchem-stack Logo',
        src: 'img/logo-qchem.svg',
      },
      items: [
        {to: '/getting-started', label: '快速开始', position: 'left'},
        {to: '/product/features', label: '产品能力', position: 'left'},
        {to: '/product/positioning', label: '定位路线', position: 'left'},
        {to: '/guide/overview', label: '指南', position: 'left'},
        {to: '/tutorial/quickstart', label: '教程', position: 'left'},
        {to: '/reference/http-api-sqlite-jobs', label: '参考', position: 'left'},
        {to: '/changelog/', label: '更新日志', position: 'left'},
        {
          type: 'docSidebar',
          sidebarId: 'mainSidebar',
          position: 'left',
          label: '文档目录',
        },
        {
          href: 'https://docs.quantinuum.com/inquanto/',
          label: 'InQuanto 参考',
          position: 'right',
        },
        {
          href: 'https://github.com/facebook/docusaurus',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: '文档',
          items: [
            {
              label: '快速开始',
              to: '/getting-started',
            },
            {label: '产品能力', to: '/product/features'},
            {label: '定位路线', to: '/product/positioning'},
            {label: '教程', to: '/tutorial/quickstart'},
            {label: '更新日志', to: '/changelog/'},
          ],
        },
        {
          title: '产品与架构',
          items: [
            {
              label: '三层架构指南',
              to: '/guide/overview',
            },
            {
              label: '云端与作业',
              to: '/cloud/overview',
            },
            {
              label: '对标与差距',
              to: '/parity/competitor-benchmark',
            },
          ],
        },
        {
          title: '外部链接',
          items: [
            {
              label: 'InQuanto 官方文档',
              href: 'https://docs.quantinuum.com/inquanto/',
            },
            {
              label: 'Docusaurus',
              href: 'https://github.com/facebook/docusaurus',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} qchem-stack. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
