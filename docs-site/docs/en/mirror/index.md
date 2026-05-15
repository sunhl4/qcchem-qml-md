---
title: Public documentation mirror (audit view)
---

# Public documentation mirror (audit view)

<div class="qcs-mirror-audit-banner">

This section mirrors a **third-party public documentation** tree so we can answer “what the public docs describe ↔ what we ship”. It is an **audit appendix**, **not** the qchem-stack product manual — for product narrative and tasks, start from the [pillar guides](/en/guide/).

Every tree node has a page here (with placeholders where not implemented yet), tagged `shipped` / `partial` / `placeholder` / `not-applicable`. The goal is **independent verification** of capability boundaries, not a reproduction of vendor prose.

</div>

## Status legend

| Badge | Meaning |
|---|---|
| <StatusBadge status="shipped" locale="en" /> | Implemented in `qchem_stack` (or an equivalent path). |
| <StatusBadge status="partial" locale="en" /> | Fields/behavior present but may differ from the public reference text. |
| <StatusBadge status="placeholder" locale="en" /> | Node exists in the reference tree; not implemented here yet — route reserved (see milestone). |
| <StatusBadge status="not-applicable" locale="en" /> | Out of scope by design (cloud, billing, proprietary hardware). |

<MirrorTree locale="en" />

> Backed by `docs-site/scripts/mirror-doc-tree.yaml` + `scripts/scaffold-mirror.mjs`. After manifest edits: `npm run scaffold:mirror`.
