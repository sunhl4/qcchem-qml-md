"""SQLite-backed store for validated quantum experiment records."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator
from uuid import UUID

from quantum_experiment_record import PathType, ProblemDomain, QuantumExperimentRecord

_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS quantum_experiment_records (
    id TEXT PRIMARY KEY,
    timestamp TEXT NOT NULL,
    path_type TEXT NOT NULL,
    domain TEXT NOT NULL,
    backend TEXT NOT NULL,
    repro_hash TEXT NOT NULL,
    n_qubits INTEGER,
    n_shots INTEGER,
    measurement_protocol TEXT,
    payload_json TEXT NOT NULL,
    ingested_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_qer_path_type ON quantum_experiment_records(path_type);
CREATE INDEX IF NOT EXISTS idx_qer_domain ON quantum_experiment_records(domain);
CREATE INDEX IF NOT EXISTS idx_qer_backend ON quantum_experiment_records(backend);
CREATE INDEX IF NOT EXISTS idx_qer_repro_hash ON quantum_experiment_records(repro_hash);
CREATE INDEX IF NOT EXISTS idx_qer_timestamp ON quantum_experiment_records(timestamp);
"""


class SqliteQuantumDataStore:
    """Persist :class:`QuantumExperimentRecord` rows with queryable metadata."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(_SCHEMA_SQL)

    def ingest(self, record: QuantumExperimentRecord) -> None:
        """Insert or replace a validated record."""
        payload = record.model_dump(mode="json")
        m = record.quantum_execution.measurement
        row = {
            "id": str(record.id),
            "timestamp": record.timestamp.isoformat(),
            "path_type": record.path_type.value,
            "domain": record.problem.domain.value,
            "backend": record.quantum_execution.backend,
            "repro_hash": record.repro.hash,
            "n_qubits": record.quantum_execution.circuit.n_qubits,
            "n_shots": m.n_shots,
            "measurement_protocol": m.protocol.value,
            "payload_json": json.dumps(payload, ensure_ascii=False),
        }
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO quantum_experiment_records (
                    id, timestamp, path_type, domain, backend, repro_hash,
                    n_qubits, n_shots, measurement_protocol, payload_json
                ) VALUES (
                    :id, :timestamp, :path_type, :domain, :backend, :repro_hash,
                    :n_qubits, :n_shots, :measurement_protocol, :payload_json
                )
                ON CONFLICT(id) DO UPDATE SET
                    timestamp=excluded.timestamp,
                    path_type=excluded.path_type,
                    domain=excluded.domain,
                    backend=excluded.backend,
                    repro_hash=excluded.repro_hash,
                    n_qubits=excluded.n_qubits,
                    n_shots=excluded.n_shots,
                    measurement_protocol=excluded.measurement_protocol,
                    payload_json=excluded.payload_json,
                    ingested_at=datetime('now')
                """,
                row,
            )

    def ingest_file(self, json_path: str | Path) -> QuantumExperimentRecord:
        path = Path(json_path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        record = QuantumExperimentRecord.model_validate(payload)
        self.ingest(record)
        return record

    def ingest_directory(
        self,
        directory: str | Path,
        *,
        pattern: str = "*.json",
    ) -> list[QuantumExperimentRecord]:
        records: list[QuantumExperimentRecord] = []
        for path in sorted(Path(directory).glob(pattern)):
            if path.name.startswith("."):
                continue
            records.append(self.ingest_file(path))
        return records

    def get(self, record_id: str | UUID) -> QuantumExperimentRecord | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT payload_json FROM quantum_experiment_records WHERE id = ?",
                (str(record_id),),
            ).fetchone()
        if row is None:
            return None
        return QuantumExperimentRecord.model_validate(json.loads(row["payload_json"]))

    def list_ids(
        self,
        *,
        path_type: PathType | None = None,
        domain: ProblemDomain | None = None,
        backend: str | None = None,
        limit: int = 100,
    ) -> list[str]:
        clauses: list[str] = []
        params: list[Any] = []
        if path_type is not None:
            clauses.append("path_type = ?")
            params.append(path_type.value)
        if domain is not None:
            clauses.append("domain = ?")
            params.append(domain.value)
        if backend is not None:
            clauses.append("backend = ?")
            params.append(backend)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""
            SELECT id FROM quantum_experiment_records
            {where}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [row["id"] for row in rows]

    def count(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS n FROM quantum_experiment_records").fetchone()
        return int(row["n"])

    def iter_records(
        self,
        *,
        path_type: PathType | None = None,
        domain: ProblemDomain | None = None,
    ) -> Iterator[QuantumExperimentRecord]:
        for record_id in self.list_ids(path_type=path_type, domain=domain, limit=10_000):
            record = self.get(record_id)
            if record is not None:
                yield record

    def export_parquet(self, parquet_path: str | Path) -> int:
        """Export flat summary + full JSON payload to Parquet (requires pyarrow)."""
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError("pandas is required for Parquet export") from exc
        try:
            import pyarrow  # noqa: F401
        except ImportError as exc:
            raise ImportError(
                "pyarrow is required for Parquet export: pip install pyarrow"
            ) from exc

        rows: list[dict[str, Any]] = []
        with self._connect() as conn:
            for row in conn.execute(
                "SELECT * FROM quantum_experiment_records ORDER BY timestamp"
            ):
                rows.append(dict(row))

        if not rows:
            Path(parquet_path).parent.mkdir(parents=True, exist_ok=True)
            pd.DataFrame(columns=["id", "payload_json"]).to_parquet(parquet_path, index=False)
            return 0

        df = pd.DataFrame(rows)
        Path(parquet_path).parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(parquet_path, index=False)
        return len(df)

    def import_parquet(self, parquet_path: str | Path) -> int:
        """Re-ingest records from a Parquet export (validates each payload)."""
        try:
            import pandas as pd
        except ImportError as exc:
            raise ImportError("pandas is required for Parquet import") from exc

        df = pd.read_parquet(parquet_path)
        if "payload_json" not in df.columns:
            raise ValueError("Parquet file missing payload_json column")

        count = 0
        for raw in df["payload_json"]:
            if isinstance(raw, str):
                payload = json.loads(raw)
            else:
                payload = raw
            record = QuantumExperimentRecord.model_validate(payload)
            self.ingest(record)
            count += 1
        return count


def default_store_path(base_dir: str | Path | None = None) -> Path:
    root = Path(base_dir or Path.cwd())
    return root / "data" / "quantum_experiment_records.sqlite"
