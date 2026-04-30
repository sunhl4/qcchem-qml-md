"""SqliteJobStore.list_jobs (no FastAPI)."""

from __future__ import annotations

import tempfile

from qchem_stack.jobs.pipeline_jobs import enqueue_full_pipeline_run
from qchem_stack.jobs.store import JobStatus, SqliteJobStore
from qchem_stack.orchestration.run_context import RunContext


def test_list_jobs_newest_first_and_filter() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/x.sqlite"
        store = SqliteJobStore(path)
        rc = RunContext.new()
        h1 = enqueue_full_pipeline_run(
            store,
            config_yaml="experiment_id: a\n",
            run_context=rc,
            meta_extra={"experiment_id": "a"},
        )
        h2 = enqueue_full_pipeline_run(
            store,
            config_yaml="experiment_id: b\n",
            run_context=rc,
            meta_extra={"experiment_id": "b"},
        )
        all_rows = store.list_jobs(limit=10)
        ids = [r["job_id"] for r in all_rows]
        assert h2.job_id in ids and h1.job_id in ids
        assert ids.index(h2.job_id) < ids.index(h1.job_id)
        q = store.list_jobs(status=JobStatus.QUEUED.value, job_kind="full_pipeline", limit=5)
        assert len(q) == 2
        qa = store.list_jobs(experiment_id="a", limit=5)
        assert len(qa) == 1 and qa[0]["job_id"] == h1.job_id
        s = store.get_job_public_summary(h1.job_id)
        assert s["job_id"] == h1.job_id
        assert s["meta"]["experiment_id"] == "a"
        cnt = store.count_by_status()
        assert cnt.get(JobStatus.QUEUED.value) == 2


def test_list_jobs_filter_api_workspace_label() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/w.sqlite"
        store = SqliteJobStore(path)
        rc = RunContext.new()
        enqueue_full_pipeline_run(
            store,
            config_yaml="experiment_id: same\n",
            run_context=rc,
            meta_extra={"experiment_id": "same", "api_workspace_label": "team-a"},
        )
        enqueue_full_pipeline_run(
            store,
            config_yaml="experiment_id: same\n",
            run_context=rc,
            meta_extra={"experiment_id": "same", "api_workspace_label": "team-b"},
        )
        fa = store.list_jobs(experiment_id="same", api_workspace_label="team-a", limit=10)
        assert len(fa) == 1
        assert fa[0].get("meta", {}).get("api_workspace_label") == "team-a"


def test_list_jobs_filter_api_project_slug() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/p2.sqlite"
        store = SqliteJobStore(path)
        rc = RunContext.new()
        enqueue_full_pipeline_run(
            store,
            config_yaml="experiment_id: slugtest\n",
            run_context=rc,
            meta_extra={"experiment_id": "slugtest", "api_project_slug": "p-x"},
        )
        enqueue_full_pipeline_run(
            store,
            config_yaml="experiment_id: slugtest\n",
            run_context=rc,
            meta_extra={"experiment_id": "slugtest", "api_project_slug": "p-y"},
        )
        fx = store.list_jobs(experiment_id="slugtest", api_project_slug="p-x", limit=10)
        assert len(fx) == 1
        assert fx[0].get("meta", {}).get("api_project_slug") == "p-x"


def test_list_jobs_offset_pagination() -> None:
    with tempfile.TemporaryDirectory() as d:
        path = f"{d}/p.sqlite"
        store = SqliteJobStore(path)
        rc = RunContext.new()
        h1 = enqueue_full_pipeline_run(
            store,
            config_yaml="experiment_id: p1\n",
            run_context=rc,
            meta_extra={"experiment_id": "p1"},
        )
        h2 = enqueue_full_pipeline_run(
            store,
            config_yaml="experiment_id: p2\n",
            run_context=rc,
            meta_extra={"experiment_id": "p2"},
        )
        h3 = enqueue_full_pipeline_run(
            store,
            config_yaml="experiment_id: p3\n",
            run_context=rc,
            meta_extra={"experiment_id": "p3"},
        )
        page0 = store.list_jobs(limit=1, offset=0)
        page1 = store.list_jobs(limit=1, offset=1)
        assert len(page0) == 1 and len(page1) == 1
        assert page0[0]["job_id"] == h3.job_id
        assert page1[0]["job_id"] == h2.job_id
        two = store.list_jobs(limit=2, offset=0)
        assert [two[0]["job_id"], two[1]["job_id"]] == [h3.job_id, h2.job_id]
        assert {r["job_id"] for r in store.list_jobs(limit=10)} == {h1.job_id, h2.job_id, h3.job_id}
