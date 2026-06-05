# Protocol job blob migration (HMAC-signed pickle)

Tier 1 engineering note for operators upgrading SQLite job stores that contain
pickled :class:`~qchem_stack.protocols.protocol.PauliAveragingProtocol` payloads.

## Environment variables

| Variable | Purpose |
|----------|---------|
| `QCHEM_PROTOCOL_HMAC_KEY` | Required for **new** writes via `secure_dumps` / `PauliAveragingProtocol.dumps()` |
| `QCHEM_ALLOW_LEGACY_PICKLE` | Set to `1` only during one-time migration to load **unsigned** legacy blobs |

See also [说明_API安全与环境变量.md](../说明_API安全与环境变量.md).

## Security boundary

HMAC provides **integrity** checking, not safe deserialization. Treat job SQLite files
and the HMAC key as sensitive. Do not expose the worker API without authentication.

## Migration procedure

1. Set a strong random `QCHEM_PROTOCOL_HMAC_KEY` in the worker environment.
2. Run `python scripts/migrate_job_protocol_blobs.py --db path/to/jobs.sqlite` (dry-run first).
3. Re-enqueue or drain jobs so workers rewrite blobs with HMAC signatures.
4. Unset `QCHEM_ALLOW_LEGACY_PICKLE` after all rows are upgraded.
5. Rotate the HMAC key on a documented schedule (requires re-saving blobs).

## Protocol v2 (JSON)

Workers **default** to HMAC-signed JSON blobs (``QCHEM_PROTOCOL_BLOB_V2`` defaults to ``1``).
Set ``QCHEM_PROTOCOL_BLOB_V2=0`` only to **write** legacy pickle v1
(``protocol_blob_version: 2``). Readers accept v2 JSON or legacy v1 pickle via
``PauliAveragingProtocol.loads()`` / ``secure_loads_protocol``. See
[protocol_serialization_v2_rfc.md](protocol_serialization_v2_rfc.md).

## Related work

Long-term replacement: [protocol_serialization_v2_rfc.md](protocol_serialization_v2_rfc.md).
