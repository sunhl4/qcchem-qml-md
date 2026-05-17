"""Registry bootstrap and :func:`~qchem_stack.chem.solvers.create_solver` wiring."""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

import pytest

import qchem_stack.chem.solvers.registry as solver_registry
from qchem_stack.chem.bridges.facade import classical_mean_field_via_solver_bridge
from qchem_stack.chem.solvers import (
    InvalidSolverIdError,
    SolverRegistrationInfo,
    UnknownSolverError,
    create_solver,
    register_solver,
    registered_solver_ids,
    registered_solvers_detail,
)
from qchem_stack.chem.solvers.psi4_solver import Psi4IntegralSolver
from qchem_stack.chem.solvers.pyscf_solver import PySCFIntegralSolver
from qchem_stack.chem.solvers.registry import (
    SolverRegistrationError,
    set_entrypoint_conflict_policy,
)
from qchem_stack.config import ExperimentConfig, load_experiment_config
from tests.helpers.solver_registry_state import reset_solver_registry_state


class _FakeEntryPoint:
    def __init__(self, *, name: str, value: str, factory: object) -> None:
        self.name = name
        self.value = value
        self._factory = factory

    def load(self) -> object:
        return self._factory


class _FakeEntrypointsSelect:
    def __init__(self, entry_points: list[_FakeEntryPoint]) -> None:
        self._entry_points = entry_points

    def select(self, *, group: str) -> list[_FakeEntryPoint]:
        if group != "qchem_stack.chem_solvers":
            return []
        return list(self._entry_points)


def test_registered_solver_ids_include_pyscf_and_psi4() -> None:
    ids = registered_solver_ids()
    assert "pyscf" in ids
    assert "psi4" in ids
    assert "precomputed" in ids


def test_registered_solvers_detail_includes_builtin_metadata() -> None:
    details = registered_solvers_detail()
    assert isinstance(details, MappingProxyType)
    pyscf = details["pyscf"]
    assert isinstance(pyscf, SolverRegistrationInfo)
    assert pyscf.source == "builtin"
    assert "pyscf_solver" in pyscf.provider


def test_register_solver_adds_custom_id() -> None:
    def _fake(_cfg: ExperimentConfig) -> PySCFIntegralSolver:
        raise RuntimeError("factory should not be invoked in this test")

    register_solver("_test_only_custom_solver", _fake)
    assert "_test_only_custom_solver" in registered_solver_ids()
    assert registered_solvers_detail()["_test_only_custom_solver"].source == "runtime"


def test_register_solver_rejects_accidental_override() -> None:
    def _fake_a(_cfg: ExperimentConfig) -> PySCFIntegralSolver:
        raise RuntimeError("factory A should not be invoked in this test")

    def _fake_b(_cfg: ExperimentConfig) -> PySCFIntegralSolver:
        raise RuntimeError("factory B should not be invoked in this test")

    register_solver("_test_only_collision_solver", _fake_a)
    with pytest.raises(SolverRegistrationError, match="already registered"):
        register_solver("_test_only_collision_solver", _fake_b)


def test_register_solver_can_override_when_explicit() -> None:
    def _fake_a(_cfg: ExperimentConfig) -> PySCFIntegralSolver:
        raise RuntimeError("factory A should not be invoked in this test")

    def _fake_b(_cfg: ExperimentConfig) -> PySCFIntegralSolver:
        raise RuntimeError("factory B should not be invoked in this test")

    register_solver("_test_only_replace_solver", _fake_a)
    register_solver("_test_only_replace_solver", _fake_b, overwrite=True)


def test_register_solver_can_preoverride_builtin_before_bootstrap() -> None:
    reset_solver_registry_state()

    def _fake(_cfg: ExperimentConfig) -> PySCFIntegralSolver:
        raise RuntimeError("factory should not be invoked in this test")

    register_solver("pyscf", _fake, overwrite=True)
    assert registered_solvers_detail()["pyscf"].source == "runtime"


def test_create_solver_pyscf_and_psi4(tmp_path: Path) -> None:
    cfg_path = tmp_path / "exp.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: reg_test
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    base = load_experiment_config(cfg_path)
    py = create_solver(base)
    assert isinstance(py, PySCFIntegralSolver)
    ps = create_solver(
        base.model_copy(update={"scf": base.scf.model_copy(update={"driver": "psi4"})})
    )
    assert isinstance(ps, Psi4IntegralSolver)


def test_create_solver_unknown_driver_reports_registered_ids(tmp_path: Path) -> None:
    cfg_path = tmp_path / "exp_unknown.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: reg_unknown
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: unknown_backend
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="unknown_backend"):
        load_experiment_config(cfg_path)


def test_create_solver_rejects_invalid_driver_id() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    cfg.scf.driver = "   "
    with pytest.raises(InvalidSolverIdError, match="non-empty"):
        create_solver(cfg)


def test_set_entrypoint_conflict_policy_rejects_unknown_value() -> None:
    with pytest.raises(ValueError, match="Unknown entrypoint conflict policy"):
        set_entrypoint_conflict_policy("panic")  # type: ignore[arg-type]


def test_iter_solver_entry_points_is_sorted(monkeypatch: pytest.MonkeyPatch) -> None:
    eps = [
        _FakeEntryPoint(name="demo", value="z.mod:fac", factory=lambda _cfg: object()),
        _FakeEntryPoint(name="abc", value="b.mod:fac", factory=lambda _cfg: object()),
        _FakeEntryPoint(name="abc", value="a.mod:fac", factory=lambda _cfg: object()),
    ]
    monkeypatch.setattr(
        solver_registry,
        "entry_points",
        lambda: _FakeEntrypointsSelect(eps),
    )
    out = solver_registry._iter_solver_entry_points()
    pairs = [(ep.name, ep.value) for ep in out]
    assert pairs == [("abc", "a.mod:fac"), ("abc", "b.mod:fac"), ("demo", "z.mod:fac")]


def test_discover_entry_points_warn_policy_skips_conflict(monkeypatch: pytest.MonkeyPatch) -> None:
    set_entrypoint_conflict_policy("warn")
    eps = [
        _FakeEntryPoint(
            name="demo",
            value="a.mod:factory",
            factory=(lambda _cfg: object()),
        ),
        _FakeEntryPoint(
            name="demo",
            value="b.mod:factory",
            factory=(lambda _cfg: object()),
        ),
    ]
    monkeypatch.setattr(
        solver_registry,
        "entry_points",
        lambda: _FakeEntrypointsSelect(eps),
    )
    with pytest.warns(RuntimeWarning, match="Skipping solver entry point"):
        solver_registry._discover_external_solvers()
    details = registered_solvers_detail()
    assert details["demo"].source == "entrypoint"
    assert details["demo"].provider == "a.mod:factory"


def test_discover_entry_points_strict_policy_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    set_entrypoint_conflict_policy("strict")
    eps = [
        _FakeEntryPoint(
            name="demo",
            value="a.mod:factory",
            factory=(lambda _cfg: object()),
        ),
        _FakeEntryPoint(
            name="demo",
            value="b.mod:factory",
            factory=(lambda _cfg: object()),
        ),
    ]
    monkeypatch.setattr(
        solver_registry,
        "entry_points",
        lambda: _FakeEntrypointsSelect(eps),
    )
    with pytest.raises(SolverRegistrationError, match="already registered"):
        solver_registry._discover_external_solvers()


@pytest.fixture(autouse=True)
def _reset_solver_registry_after_each_test() -> None:
    yield
    reset_solver_registry_state()


def test_example_h2_config_loads_through_registry_pyscf() -> None:
    root = Path(__file__).resolve().parents[1]
    cfg = load_experiment_config(root / "configs" / "example_h2.yaml")
    sol = create_solver(cfg)
    assert isinstance(sol, PySCFIntegralSolver)


def test_classical_mean_field_facade_uses_registry_and_merges_headers(tmp_path: Path) -> None:
    """Downstream SCF entry must go through create_solver, not ad-hoc PySCF imports."""
    cfg_path = tmp_path / "exp.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: facade_registry
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: pyscf
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    out = classical_mean_field_via_solver_bridge(cfg)
    assert out.driver_meta.get("upstream_classical_software_tag") == "pyscf"
    assert out.driver_meta.get("classical_problem_periodic_boundary_condition") is False
    assert float(out.e_tot) < 0.0


def test_psi4_compute_mean_field_smoke_and_canonical_headers(tmp_path: Path) -> None:
    pytest.importorskip("psi4")
    cfg_path = tmp_path / "exp_psi4.yaml"
    cfg_path.write_text(
        """
schema_version: "1"
experiment_id: psi4_smoke
random_seed: 0
molecule:
  symbols: ["H", "H"]
  coordinates_bohr:
    - [0.0, 0.0, 0.0]
    - [0.0, 0.0, 1.4]
  charge: 0
  multiplicity: 1
  basis: sto-3g
scf:
  driver: psi4
  method: RHF
active_space:
  n_active_orbitals: 2
  n_active_electrons: 2
""",
        encoding="utf-8",
    )
    cfg = load_experiment_config(cfg_path)
    out = classical_mean_field_via_solver_bridge(cfg)
    assert out.driver_meta.get("upstream_classical_software_tag") == "psi4"
    assert out.driver_meta.get("classical_problem_periodic_boundary_condition") is False
