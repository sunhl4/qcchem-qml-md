---
title: Security & data
description: Default deployment, residency, and explicit non-claims (short)
---

**Short note for procurement / security**: by default the stack runs on **your** infrastructure; molecular inputs, YAML, and the **SQLite job store** stay on disks you control. No default coupling to Quantinuum commercial cloud or Nexus. Bind, TLS, and auth are deployment choices — see [HTTP API](/en/reference/http-api-sqlite-jobs).

The repo and docs **do not** claim SOC 2, ISO 27001, or similar. Technical evidence: [parity matrix](/en/product/roadmap) and `repro` / CI — not a substitute for your security review.

Also: [site map](/en/meta/ia-mapping) · [architecture boundaries](/en/concept/architecture-boundaries).

## No auth by default

The optional HTTP job gateway **does not ship** logins, RBAC, or API keys. It assumes **localhost or a trusted network** unless you terminate TLS and enforce identity at a reverse proxy or API gateway. Do not expose the bind address to the public internet without those controls.

## Logs and SQLite on disk

Job rows, timeline JSON, and payloads live in the **SQLite file path** you configure (see the HTTP API / worker docs). Application stdout/stderr follow your process supervisor or container logging. Retention and backup are operator decisions; this site does not prescribe directory names.

## Threat model (one line)

The main risk is **any principal that can reach the HTTP bind address and read/write the job database**; mitigations are network isolation, filesystem permissions, and dependency hygiene — not marketing claims from this documentation site.
