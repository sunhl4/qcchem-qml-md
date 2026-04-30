"""Smoke tests for ``qchem_stack.integrations`` (no commercial accounts)."""

from __future__ import annotations

from dataclasses import replace

from qchem_stack.backends.spec import CircuitIR
from qchem_stack.chem.embedding.dmet import DMETContext, VQEFragmentSolverStub
from qchem_stack.integrations import (
    OneShotEmbeddingDriver,
    probe_qnexus_installation,
    qermit_capability_matrix,
    tensornet_closure_strategy,
)
from qchem_stack.integrations.dmet_self_consistent import DMETBathState, DMETSelfConsistencyLoop
from qchem_stack.integrations.tket_fullchain import (
    TketCompileMode,
    circuit_ir_to_tket_stats_or_none,
    describe_tket_closure_layer,
)
from qchem_stack.integrations.ucc_reference import (
    IdentityRegrouping,
    build_spin_uccsd_fermion_generators,
    count_uccsd_excitations,
)


class _SequentialStubSolver:
    def solve(self, fragment_id: str, hamiltonian: object) -> dict[str, object]:  # noqa: ARG002
        return {"energy": -0.1, "note": "stub"}


def test_dmet_loop_sequential() -> None:
    ctx = DMETContext(fragments=["a", "b"], solver=_SequentialStubSolver())

    def build_ham(_fid: str, _bath: DMETBathState) -> dict:
        return {}

    def upd(bath: DMETBathState, _res: object) -> DMETBathState:
        return replace(bath, meta={**bath.meta, "tick": int(bath.meta.get("tick", 0)) + 1})

    def conv(_prev: DMETBathState, bath: DMETBathState, k: int) -> bool:
        _ = bath
        return k >= 0

    loop = DMETSelfConsistencyLoop(ctx, max_cycles=3)
    rep = loop.run_with_sequential_bath_updates(
        initial_bath=DMETBathState(meta={"tick": 0}),
        build_fragment_hamiltonian=build_ham,
        update_bath_sequential=upd,
        is_converged=conv,
    )
    assert rep.get("sequential_fragment_updates") is True
    assert rep.get("converged") is True
    assert rep.get("cycles") == 1
    assert "_final_bath_state" in rep
    hist = rep.get("history") or []
    assert len(hist) == 1
    assert len(hist[0].get("per_fragment", [])) == 2


def test_ucc_counts_and_generators() -> None:
    c = count_uccsd_excitations(8, 4)
    assert c["n_single_excitations"] == 16
    assert c["n_double_excitations"] == 36
    gens = build_spin_uccsd_fermion_generators(8, 4)
    assert len(gens) == 52


def test_ucc_policy_hook() -> None:
    class Rev(IdentityRegrouping):
        def regroup_generators(self, ops):  # type: ignore[no-untyped-def]
            return list(reversed(ops))

    g0 = build_spin_uccsd_fermion_generators(4, 2, policy=IdentityRegrouping())
    g1 = build_spin_uccsd_fermion_generators(4, 2, policy=Rev())
    assert len(g0) == len(g1)
    assert g0[0] != g1[0]


def test_dmet_one_shot() -> None:
    ctx = DMETContext(fragments=["a", "b"], solver=VQEFragmentSolverStub())
    out = OneShotEmbeddingDriver.run(ctx, {"a": {}, "b": {}})
    assert out["schema"] == "dmet_one_shot_v1"
    assert len(out["fragments"]) == 2


def test_dmet_loop_converges() -> None:
    ctx = DMETContext(fragments=["a"], solver=VQEFragmentSolverStub())

    def build_ham(_fid: str, _bath: DMETBathState) -> dict:
        return {}

    def update_bath(bath: DMETBathState, _frags) -> DMETBathState:  # type: ignore[no-untyped-def]
        n = int(bath.meta.get("tick", 0)) + 1
        return replace(bath, meta={**bath.meta, "tick": n})

    def converged(_prev: DMETBathState, bath: DMETBathState, k: int) -> bool:
        return k >= 1 or int(bath.meta.get("tick", 0)) >= 2

    loop = DMETSelfConsistencyLoop(ctx, max_cycles=5)
    rep = loop.run_with_hooks(
        initial_bath=DMETBathState(meta={}),
        build_fragment_hamiltonian=build_ham,
        update_bath=update_bath,
        is_converged=converged,
    )
    assert rep["converged"] is True
    assert rep["schema"] == "dmet_self_consistency_v1"


def test_nexus_probe_schema() -> None:
    p = probe_qnexus_installation()
    assert p.get("schema") == "qnexus_probe_v1"
    assert "available" in p


def test_qermit_matrix() -> None:
    m = qermit_capability_matrix()
    assert m["schema"] == "qermit_open_reference_v1"
    assert len(m["rows"]) >= 3


def test_tensornet_closure_map() -> None:
    t = tensornet_closure_strategy()
    assert t["schema"] == "tensornet_closure_reference_v1"
    assert "opt_einsum_demo" in t["strategies"]


def test_tket_layer_and_stats_soft() -> None:
    d = describe_tket_closure_layer()
    assert d["schema"] == "tket_closure_layer_v1"
    assert TketCompileMode.STATS.value in d["modes"]
    ir = CircuitIR(n_qubits=1, operations=[{"name": "RX", "qubits": [0], "params": {"theta": 0.1}}])
    stats = circuit_ir_to_tket_stats_or_none(ir)
    assert stats is None or stats.get("schema") == "tket_stats_attempt_v1"
