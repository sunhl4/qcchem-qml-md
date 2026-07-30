"""In-process pipeline: SCF → pre-quantum → variational → embedding → excited → protocol finalize.

Orchestration wires chem, quantum, and backends; it must not be imported from those layers.

Stage map (``run_pipeline_sync``; see ``stage_registry.PIPELINE_STAGE_SPECS``)
---------------------------------------------------------------------------
1. **scf** — ``run_scf_stage``
2. **pre_quantum** — ``build_pre_quantum_stage`` (post_run hook ``bind_post_pre_quantum_ctx``
   collects **repro** metadata once the Hamiltonian is fixed; ``repro`` is therefore *not* a
   standalone stage, despite some older docs listing it as one)
3. **variational** — ``run_variational_stage``
4. **embedding_workflow** — ``apply_embedding_workflow_stage``
5. **excited** — ``run_excited_stages``
6. **protocol_finalize** — ``run_protocol_and_finalize_stage``

Note on ordering: ``embedding_workflow`` runs **after** ``variational`` by design — it applies
a post-variational embedding correction / parity snapshot on top of the converged variational
result rather than before it. Do not reorder without updating the parity contracts.

Lifecycle names and events: ``stage_registry.PIPELINE_STAGE_LIFECYCLES``.
Implementation body: ``pipeline_sync_runner.run_pipeline_sync``.

``run_pipeline_from_config`` adds an optional **job_enqueue** step when
``pauli_protocol_enabled(cfg)`` and ``job_db`` are set.
"""

from __future__ import annotations

import asyncio
import hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import TYPE_CHECKING, cast

import numpy as np

from qchem_stack.backends.factory import executor_from_spec
from qchem_stack.config import (
    ExperimentConfig,
    backend_spec_from_config,
    compiler_pass_bundle_from_config,
    load_experiment_config,
)
from qchem_stack.config.quantum_helpers import pauli_protocol_enabled, resolve_vqe_depth
from qchem_stack.exceptions import PipelineError
from qchem_stack.jobs.store import SqliteJobStore
from qchem_stack.orchestration.pipeline_assembly import (
    assemble_pipeline_result_dict,
    patch_repro_parity_snapshot,
)
from qchem_stack.orchestration.pipeline_result import PipelineResultV1, tag_pipeline_result
from qchem_stack.orchestration.pipeline_sync_runner import run_pipeline_sync as _run_pipeline_sync
from qchem_stack.orchestration.protocol_finalize_stage import (
    ansatz_prep_for_job,
    protocol_for_job,
)
from qchem_stack.orchestration.repro_metadata import (
    collect_repro_metadata_impl as _collect_repro_metadata_impl,
)
from qchem_stack.orchestration.repro_snapshot import repro_quantum_snapshot
from qchem_stack.orchestration.repro_summary import attach_run_summary
from qchem_stack.protocols.protocol import PauliAveragingProtocol

if TYPE_CHECKING:
    from collections.abc import Callable

    from qchem_stack.chem.hamiltonian import QubitHamiltonian
    from qchem_stack.orchestration.run_context import RunContext

__all__ = [
    "assemble_pipeline_result_dict",
    "collect_repro_metadata",
    "patch_repro_parity_snapshot",
    "run_pipeline_async",
    "run_pipeline_batch_async",
    "run_pipeline_from_config",
    "run_pipeline_sync",
]


def collect_repro_metadata(
    cfg: ExperimentConfig,
    cfg_path: Path | None = None,
    qh: QubitHamiltonian | None = None,
) -> dict[str, object]:
    return _collect_repro_metadata_impl(
        cfg,
        parity_snapshot_fn=repro_quantum_snapshot,
        cfg_path=cfg_path,
        qh=qh,
    )


def run_pipeline_sync(
    cfg: ExperimentConfig,
    *,
    cfg_path: Path | None = None,
    hamiltonian_out: list[QubitHamiltonian] | None = None,
    run_context: RunContext | None = None,
    job_timeline_emit: Callable[[dict[str, object]], None] | None = None,
) -> PipelineResultV1:
    """Run chemistry + VQE/ADAPT + optional excited stages + optional Pauli protocol in-process."""
    return _run_pipeline_sync(
        cfg,
        cfg_path=cfg_path,
        hamiltonian_out=hamiltonian_out,
        run_context=run_context,
        job_timeline_emit=job_timeline_emit,
        collect_repro_metadata_fn=collect_repro_metadata,
    )


def run_pipeline_from_config(
    cfg_path: str | Path,
    *,
    job_db: Path | None = None,
    enqueue_only: bool = False,
    run_context: RunContext | None = None,
) -> PipelineResultV1:
    """Sync pipeline plus optional job enqueue (pickled :class:`PauliAveragingProtocol`)."""
    p = Path(cfg_path)
    cfg = load_experiment_config(p)
    qh_lane: list[QubitHamiltonian] = []
    sync = run_pipeline_sync(cfg, cfg_path=p, hamiltonian_out=qh_lane, run_context=run_context)

    if job_db is None or not pauli_protocol_enabled(cfg):
        return tag_pipeline_result(sync)

    qh = qh_lane[0]
    angles_raw = sync.get("angles")
    if angles_raw is None:
        raise PipelineError("pipeline sync missing angles before job enqueue")
    angles = np.asarray(angles_raw, dtype=float)
    bspec2 = backend_spec_from_config(cfg)
    exe2 = executor_from_spec(bspec2)
    bundle2 = compiler_pass_bundle_from_config(cfg)
    proto = protocol_for_job(cfg, qh, bspec=bspec2, exe=exe2, bundle=bundle2)
    prep = ansatz_prep_for_job(cfg, qh, angles, hea_depth=resolve_vqe_depth(cfg))
    from qchem_stack.protocols.product_contract import validate_pauli_protocol_for_config

    validate_pauli_protocol_for_config(cfg, ansatz=prep.kind)
    proto.build(angles, hea_depth=resolve_vqe_depth(cfg), ansatz_prep=prep)
    proto.compile()
    blob = proto.dumps()
    ph = hashlib.sha256(blob).hexdigest()[:24]
    store = SqliteJobStore(job_db)
    handle = proto.launch(store)
    sync["job"] = {"job_id": handle.job_id, "protocol_hash": ph, "store": str(job_db)}
    if not enqueue_only:
        PauliAveragingProtocol.process_job(store, handle.job_id)
        sync["job_result"] = store.result(handle.job_id)
    attach_run_summary(cast("dict[str, object]", sync), cfg)
    return tag_pipeline_result(sync)


async def run_pipeline_async(
    cfg_path: str | Path,
    *,
    job_db: Path | None = None,
    enqueue_only: bool = False,
    run_context: RunContext | None = None,
    executor: ThreadPoolExecutor | None = None,
) -> PipelineResultV1:
    """Async wrapper for :func:`run_pipeline_from_config`."""
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        executor,
        lambda: run_pipeline_from_config(
            cfg_path,
            job_db=job_db,
            enqueue_only=enqueue_only,
            run_context=run_context,
        ),
    )


async def run_pipeline_batch_async(
    cfg_paths: list[str | Path],
    *,
    job_db: Path | None = None,
    max_workers: int | None = None,
) -> list[PipelineResultV1]:
    """Run multiple pipelines concurrently in async mode."""
    pool = ThreadPoolExecutor(max_workers=max_workers)
    try:
        tasks = [
            run_pipeline_async(cfg_path, job_db=job_db, executor=pool) for cfg_path in cfg_paths
        ]
        return await asyncio.gather(*tasks)
    finally:
        pool.shutdown(wait=True)
