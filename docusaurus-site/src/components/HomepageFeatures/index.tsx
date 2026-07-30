import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';

type LayerItem = {
  title: string;
  description: ReactNode;
  to: string;
};

const layers: LayerItem[] = [
  {
    title: '模块手册',
    description: <>按源码包：理论、调用、参数与可运行示例。</>,
    to: '/modules/',
  },
  {
    title: '选型指南',
    description: <>P1–P4：何时用什么映射、算法、后端与契约。</>,
    to: '/guide/',
  },
  {
    title: '教程与示例',
    description: <>可运行步骤与 YAML 索引（验证命令 / 期望输出）。</>,
    to: '/tutorial/',
  },
  {
    title: '参考与 FAQ',
    description: (
      <>
        <Link to="/reference/api-surface">API 面</Link>、HTTP、配置字段、
        <Link to="/faq/">FAQ</Link>。
      </>
    ),
    to: '/reference/python-sdk',
  },
];

function Layer({title, description, to}: LayerItem) {
  return (
    <div className={clsx('col col--3', styles.featureCol)}>
      <Link className={styles.featureBody} to={to}>
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </Link>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.featuresHeader}>
          <Heading as="h2">文档分层</Heading>
          <p>
            模块讲「怎么用包」；选型讲「选什么」；教程讲「跟着做」；参考讲「字段与契约」。
          </p>
        </div>
        <div className="row">
          {layers.map((props) => (
            <Layer key={props.title} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
