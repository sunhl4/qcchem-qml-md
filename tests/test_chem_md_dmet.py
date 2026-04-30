from __future__ import annotations

from qchem_stack.chem.embedding.dmet import DMETContext, VQEFragmentSolverStub
from qchem_stack.md_bridge import QMEFDataset, QMFrame
from qchem_stack.md_bridge.exporter import export_extended_xyz


class _StubSolver:
    def solve(self, fragment_id: str, hamiltonian: object) -> dict[str, float | str]:
        return {"fragment_id": fragment_id, "energy": -0.5, "method": "stub_vqe"}


def test_vqe_fragment_solver_stub() -> None:
    s = VQEFragmentSolverStub(depth=2)
    r = s.solve("f1", object())
    assert r["fragment_id"] == "f1"
    assert r["solver"] == "VQEFragmentSolverStub"
    assert r["hea_depth"] == 2


def test_dmet_solver_hook_and_qmef_contract(tmp_path) -> None:
    ctx = DMETContext(fragments=["A", "B"], solver=None)
    ctx.register_solver(_StubSolver())  # type: ignore[arg-type]
    assert ctx.solver is not None
    out_a = ctx.solver.solve("A", {})
    assert out_a["energy"] == -0.5

    fr = QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=[[0, 0, 0], [0, 0, 1.4]],
        energy_hartree=float(out_a["energy"]),
        forces_hartree_bohr=[[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]],
        method_tag="DMET_stub",
        protocol_hash="dmet_test",
    )
    ds = QMEFDataset(
        frames=[fr],
        provenance_yaml="dmet_fragments: [A, B]\n",
    )
    assert ds.frames[0].protocol_hash == "dmet_test"
    xyz = tmp_path / "out.xyz"
    export_extended_xyz(ds, xyz)
    assert xyz.exists()
