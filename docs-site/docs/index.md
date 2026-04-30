---
layout: home

hero:
  name: qchem-stack
  text: 量子化学编排 · 可审计交付
  tagline: "YAML、多后端、strict repro；与公开 InQuanto **295 节点** 可对照。主文档：[指南](/guide/) · [产品与方案](/product/) · [/mirror/](/mirror/) 为结构审计。"
  image:
    src: /favicon.svg
    alt: qchem-stack
  actions:
    - theme: brand
      text: 15 分钟上手
      link: /tutorial/quickstart
    - theme: alt
      text: 四柱指南
      link: /guide/
    - theme: alt
      text: 产品与方案
      link: /product/

features:
  - title: 化学规格与嵌入
    details: 对齐公开 Chemical Specification 柱（驱动、活性空间、嵌入）。
  - title: 程序构造与协议
    details: 对齐 Program Construction 柱（算法、五阶段 Protocol）。
  - title: 执行与可复现
    details: 多后端、作业、HTTP、repro；与 Execution 叙事对照。
---

## 四柱指南

<div class="qcs-hero-pillars">
  <PillarCard id="P1" icon="🧬" title="化学与嵌入" subtitle="PySCF、活性空间、JW；DMET / 投影 / Schmidt。" link="/guide/chemistry-and-embedding/" cta="指南 →" />
  <PillarCard id="P2" icon="⚛️" title="算法与协议" subtitle="VQE / ADAPT / 激发态；Protocol 与 computable。" link="/guide/algorithms-and-protocols/" cta="指南 →" />
  <PillarCard id="P3" icon="📊" title="执行与分析" subtitle="后端、采样、资源与缓解。" link="/guide/execution-and-analysis/" cta="指南 →" />
  <PillarCard id="P4" icon="📦" title="作业与可复现" subtitle="FastAPI、SQLite、repro / parity。" link="/guide/jobs-and-reproducibility/" cta="指南 →" />
</div>

开源编排栈；边界见 [竞争定位](/concept/competitive-positioning)。对照仅 [Quantinuum 公开 InQuanto 文档](https://docs.quantinuum.com/inquanto/)；深度材料在仓库 `docs/`，不进本站树。

| 用途 | 链接 |
|------|------|
| 产品说明 | [指南](/guide/) · [产品与方案](/product/) · [教程](/tutorial/quickstart) |
| 公开站对照 | [/mirror/](/mirror/) · [契约矩阵](/parity/public-matrix) · [云](/cloud/) |

上手：`pip install -e ".[dev]"` → `configs/example_h2.yaml` → `run_pipeline_from_config(...)`（见 [教程](/tutorial/quickstart)）。签核与映射：[契约矩阵](/parity/public-matrix) · [Y1 台账](/parity/y1-alignment-ledger) · [站点地图](/meta/ia-mapping) · [安全与数据](/meta/security-and-data)。
