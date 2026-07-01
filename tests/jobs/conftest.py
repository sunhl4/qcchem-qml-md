"""Shared fixtures for job store integration tests."""

from __future__ import annotations

import os

import pytest


@pytest.fixture
def pg_store():
    url = os.environ.get("QCHEM_JOB_DATABASE_URL")
    if not url:
        pytest.skip("QCHEM_JOB_DATABASE_URL not set")
    from qchem_stack.jobs.store_postgres import PostgresJobStore

    store = PostgresJobStore(url)
    con = store._connect()
    try:
        con.execute("DELETE FROM jobs")
        con.commit()
    finally:
        con.close()
    return store
