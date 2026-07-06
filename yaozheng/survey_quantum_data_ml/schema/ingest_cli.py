#!/usr/bin/env python3
"""CLI for ingesting and exporting quantum experiment records."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCHEMA_DIR = Path(__file__).resolve().parent
if str(_SCHEMA_DIR) not in sys.path:
    sys.path.insert(0, str(_SCHEMA_DIR))

from quantum_data_store import SqliteQuantumDataStore, default_store_path  # noqa: E402
from quantum_experiment_record import PathType, ProblemDomain  # noqa: E402


def _parse_path_type(value: str | None) -> PathType | None:
    if value is None:
        return None
    return PathType(value)


def _parse_domain(value: str | None) -> ProblemDomain | None:
    if value is None:
        return None
    return ProblemDomain(value)


def cmd_ingest(args: argparse.Namespace) -> int:
    store = SqliteQuantumDataStore(args.db)
    path = Path(args.path)
    if path.is_dir():
        records = store.ingest_directory(path, pattern=args.pattern)
        print(f"Ingested {len(records)} record(s) from {path}")
    else:
        record = store.ingest_file(path)
        print(f"Ingested {record.id} ({record.path_type.value}, {record.problem.domain.value})")
    print(f"Total in store: {store.count()}")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    store = SqliteQuantumDataStore(args.db)
    ids = store.list_ids(
        path_type=_parse_path_type(args.path_type),
        domain=_parse_domain(args.domain),
        backend=args.backend,
        limit=args.limit,
    )
    for record_id in ids:
        print(record_id)
    print(f"# total in store: {store.count()}, shown: {len(ids)}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    store = SqliteQuantumDataStore(args.db)
    record = store.get(args.id)
    if record is None:
        print(f"Not found: {args.id}", file=sys.stderr)
        return 1
    print(record.model_dump_json(indent=2))
    return 0


def cmd_export_parquet(args: argparse.Namespace) -> int:
    store = SqliteQuantumDataStore(args.db)
    n = store.export_parquet(args.output)
    print(f"Exported {n} row(s) to {args.output}")
    return 0


def cmd_import_parquet(args: argparse.Namespace) -> int:
    store = SqliteQuantumDataStore(args.db)
    n = store.import_parquet(args.input)
    print(f"Imported {n} record(s) from {args.input}; total: {store.count()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--db",
        type=Path,
        default=default_store_path(_SCHEMA_DIR.parent),
        help="SQLite database path (default: survey_quantum_data_ml/data/...)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="Ingest JSON file or directory")
    p_ingest.add_argument("path", type=Path)
    p_ingest.add_argument("--pattern", default="*.json")
    p_ingest.set_defaults(func=cmd_ingest)

    p_list = sub.add_parser("list", help="List record IDs")
    p_list.add_argument("--path-type", choices=[p.value for p in PathType])
    p_list.add_argument("--domain", choices=[d.value for d in ProblemDomain])
    p_list.add_argument("--backend")
    p_list.add_argument("--limit", type=int, default=50)
    p_list.set_defaults(func=cmd_list)

    p_show = sub.add_parser("show", help="Show one record as JSON")
    p_show.add_argument("id")
    p_show.set_defaults(func=cmd_show)

    p_exp = sub.add_parser("export-parquet", help="Export store to Parquet")
    p_exp.add_argument("-o", "--output", type=Path, required=True)
    p_exp.set_defaults(func=cmd_export_parquet)

    p_imp = sub.add_parser("import-parquet", help="Import from Parquet export")
    p_imp.add_argument("input", type=Path)
    p_imp.set_defaults(func=cmd_import_parquet)

    args = parser.parse_args()
    try:
        return args.func(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
