import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'P1 化学问题定义',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        先把分子、基组、活性空间和嵌入参数定义清楚，减少后续调试中的语义歧义。
      </>
    ),
  },
  {
    title: 'P2 程序构建与协议',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        把算法、协议和编排拆开，形成可演进、可验证、可追溯的执行计划。
      </>
    ),
  },
  {
    title: 'P3/P4 执行与作业',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        从后端执行到作业状态机，再到 repro 导出，把实验升级为可维护的工程流程。
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--4', styles.featureCol)}>
      <div className={styles.featureIconWrap}>
        <Svg className={styles.featureSvg} role="img" />
      </div>
      <div className={styles.featureBody}>
        <Heading as="h3">{title}</Heading>
        <p>{description}</p>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className={styles.featuresHeader}>
          <Heading as="h2">从能跑到能维护</Heading>
          <p>围绕 P1-P4 构建产品手册，让新用户和维护者都能快速找到下一步动作。</p>
        </div>
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
