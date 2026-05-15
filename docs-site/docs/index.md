---
layout: home

hero:
  name: qchem-stack
  text: Documentation
  tagline: 面向量子化学工作流的开放 Python 栈：YAML 单一配置、多后端执行、strict repro，以及与公开 InQuanto 文档目录对齐的验收与镜像对照。
  actions:
    - theme: brand
      text: 快速开始
      link: /tutorial/quickstart
    - theme: alt
      text: 产品功能
      link: /product/features
---

<div id="inq-doc-home" class="inq-doc-home">

<div class="inq-doc-home__top">
  <nav class="inq-doc-home__utilities" aria-label="快捷入口">
    <a href="/reference/http-api-sqlite-jobs">Runs API</a>
    <a href="/product/roadmap">路线图</a>
  </nav>
</div>

<div class="inq-doc-home__section-head">
  <p class="inq-doc-home__section-eyebrow inq-doc-home__section-eyebrow--zh">四条能力主轴</p>
  <p class="inq-doc-home__section-sub">在公开 InQuanto 三柱心智上显式增加「作业与可复现」第四维；卡片标题沿用常用英文便于检索，正文链向本站指南、参考与手册镜像。</p>
</div>

<section class="inq-doc-home__pillars" aria-label="Four pillars">

<article class="inq-doc-home__pillar">
  <header class="inq-doc-home__pillar-head">
    <span class="inq-doc-home__pillar-num" aria-hidden="true">01</span>
    <h2>Chemical Specification</h2>
  </header>
  <p class="inq-doc-home__lead">从几何、基组与化学假设出发，在单一 YAML 配置下构造哈密顿量与嵌入 / 片段语义。</p>
  <p class="inq-doc-home__p"><strong>qchem_stack.chem</strong> 提供可选 PySCF 驱动、哈密顿量构建与 Schmidt / DMET <em>形状</em>；顶层契约由 <strong>ExperimentConfig</strong>（Pydantic）校验与成本护栏约束。</p>
  <p class="inq-doc-home__p">用法与边界：<a href="/guide/chemistry-and-embedding/">P1 化学与嵌入</a> · <a href="/reference/dmet-parity-snapshot">DMET 与 parity 契约</a>；公开手册路径对照 <a href="/mirror/manual/">/mirror/manual/</a>。</p>
</article>

<article class="inq-doc-home__pillar">
  <header class="inq-doc-home__pillar-head">
    <span class="inq-doc-home__pillar-num" aria-hidden="true">02</span>
    <h2>Program Construction</h2>
  </header>
  <p class="inq-doc-home__lead">将实验配置编译为量子算法、Pauli 协议与可观测资源行，由编排层串联为一条可日志、可导出的流水线。</p>
  <p class="inq-doc-home__p"><strong>qchem_stack.quantum</strong>、<strong>protocols</strong> 与 <strong>orchestration</strong> 分层：算法与驱动不解析 YAML；<strong>run_pipeline_sync</strong> / <strong>run_pipeline_from_config</strong> 负责接线。<strong>repro</strong> 块遵循开放契约白名单（如 <code>parity_snapshot</code>、<code>run_summary</code>），禁止静默 <code>default=str</code> 写库。</p>
  <p class="inq-doc-home__manual"><a href="/mirror/manual/computables/evaluating_w_protocols/">手册镜像：Computable 与协议评估</a></p>
  <p class="inq-doc-home__p">延伸：<a href="/guide/algorithms-and-protocols/">P2 算法与协议</a> · <a href="/reference/cli-and-scripts">命令行与脚本</a> · <a href="/tutorial/workflow-overview">工作流与 YAML</a>。</p>
</article>

<article class="inq-doc-home__pillar">
  <header class="inq-doc-home__pillar-head">
    <span class="inq-doc-home__pillar-num" aria-hidden="true">03</span>
    <h2>Execution and Analysis</h2>
  </header>
  <p class="inq-doc-home__lead">在后端抽象上执行线路，管理采样与编译路径，并对接缓解与资源估计等分析侧能力。</p>
  <p class="inq-doc-home__p"><strong>BackendSpec</strong> 与执行器抽象切换 statevector、Qiskit、Aer 等形状；协议层产出资源行与可观测摘要，供下游分析与控制台展示。</p>
  <p class="inq-doc-home__manual"><a href="/mirror/manual/noise_mitigation/">手册镜像：噪声缓解</a></p>
  <p class="inq-doc-home__p">延伸：<a href="/guide/execution-and-analysis/">P3 执行与分析</a> · <a href="/concept/mitigation-mapping">缓解映射</a>。</p>
</article>

<article class="inq-doc-home__pillar">
  <header class="inq-doc-home__pillar-head">
    <span class="inq-doc-home__pillar-num" aria-hidden="true">04</span>
    <h2>Jobs &amp; Reproducibility</h2>
  </header>
  <p class="inq-doc-home__lead">以 SQLite 作业台账与可选 Runs API 承载异步全流水线；strict repro、队列时间线与 slim 摘要服务 Methods 与网关集成。</p>
  <p class="inq-doc-home__p"><strong>run_context</strong>、<strong>pipeline_profile</strong> 与 <code>meta</code> 标签写入 repro；<strong>GET /v1/runs/…/summary|repro</strong> 等契约与 parity 白名单见参考文档。</p>
  <p class="inq-doc-home__manual"><a href="/reference/http-api-sqlite-jobs">参考：HTTP API 与 SQLite 作业契约</a></p>
  <p class="inq-doc-home__p">延伸：<a href="/guide/jobs-and-reproducibility/">P4 作业与可复现</a> · <a href="/concept/launch-retrieve-nexus-analog">Launch / Retrieve（Nexus 类比）</a> · <a href="/product/roadmap">公开契约矩阵</a>。</p>
</article>

</section>

<div class="inq-doc-home__trust">
  <p class="inq-doc-home__trust-inner">
    <span class="inq-doc-home__trust-label">信任与边界</span>
    <a href="/product/roadmap">公开契约矩阵</a>
    <span class="inq-doc-home__trust-sep" aria-hidden="true">·</span>
    <a href="/product/roadmap">L1 签 off</a>
    <span class="inq-doc-home__trust-sep" aria-hidden="true">·</span>
    <a href="/product/roadmap">差距与实施计划</a>
  </p>
</div>

<footer class="inq-doc-home__footer-links">
  <a href="/meta/security-and-data">安全与数据</a>
  <span class="inq-doc-home__footer-dot" aria-hidden="true"></span>
  <a href="/guide/principles-and-reading">原理与阅读建议</a>
</footer>

</div>
