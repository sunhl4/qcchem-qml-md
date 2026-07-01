-- qchem-stack job ledger (Postgres reference schema; mirrors SQLite jobs table).
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    payload BYTEA,
    status TEXT NOT NULL,
    result TEXT,
    created DOUBLE PRECISION,
    updated DOUBLE PRECISION,
    retry_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    protocol_hash TEXT,
    job_kind TEXT NOT NULL DEFAULT 'pauli_protocol',
    meta TEXT,
    timeline_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_jobs_status_created ON jobs (status, created ASC);
CREATE INDEX IF NOT EXISTS idx_jobs_job_kind_created ON jobs (job_kind, created DESC);
