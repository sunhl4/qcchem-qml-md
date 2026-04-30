---
title: Public doc map (audit view)
---

# Public doc map (audit view)

This section is **structurally aligned** with Quantinuum’s [public InQuanto documentation tree](https://docs.quantinuum.com/inquanto/) so we can answer “what the public docs describe ↔ what we ship”. It is an **audit appendix**, **not** the qchem-stack product manual — for product narrative and tasks, start from the [pillar guides](/en/guide/).

Every tree node has a page here (with placeholders where not implemented yet), tagged `shipped` / `partial` / `placeholder` / `not-applicable`. The goal is **independent verification** of capability boundaries, not a reproduction of vendor prose.

## Status legend

| Badge | Meaning |
|---|---|
| <StatusBadge status="shipped" locale="en" /> | Equivalent or improved implementation in `qchem_stack`. |
| <StatusBadge status="partial" locale="en" /> | Fields/behavior present but not full semantic match with **public** docs. |
| <StatusBadge status="placeholder" locale="en" /> | Node exists in the public tree; not implemented here yet — route reserved (see milestone). |
| <StatusBadge status="not-applicable" locale="en" /> | Out of scope by design (cloud, billing, proprietary hardware). |

<MirrorTree locale="en" />

> Backed by `docs-site/scripts/inquanto-tree.yaml` + `scripts/scaffold-mirror.mjs`. After manifest edits: `npm run scaffold:mirror`.
