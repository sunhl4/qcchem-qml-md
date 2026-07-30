import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: '量子计算化学',
  tagline: '面向科学计算：YAML 管线、多后端执行与可复现导出',
  favicon: 'img/favicon.svg',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
    // Rspack (@docusaurus/faster) can panic on Windows with React 19 paths; use webpack dev server.
    faster: false,
  },

  // Set the production url of your site here
  url: 'https://sunhl4.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/qcchem-qml-md/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'sunhl4',
  projectName: 'qcchem-qml-md',

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'throw',
    },
  },

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
            'https://github.com/sunhl4/qcchem-qml-md/tree/main/docusaurus-site/',
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
        },
        blog: false, // residual blog/ directory removed; do not re-enable without content
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themes: [
    [
      require.resolve('@easyops-cn/docusaurus-search-local'),
      {
        hashed: true,
        language: ['en', 'zh'],
        indexDocs: true,
        docsRouteBasePath: '/',
        highlightSearchTermsOnTargetPage: true,
        explicitSearchResultPath: true,
        searchBarShortcutHint: true,
      },
    ],
  ],

  themeConfig: {
    image: 'img/social-card-qchem.svg',
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: '量子计算化学',
      logo: {
        alt: '量子计算化学',
        src: 'img/logo-qchem.svg',
      },
      items: [
        {to: '/getting-started', label: '开始', position: 'left'},
        {to: '/guide/', label: '选型', position: 'left'},
        {to: '/modules/', label: '模块', position: 'left'},
        {to: '/tutorial/', label: '教程', position: 'left'},
        {to: '/examples/', label: '示例', position: 'left'},
        {
          type: 'dropdown',
          label: '参考',
          position: 'left',
          items: [
            {to: '/reference/python-sdk', label: 'Python SDK'},
            {to: '/reference/api-generated', label: 'API 参考'},
            {to: '/reference/http-api-sqlite-jobs', label: 'HTTP API'},
            {to: '/reference/config-fields/', label: '配置字段'},
            {to: '/faq/', label: 'FAQ'},
            {to: '/reference/configs-catalog', label: '配置目录'},
          ],
        },
        {
          type: 'search',
          position: 'right',
        },
        {
          to: '/tutorial/quickstart',
          label: '开始上手',
          position: 'right',
          className: 'navbar-cta',
        },
        {
          href: 'https://pypi.org/project/qchem-stack/',
          label: 'PyPI',
          position: 'right',
        },
        {
          href: 'https://github.com/sunhl4/qcchem-qml-md',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: '产品',
          items: [
            {label: '开始使用', to: '/getting-started'},
            {label: '15 分钟上手', to: '/tutorial/quickstart'},
            {label: '能力 SLA', to: '/product/capability-sla'},
            {label: 'FAQ', to: '/faq/'},
          ],
        },
        {
          title: '文档',
          items: [
            {label: '选型手册', to: '/guide/'},
            {label: '模块手册', to: '/modules/'},
            {label: 'Python SDK', to: '/reference/python-sdk'},
            {label: '配置字段', to: '/reference/config-fields/'},
          ],
        },
        {
          title: '项目',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/sunhl4/qcchem-qml-md',
            },
            {
              label: 'PyPI',
              href: 'https://pypi.org/project/qchem-stack/',
            },
            {label: 'Changelog', to: '/changelog/'},
          ],
        },
      ],
      copyright: `© ${new Date().getFullYear()} qchem-stack · Apache-2.0`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
