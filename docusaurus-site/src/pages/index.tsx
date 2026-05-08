import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import {useAllDocsData} from '@docusaurus/plugin-content-docs/client';
import HomepageFeatures from '@site/src/components/HomepageFeatures';
import Heading from '@theme/Heading';

import styles from './index.module.css';

const quickCards = [
  {
    title: '产品能力',
    description: '先建立能力全景，再决定阅读路径。',
    to: '/product/features',
  },
  {
    title: '新手路径',
    description: '按角色选择上手路径，减少信息噪音。',
    to: '/guide/onboarding-three-paths',
  },
  {
    title: 'CLI 与 HTTP',
    description: '命令、脚本、API 的集成入口。',
    to: '/reference/cli-and-scripts',
  },
  {
    title: '对标与路线',
    description: '查看 InQuanto 对标框架与收敛计划。',
    to: '/parity/public-matrix',
  },
];

type SiteDoc = {
  id: string;
  unversionedId?: string;
};

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <div className={styles.heroContent}>
          <div className={styles.heroCopy}>
            <div className={styles.badges}>
              <span>Open workflow</span>
              <span>Multi-backend</span>
              <span>Reproducible outputs</span>
            </div>
            <p className={styles.eyebrow}>Quantum Chemistry Documentation</p>
            <Heading as="h1" className={clsx('hero__title', styles.heroTitle)}>
              {siteConfig.title}
            </Heading>
            <p className={clsx('hero__subtitle', styles.heroSubtitle)}>
              {siteConfig.tagline}
            </p>
            <div className={styles.buttons}>
              <Link
                className="button button--secondary button--lg"
                to="/getting-started">
                开始搭建工作流
              </Link>
              <Link className="button button--outline button--lg" to="/product/features">
                查看产品能力
              </Link>
            </div>
          </div>
          <div className={styles.heroVisual} aria-hidden="true">
            <div className={styles.orbit}>
              <span className={styles.orbitDotA}></span>
              <span className={styles.orbitDotB}></span>
              <span className={styles.orbitDotC}></span>
            </div>
            <div className={styles.visualCard}>
              <span>workflow.yaml</span>
              <strong>chem → program → execute</strong>
              <small>repro.json + run_summary</small>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  const docsData = useAllDocsData() as Record<
    string,
    {versions?: Array<{docs?: SiteDoc[]}>}
  >;
  const allDocs = docsData.default?.versions?.[0]?.docs ?? [];
  const getPrefixCount = (prefix: string) =>
    allDocs.filter((doc) => (doc.unversionedId ?? doc.id).startsWith(`${prefix}/`))
      .length;
  const moduleCount = new Set(
    allDocs.map((doc) => (doc.unversionedId ?? doc.id).split('/')[0]),
  ).size;
  const metrics = [
    {label: '文档模块', value: `${moduleCount || 0}+`},
    {label: '教程专题', value: `${getPrefixCount('tutorial')}+`},
    {label: '参考页面', value: `${getPrefixCount('reference')}+`},
    {label: '对标与路线', value: `${getPrefixCount('parity')}+`},
  ];
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="qchem_qml_md documentation built with Docusaurus">
      <HomepageHeader />
      <main>
        <section className={styles.quickStartSection}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <span className={styles.sectionKicker}>Start here</span>
              <Heading as="h2" className={styles.sectionTitle}>
                快速入口
              </Heading>
              <p className={styles.sectionSubtitle}>
                按使用路径组织：先上手，再深入架构与接口，最后做对标与规划。
              </p>
            </div>
            <div className={styles.quickGrid}>
              {quickCards.map((item) => (
                <Link key={item.title} className={styles.quickCard} to={item.to}>
                  <h3>{item.title}</h3>
                  <p>{item.description}</p>
                </Link>
              ))}
            </div>
            <div className={styles.metricsGrid}>
              {metrics.map((item) => (
                <article key={item.label} className={styles.metricCard}>
                  <p className={styles.metricValue}>{item.value}</p>
                  <p className={styles.metricLabel}>{item.label}</p>
                </article>
              ))}
            </div>
            <div className={styles.pathwayCard}>
              <Heading as="h3">推荐阅读路径</Heading>
              <p>
                产品能力 → 新手路径 → 四柱指南（P1/P2/P3/P4）→ CLI/HTTP
                → 对标与路线。
              </p>
            </div>
          </div>
        </section>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
