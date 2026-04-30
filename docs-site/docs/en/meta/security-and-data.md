---
title: Security & data
description: Default deployment, residency, and explicit non-claims (short)
---

**Short note for procurement / security**: by default the stack runs on **your** infrastructure; molecular inputs, YAML, and the **SQLite job store** stay on disks you control. No default coupling to Quantinuum commercial cloud or Nexus. Bind, TLS, and auth are deployment choices — see [HTTP API](/en/reference/http-api-sqlite-jobs).

The repo and docs **do not** claim SOC 2, ISO 27001, or similar. Technical evidence: [parity matrix](/en/parity/public-matrix) and `repro` / CI — not a substitute for your security review.

Also: [site map](/en/meta/ia-mapping) · [architecture boundaries](/en/concept/architecture-boundaries).
