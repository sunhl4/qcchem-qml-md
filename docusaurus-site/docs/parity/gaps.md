---
title: Parity gaps snapshot
description: Live capability gaps from the same source as GET /v1/meta/capability-surface.
---

# Parity gaps

Machine-readable gaps are exported by **`GET /v1/meta/capability-surface`** (`gaps` field, schema `capability_surface_v2`).

## Quick links

- Full matrix: [public parity matrix](../../../docs/public_parity_matrix.md) (repo `docs/public_parity_matrix.md`)
- Implementation plan excerpt: [gap implementation plan](./gap-implementation-plan.md)
- L1 playbook: [partial → L1](../../../docs/engineering/partial_to_l1_playbook.md)

## HTTP

```bash
curl -s http://127.0.0.1:8000/v1/meta/parity-gaps | jq '.gaps | length'
curl -sI http://127.0.0.1:8000/v1/meta/capability-surface | grep -i etag
```

The capability surface supports **ETag** caching (`If-None-Match` → 304).
