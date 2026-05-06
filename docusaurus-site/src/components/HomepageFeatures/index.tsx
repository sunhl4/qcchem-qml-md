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
    title: 'Chemical Specification',
    Svg: require('@site/static/img/undraw_docusaurus_mountain.svg').default,
    description: (
      <>
        用统一 YAML 组织分子、基组、活性空间与嵌入参数，先建立可复现的化学问题定义。
      </>
    ),
  },
  {
    title: 'Program Construction',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        在算法、协议和编排层解耦构建程序，支持 VQE 类流程以及可追踪的中间产物输出。
      </>
    ),
  },
  {
    title: 'Execution and Analysis',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        多后端执行、作业队列和 repro 导出能力帮助你把实验从 notebook 推进到工程化流程。
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
          <Heading as="h2">三条能力主轴</Heading>
          <p>对齐行业文档结构，同时覆盖你自己的工程化扩展路径。</p>
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
