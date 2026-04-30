---
layout: home
hero:
  name: qchem-stack
  text: QC orchestration · audit-ready delivery
  tagline: "YAML, pluggable backends, strict repro; **295-node** map vs published InQuanto. Main docs: [Guides](/en/guide/) · [Product](/en/product/) · [/mirror/](/en/mirror/) for structural audit."
  image:
    src: /favicon.svg
    alt: qchem-stack
  actions:
    - theme: brand
      text: 15-minute quickstart
      link: /en/tutorial/quickstart
    - theme: alt
      text: Pillar guides
      link: /en/guide/
    - theme: alt
      text: Product
      link: /en/product/

features:
  - title: Specification & embedding
    details: Public Chemical Specification pillar (drivers, active space, embedding).
  - title: Program construction
    details: Public Program Construction pillar (algorithms, five-stage protocol).
  - title: Execution & reproducibility
    details: Backends, jobs, HTTP, repro — aligned to public execution narrative.
---

## Pillar guides

<div class="qcs-hero-pillars">
  <PillarCard id="P1" icon="🧬" title="Chemistry & embedding" subtitle="PySCF, active space, JW; DMET / projection / Schmidt." link="/en/guide/chemistry-and-embedding/" cta="Guide →" />
  <PillarCard id="P2" icon="⚛️" title="Algorithms & protocols" subtitle="VQE / ADAPT / excited states; Protocol & computable." link="/en/guide/algorithms-and-protocols/" cta="Guide →" />
  <PillarCard id="P3" icon="📊" title="Execution & analysis" subtitle="Backends, sampling, resources, mitigation." link="/en/guide/execution-and-analysis/" cta="Guide →" />
  <PillarCard id="P4" icon="📦" title="Jobs & reproducibility" subtitle="FastAPI, SQLite, repro / parity." link="/en/guide/jobs-and-reproducibility/" cta="Guide →" />
</div>

Open orchestration stack; boundaries in [competitive positioning](/en/concept/competitive-positioning). Comparisons cite [Quantinuum’s published InQuanto docs](https://docs.quantinuum.com/inquanto/) only; deeper material stays in repo `docs/`, not duplicated here.

| Goal | Links |
|------|-------|
| How it works | [/en/guide/](/en/guide/) · [/en/product/](/en/product/) · [Quickstart](/en/tutorial/quickstart) |
| Gap vs public site | [/en/mirror/](/en/mirror/) · [Parity matrix](/en/parity/public-matrix) · [Cloud](/en/cloud/) |

Quickstart: `pip install -e ".[dev]"` → `configs/example_h2.yaml` → `run_pipeline_from_config(...)` ([tutorial](/en/tutorial/quickstart)). Trust: [parity matrix](/en/parity/public-matrix) · [Y1 ledger](/en/parity/y1-alignment-ledger) · [Site map](/en/meta/ia-mapping) · [Security & data](/en/meta/security-and-data).
