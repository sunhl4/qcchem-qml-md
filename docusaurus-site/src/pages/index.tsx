import {useCallback, useState, type ReactNode} from 'react';
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
    title: '按角色导航',
    description: '研究者、平台工程师、维护者三条直达路径。',
    to: '/guide/role-based-paths',
  },
  {
    title: 'CLI 与 HTTP',
    description: '命令、脚本、API 的集成入口。',
    to: '/reference/cli-and-scripts',
  },
  {
    title: '架构与路线',
    description: '查看产品架构、能力边界与迭代计划。',
    to: '/product/roadmap',
  },
];

const apiQuickCopy = [
  {
    title: '1) 提交异步任务',
    command: `curl -sS -X POST "http://127.0.0.1:8000/v1/runs" \\
  -H "Content-Type: application/json" \\
  -d "$(python - <<'PY'
import json
from pathlib import Path
payload = {"experiment_yaml": Path("configs/example_h2.yaml").read_text(), "sync": False}
print(json.dumps(payload))
PY
)"`,
  },
  {
    title: '2) 轮询状态',
    command: `RUN_ID="<your_job_id>"
curl -sS "http://127.0.0.1:8000/v1/runs/$RUN_ID/status"`,
  },
  {
    title: '3) 拉取摘要与 repro',
    command: `curl -sS "http://127.0.0.1:8000/v1/runs/$RUN_ID/summary"
curl -sS "http://127.0.0.1:8000/v1/runs/$RUN_ID/repro"`,
  },
];

type SiteDoc = {
  id: string;
  unversionedId?: string;
};

function CopyCommandButton({text}: {text: string}) {
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState(false);

  const onCopy = useCallback(async () => {
    setError(false);
    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        window.setTimeout(() => setCopied(false), 2000);
        return;
      }
    } catch {
      /* fall through */
    }
    try {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.position = 'fixed';
      ta.style.left = '-9999px';
      document.body.appendChild(ta);
      ta.select();
      document.execCommand('copy');
      document.body.removeChild(ta);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 2000);
    } catch {
      setError(true);
      window.setTimeout(() => setError(false), 2500);
    }
  }, [text]);

  return (
    <button
      type="button"
      className={styles.copyButton}
      onClick={onCopy}
      aria-label={copied ? '已复制到剪贴板' : '复制命令到剪贴板'}>
      {error ? '复制失败' : copied ? '已复制' : '复制'}
    </button>
  );
}

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
    {label: '产品与架构页', value: `${getPrefixCount('product') + getPrefixCount('concept')}+`},
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
                按使用路径组织：先上手，再深入架构与接口，再做工程规划。
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
                → 架构与路线。
              </p>
            </div>
            <div className={styles.apiQuickCopyCard}>
              <div className={styles.apiQuickCopyHeader}>
                <Heading as="h3">API Quick Copy</Heading>
                <p>给接入同学的三步最小联调命令。</p>
              </div>
              <div className={styles.apiCommandGrid}>
                {apiQuickCopy.map((item) => (
                  <article key={item.title} className={styles.apiCommandCard}>
                    <div className={styles.apiCommandCardHeader}>
                      <h4>{item.title}</h4>
                      <CopyCommandButton text={item.command} />
                    </div>
                    <pre className={styles.apiCommandPre}>
                      <code>{item.command}</code>
                    </pre>
                  </article>
                ))}
              </div>
              <p className={styles.apiQuickCopyFooter}>
                更多字段与返回示例见{' '}
                <Link to="/reference/http-api-sqlite-jobs">HTTP API 参考页</Link>。
              </p>
            </div>
          </div>
        </section>
        <HomepageFeatures />
      </main>
    </Layout>
  );
}
