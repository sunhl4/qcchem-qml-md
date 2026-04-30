from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ObservationRecord:
    experiment_id: str
    energy: float
    meta: dict[str, Any]


class ObservationCache:
    """Versioned append-only cache for energies / Pauli shards."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(path)
        con.execute(
            """CREATE TABLE IF NOT EXISTS obs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT,
                energy REAL,
                meta TEXT
            )"""
        )
        con.commit()
        con.close()

    def append(self, rec: ObservationRecord) -> None:
        con = sqlite3.connect(self.path)
        con.execute(
            "INSERT INTO obs (experiment_id, energy, meta) VALUES (?,?,?)",
            (rec.experiment_id, rec.energy, json.dumps(rec.meta)),
        )
        con.commit()
        con.close()

    def recent(self, limit: int = 50) -> list[ObservationRecord]:
        con = sqlite3.connect(self.path)
        rows = con.execute(
            "SELECT experiment_id, energy, meta FROM obs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        con.close()
        out: list[ObservationRecord] = []
        for eid, e, m in rows:
            out.append(ObservationRecord(experiment_id=eid, energy=float(e), meta=json.loads(m)))
        return out
