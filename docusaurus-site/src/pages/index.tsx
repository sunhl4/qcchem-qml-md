import {useCallback, useState, type ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';

import styles from './index.module.css';

const audiences = [
  {
    title: '研究者',
    description: '从 H₂ 基线到 UCCSD / ADAPT，对照能量与可复现导出。',
    to: '/tutorial/quickstart',
    cta: '跑第一个实验',
  },
  {
    title: '集成方',
    description: '用 Python SDK 或 HTTP 提交作业，读取 parity 与能力面。',
    to: '/reference/python-sdk',
    cta: '接入 SDK',
  },
  {
    title: '平台维护',
    description: '模块契约、作业队列、部署清单与 CI 门禁。',
    to: '/modules/',
    cta: '看部署与契约',
  },
];

const workflowStages = [
  {
    id: 'P1',
    title: 'Chemistry',
    titleZh: '化学与嵌入',
    description: '分子、SCF、活性空间、映射与嵌入。',
    to: '/guide/chemistry-and-embedding',
  },
  {
    id: 'P2',
    title: 'Algorithm',
    titleZh: '算法与协议',
    description: '变分 ansatz、算符池、Pauli 与激发态。',
    to: '/guide/program-construction',
  },
  {
    id: 'P3',
    title: 'Backend',
    titleZh: '执行与分析',
    description: '多后端、误差缓解与资源估计。',
    to: '/guide/execution-and-analysis',
  },
  {
    id: 'P4',
    title: 'Jobs & Repro',
    titleZh: '作业与可复现',
    description: '作业队列、HTTP API 与 repro 契约。',
    to: '/guide/jobs-and-reproducibility',
  },
];

function CopyCommandButton({text, label = '复制安装命令'}: {text: string; label?: string}) {
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
      aria-label={copied ? '已复制到剪贴板' : label}>
      {error ? '失败' : copied ? '已复制' : '复制'}
    </button>
  );
}

function HeroDemo() {
  const [tab, setTab] = useState<'cli' | 'python'>('cli');
  const cliCmd = 'qchem-run --scenario minimal_vqe';

  return (
    <div className={styles.heroVisual}>
      <div className={styles.heroDemo}>
        <div className={styles.heroTabs} role="tablist" aria-label="最小运行示例">
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'cli'}
            className={clsx(styles.heroTab, tab === 'cli' && styles.heroTabActive)}
            onClick={() => setTab('cli')}>
            CLI
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === 'python'}
            className={clsx(styles.heroTab, tab === 'python' && styles.heroTabActive)}
            onClick={() => setTab('python')}>
            Python
          </button>
        </div>
        {tab === 'cli' ? (
          <>
            <div className={styles.heroCodeRow}>
              <pre className={styles.heroCode}>
                <code>{cliCmd}</code>
              </pre>
              <CopyCommandButton text={cliCmd} label="复制命令" />
            </div>
            <pre className={styles.heroOutput}>
              <code>{`# 典型 H₂ / sto-3g 量级（示意）
energy_after_variational ≈ -1.137 Ha
repro.run_summary … exported`}</code>
            </pre>
          </>
        ) : (
          <>
            <pre className={styles.heroCode}>
              <code>{`from qchem_stack.sdk import (
    run_pipeline_from_config,
    repro_json_dumps,
)

out = run_pipeline_from_config(
    "configs/example_h2.yaml",
)
print(repro_json_dumps(out["repro"]))`}</code>
            </pre>
            <pre className={styles.heroOutput}>
              <code>{`# energy_after_variational ≈ -1.137…
# repro 可审计导出`}</code>
            </pre>
          </>
        )}
      </div>
    </div>
  );
}

function HomepageHeader() {
  return (
    <header className={clsx(styles.heroBanner)}>
      <div className="container">
        <div className={styles.heroContent}>
          <div className={styles.heroCopy}>
            <Heading as="h1" className={styles.heroTitle}>
              量子计算化学
            </Heading>
            <p className={styles.heroSubtitle}>
              面向科学计算：用 YAML 定义分子与算法，在多后端上跑量子化学计算，导出可审计的{' '}
              <code className={styles.inlineCode}>repro</code>
              。分钟级跑通 H₂ VQE。
            </p>
            <div className={styles.buttons}>
              <Link className="button button--primary button--lg" to="/tutorial/quickstart">
                开始上手
              </Link>
              <Link className="button button--outline button--lg" to="/getting-started">
                安装
              </Link>
            </div>
          </div>
          <HeroDemo />
        </div>
        <ul className={styles.trustBar}>
          <li>
            <code>pip install</code>
          </li>
          <li>Apache-2.0</li>
          <li>科学计算管线 Stable</li>
          <li>
            <Link to="/product/capability-sla">能力 SLA</Link>
          </li>
          <li>
            <a href="https://pypi.org/project/qchem-stack/" target="_blank" rel="noreferrer">
              PyPI
            </a>
          </li>
        </ul>
      </div>
    </header>
  );
}

export default function Home(): ReactNode {
  const installCmd = 'pip install "qchem-stack[chem,quantum]"';
  const smokeCmd = 'qchem-run --scenario minimal_vqe';

  return (
    <Layout
      title="量子计算化学"
      description="面向科学计算的量子计算化学：YAML 管线、多后端执行与可复现导出">
      <HomepageHeader />
      <main>
        <section className={styles.pathSection}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <Heading as="h2" className={styles.sectionTitle}>
                按角色开始
              </Heading>
              <p className={styles.sectionSubtitle}>选一条路径即可；其余文档按需展开。</p>
            </div>
            <ul className={styles.audienceList}>
              {audiences.map((item) => (
                <li key={item.title} className={styles.audienceRow}>
                  <div className={styles.audienceCopy}>
                    <h3>{item.title}</h3>
                    <p>{item.description}</p>
                  </div>
                  <Link className={styles.audienceLink} to={item.to}>
                    {item.cta}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </section>

        <section className={styles.capabilitySection}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <Heading as="h2" className={styles.sectionTitle}>
                工作流阶段
              </Heading>
              <p className={styles.sectionSubtitle}>
                Chemistry → Algorithm → Backend → Jobs & Repro。核心管线 Stable；局部能力见{' '}
                <Link to="/product/capability-sla">能力 SLA</Link>。
              </p>
            </div>
            <div className={styles.capabilityGrid}>
              {workflowStages.map((item) => (
                <Link key={item.id} className={styles.capabilityItem} to={item.to}>
                  <span className={styles.capabilityId}>{item.id}</span>
                  <span className={styles.capabilityTitle}>{item.titleZh}</span>
                  <span className={styles.capabilityStage}>{item.title}</span>
                  <span className={styles.capabilityDesc}>{item.description}</span>
                </Link>
              ))}
            </div>
          </div>
        </section>

        <section className={styles.proofSection}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <Heading as="h2" className={styles.sectionTitle}>
                最小可验证
              </Heading>
              <p className={styles.sectionSubtitle}>
                安装后一条命令即可对照能量量级；配置是否有教程见矩阵。
              </p>
            </div>
            <div className={styles.proofBlock}>
              <div className={styles.proofMain}>
                <code className={styles.proofCmd}>{smokeCmd}</code>
                <CopyCommandButton text={smokeCmd} label="复制烟测命令" />
              </div>
              <p className={styles.proofMeta}>
                期望量级：H₂ / sto-3g 变分能量约 <strong>−1.137 Ha</strong>
                （具体值随配置变化）。教程覆盖见{' '}
                <Link to="/reference/tutorial-config-matrix">配置↔教程矩阵</Link>
                ，完整上手见 <Link to="/tutorial/quickstart">15 分钟上手</Link>。
              </p>
            </div>
          </div>
        </section>

        <section className={styles.installSection}>
          <div className="container">
            <div className={styles.installBar}>
              <code>{installCmd}</code>
              <CopyCommandButton text={installCmd} />
            </div>
            <p className={styles.installHint}>
              开发环境见 <Link to="/getting-started">开始使用</Link>
              ；档位说明见 <Link to="/reference/install-profiles">安装档位</Link>。
            </p>
          </div>
        </section>
      </main>
    </Layout>
  );
}
