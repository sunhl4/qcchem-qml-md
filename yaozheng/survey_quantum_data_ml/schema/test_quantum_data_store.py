"""Tests for quantum experiment record store."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_SCHEMA = Path(__file__).resolve().parent
if str(_SCHEMA) not in sys.path:
    sys.path.insert(0, str(_SCHEMA))

from quantum_data_store import SqliteQuantumDataStore  # noqa: E402
from quantum_experiment_record import PathType, ProblemDomain  # noqa: E402

EXAMPLES = _SCHEMA / "examples"


@pytest.fixture
def store(tmp_path: Path) -> SqliteQuantumDataStore:
    return SqliteQuantumDataStore(tmp_path / "test.sqlite")


def test_ingest_hybrid_example(store: SqliteQuantumDataStore) -> None:
    record = store.ingest_file(EXAMPLES / "hybrid_many_body.json")
    assert store.count() == 1
    assert record.path_type == PathType.HYBRID
    got = store.get(record.id)
    assert got is not None
    assert got.problem.domain == ProblemDomain.MANY_BODY


def test_ingest_native_example(store: SqliteQuantumDataStore) -> None:
    store.ingest_file(EXAMPLES / "native_shadow_only.json")
    ids = store.list_ids(path_type=PathType.NATIVE)
    assert len(ids) == 1


def test_ingest_directory(store: SqliteQuantumDataStore) -> None:
    records = store.ingest_directory(EXAMPLES)
    assert len(records) == 2
    assert store.count() == 2


def test_export_parquet_roundtrip(store: SqliteQuantumDataStore, tmp_path: Path) -> None:
    pytest.importorskip("pyarrow")
    store.ingest_directory(EXAMPLES)
    pq = tmp_path / "export.parquet"
    n = store.export_parquet(pq)
    assert n == 2

    store2 = SqliteQuantumDataStore(tmp_path / "other.sqlite")
    imported = store2.import_parquet(pq)
    assert imported == 2
    assert store2.count() == 2


def test_validate_script_examples() -> None:
    for name in ("hybrid_many_body.json", "native_shadow_only.json"):
        payload = json.loads((EXAMPLES / name).read_text(encoding="utf-8"))
        from quantum_experiment_record import QuantumExperimentRecord

        QuantumExperimentRecord.model_validate(payload)
