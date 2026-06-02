# RFC: Protocol serialization v2 (non-pickle job blobs)

**Status:** implemented (MVP read/write behind ``QCHEM_PROTOCOL_BLOB_V2=1``)  
**Target:** qchem-stack 0.7+

## Problem

SQLite `pauli_protocol` jobs store HMAC-signed **pickle** blobs. Pickle is convenient
for in-process `PauliAveragingProtocol` graphs but is a poor long-term interchange format
(cross-version fragility, security sensitivity).

## Goals

1. Persist a versioned **JSON** (or msgpack) document: `protocol_blob_version: 2`.
2. Include stable references: `hamiltonian_fingerprint`, measurement plan summary,
   variational angles (or job-relative path), backend spec snapshot.
3. Worker reconstructs `PauliAveragingProtocol` in-process without unpickling user code.

## Non-goals (v2.0)

- Cross-language deserialization of full protocol objects.
- Binary parity with historical unsigned pickle rows (use [protocol_pickle_migration.md](protocol_pickle_migration.md)).

## Schema sketch

```json
{
  "protocol_blob_version": 2,
  "experiment_id": "...",
  "hamiltonian_fingerprint": "...",
  "pauli_groups_digest": "...",
  "angles": [...],
  "backend_spec": { "provider": "statevector", "shots_per_circuit": 1000 },
  "mitigation": { "zne_enabled": false }
}
```

## Migration

| `protocol_blob_version` | Reader behavior |
|-------------------------|-----------------|
| 1 (pickle + HMAC) | `secure_loads_protocol` (current) |
| 2 (JSON) | `protocol_from_v2_document` builder |

Dual-read in `jobs/worker_dispatch` for one release cycle; write v2 only when
`QCHEM_PROTOCOL_BLOB_V2=1`.

## Acceptance

- [x] RFC reviewed by maintainers
- [x] Row in `docs/public_parity_matrix.md` under job-store / reproducibility
- [x] CI round-trip test: `tests/jobs/test_protocol_blob_v2_roundtrip.py`
