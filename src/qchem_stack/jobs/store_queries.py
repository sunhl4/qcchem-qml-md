"""Job listing and aggregate status counts (mixin)."""

from __future__ import annotations

from typing import Any

from .store_schema import JobListItem, JobStoreSqlProtocol, meta_top_str
from .store_sql import JSON_SCAN_CAP, rows_to_list_items


class JobStoreQueriesMixin:
    """List/filter jobs and status histograms."""

    def count_by_status(self: JobStoreSqlProtocol) -> dict[str, int]:
        con = self._connect()
        rows = con.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status").fetchall()
        con.close()
        return {str(st): int(n) for st, n in rows}

    def list_jobs(
        self: JobStoreSqlProtocol,
        *,
        status: str | None = None,
        job_kind: str | None = None,
        experiment_id: str | None = None,
        api_workspace_label: str | None = None,
        api_project_slug: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[JobListItem]:
        import sqlite3

        lim = max(1, min(int(limit), 500))
        off = max(0, min(int(offset), 10_000))
        clauses: list[str] = []
        params: list[Any] = []
        if status is not None:
            clauses.append("status=?")
            params.append(status)
        if job_kind is not None:
            clauses.append("job_kind=?")
            params.append(job_kind)

        meta_eq: list[tuple[str, str]] = []
        if experiment_id is not None:
            meta_eq.append(("experiment_id", experiment_id))
        if api_workspace_label is not None:
            meta_eq.append(("api_workspace_label", api_workspace_label))
        if api_project_slug is not None:
            meta_eq.append(("api_project_slug", api_project_slug))

        where_base = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        con = self._connect()
        try:
            if not meta_eq:
                sql = (
                    f"SELECT job_id, status, job_kind, created, updated, protocol_hash, meta "
                    f"FROM jobs {where_base} ORDER BY created DESC, rowid DESC LIMIT ? OFFSET ?"
                )
                rows = con.execute(sql, [*params, lim, off]).fetchall()
                return list(rows_to_list_items(rows))

            json_parts = [f"json_extract(meta, '$.{k}') = ?" for k, _ in meta_eq]
            exp_clauses = [*clauses, *json_parts]
            exp_params = [*params, *[v for _, v in meta_eq]]
            where_exp = f"WHERE {' AND '.join(exp_clauses)}"
            sql_json = (
                f"SELECT job_id, status, job_kind, created, updated, protocol_hash, meta "
                f"FROM jobs {where_exp} ORDER BY created DESC, rowid DESC LIMIT ? OFFSET ?"
            )
            try:
                rows = con.execute(sql_json, [*exp_params, lim, off]).fetchall()
                return list(rows_to_list_items(rows))
            except sqlite3.OperationalError:
                scan_n = min(lim + off + 500, JSON_SCAN_CAP)
                scan_sql = (
                    f"SELECT job_id, status, job_kind, created, updated, protocol_hash, meta "
                    f"FROM jobs {where_base} ORDER BY created DESC, rowid DESC LIMIT ?"
                )
                scanned = con.execute(scan_sql, [*params, scan_n]).fetchall()

                def _row_matches(r: Any) -> bool:
                    return all(meta_top_str(r[6], k) == v for k, v in meta_eq)

                filtered = [r for r in scanned if _row_matches(r)]
                return list(rows_to_list_items(filtered[off : off + lim]))
        finally:
            con.close()
