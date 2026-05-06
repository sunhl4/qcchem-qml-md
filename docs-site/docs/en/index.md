---
layout: home

hero:
  name: qchem-stack
  text: Documentation
  tagline: Open Python stack for quantum-chemistry workflows — YAML-first configs, pluggable backends, strict repro exports, and audit maps aligned with Quantinuum’s published InQuanto documentation tree.
  actions:
    - theme: brand
      text: Quickstart
      link: /en/tutorial/quickstart
    - theme: alt
      text: Product features
      link: /en/product/features
---

<div id="inq-doc-home" class="inq-doc-home">

<div class="inq-doc-home__top">
  <nav class="inq-doc-home__utilities" aria-label="Quick links">
    <a href="/en/reference/http-api-sqlite-jobs">Runs API</a>
    <a href="/en/product/roadmap">Roadmap</a>
  </nav>
</div>

<div class="inq-doc-home__section-head">
  <p class="inq-doc-home__section-eyebrow">Capability pillars</p>
  <p class="inq-doc-home__section-sub">The public InQuanto three-column mental model plus an explicit fourth pillar — jobs &amp; reproducibility. Cards link to guides, reference, and the manual mirror.</p>
</div>

<section class="inq-doc-home__pillars" aria-label="Four pillars">

<article class="inq-doc-home__pillar">
  <header class="inq-doc-home__pillar-head">
    <span class="inq-doc-home__pillar-num" aria-hidden="true">01</span>
    <h2>Chemical Specification</h2>
  </header>
  <p class="inq-doc-home__lead">Start from geometry, basis sets, and chemistry assumptions; build Hamiltonians and embedding / fragment semantics under one validated YAML contract.</p>
  <p class="inq-doc-home__p"><strong>qchem_stack.chem</strong> wraps optional PySCF drivers, Hamiltonian builders, and Schmidt / DMET <em>shapes</em>. The top-level contract is <strong>ExperimentConfig</strong> (Pydantic) with validation and cost guards.</p>
  <p class="inq-doc-home__p">Guides: <a href="/en/guide/chemistry-and-embedding/">P1 Chemistry &amp; embedding</a> · <a href="/en/reference/dmet-parity-snapshot">DMET &amp; parity snapshot</a>; public manual map <a href="/en/mirror/manual/">/en/mirror/manual/</a>.</p>
</article>

<article class="inq-doc-home__pillar">
  <header class="inq-doc-home__pillar-head">
    <span class="inq-doc-home__pillar-num" aria-hidden="true">02</span>
    <h2>Program Construction</h2>
  </header>
  <p class="inq-doc-home__lead">Compile experiments into quantum algorithms, Pauli protocols, and resource rows, wired by orchestration into a logged, exportable pipeline.</p>
  <p class="inq-doc-home__p"><strong>qchem_stack.quantum</strong>, <strong>protocols</strong>, and <strong>orchestration</strong> stay layered: algorithms don’t parse YAML. <strong>run_pipeline_sync</strong> / <strong>run_pipeline_from_config</strong> connect drivers and backends. The <strong>repro</strong> blob follows documented key whitelists (e.g. <code>parity_snapshot</code>, <code>run_summary</code>); production paths avoid silent <code>default=str</code> JSON.</p>
  <p class="inq-doc-home__manual"><a href="/en/mirror/manual/computables/evaluating_w_protocols/">Manual mirror — computables &amp; protocol evaluation</a></p>
  <p class="inq-doc-home__p">More: <a href="/en/guide/algorithms-and-protocols/">P2 Algorithms &amp; protocols</a> · <a href="/en/reference/cli-and-scripts">CLI &amp; scripts</a> · <a href="/en/tutorial/workflow-overview">Workflow &amp; YAML</a>.</p>
</article>

<article class="inq-doc-home__pillar">
  <header class="inq-doc-home__pillar-head">
    <span class="inq-doc-home__pillar-num" aria-hidden="true">03</span>
    <h2>Execution and Analysis</h2>
  </header>
  <p class="inq-doc-home__lead">Run circuits behind a backend abstraction; manage sampling and compilation paths; connect mitigation and resource-style analysis.</p>
  <p class="inq-doc-home__p"><strong>BackendSpec</strong> selects simulators, Qiskit, Aer-shaped executors, and similar backends. Protocol layers emit resource rows and observable summaries for downstream analysis.</p>
  <p class="inq-doc-home__manual"><a href="/en/mirror/manual/noise_mitigation/">Manual mirror — noise mitigation</a></p>
  <p class="inq-doc-home__p">More: <a href="/en/guide/execution-and-analysis/">P3 Execution &amp; analysis</a> · <a href="/en/concept/mitigation-mapping">Mitigation mapping</a>.</p>
</article>

<article class="inq-doc-home__pillar">
  <header class="inq-doc-home__pillar-head">
    <span class="inq-doc-home__pillar-num" aria-hidden="true">04</span>
    <h2>Jobs &amp; Reproducibility</h2>
  </header>
  <p class="inq-doc-home__lead">SQLite job ledgers and an optional Runs API carry async full pipelines; strict repro, timelines, and slim summaries support Methods and gateway integrations.</p>
  <p class="inq-doc-home__p"><strong>run_context</strong>, <strong>pipeline_profile</strong>, and API labels are written into <strong>repro</strong>; <strong>GET /v1/runs/…/summary|repro</strong> contracts and parity key whitelists live in Reference.</p>
  <p class="inq-doc-home__manual"><a href="/en/reference/http-api-sqlite-jobs">Reference — HTTP API &amp; SQLite jobs</a></p>
  <p class="inq-doc-home__p">More: <a href="/en/guide/jobs-and-reproducibility/">P4 Jobs &amp; reproducibility</a> · <a href="/en/concept/launch-retrieve-nexus-analog">Launch / Retrieve (Nexus analog)</a> · <a href="/en/parity/public-matrix">Parity matrix</a>.</p>
</article>

</section>

<div class="inq-doc-home__trust">
  <p class="inq-doc-home__trust-inner">
    <span class="inq-doc-home__trust-label">Trust &amp; limits</span>
    <a href="/en/parity/public-matrix">Parity matrix</a>
    <span class="inq-doc-home__trust-sep" aria-hidden="true">·</span>
    <a href="/en/parity/l1-signoff">L1 sign-off</a>
    <span class="inq-doc-home__trust-sep" aria-hidden="true">·</span>
    <a href="/parity/gap-implementation-plan">Gap plan (ZH)</a>
  </p>
</div>

<footer class="inq-doc-home__footer-links">
  <a href="/en/meta/security-and-data">Security &amp; data</a>
  <span class="inq-doc-home__footer-dot" aria-hidden="true"></span>
  <a href="/en/guide/principles-and-reading">Principles &amp; reading</a>
</footer>

</div>
