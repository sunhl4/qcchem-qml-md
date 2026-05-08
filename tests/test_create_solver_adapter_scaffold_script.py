from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _load_scaffold_module():
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "create_solver_adapter_scaffold.py"
    spec = importlib.util.spec_from_file_location("_scs", script)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, root


def test_package_import_for_solver_file_strips_src() -> None:
    mod, root = _load_scaffold_module()
    out = root / "src" / "qchem_stack" / "chem" / "solvers" / "foo_bar_solver.py"
    assert mod._package_import_for_solver_file(root, out) == "qchem_stack.chem.solvers.foo_bar_solver"


def test_create_solver_adapter_scaffold_writes_template(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "create_solver_adapter_scaffold.py"
    out = tmp_path / "demo_backend_solver.py"
    cp = subprocess.run(
        [sys.executable, str(script), "demo_backend", "--output", str(out)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode == 0, cp.stderr
    txt = out.read_text(encoding="utf-8")
    assert "class DemoBackendIntegralSolver" in txt
    assert 'backend_id="demo_backend"' in txt
    assert "TODO[1]" in txt and "TODO[2]" in txt and "TODO[3]" in txt
    assert "register_solver" in cp.stdout


def test_create_solver_adapter_scaffold_rejects_invalid_backend_id(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "create_solver_adapter_scaffold.py"
    out = tmp_path / "x.py"
    cp = subprocess.run(
        [sys.executable, str(script), "Demo-Backend!", "--output", str(out)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode != 0


def test_create_solver_adapter_scaffold_with_demo_register(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    script = root / "scripts" / "create_solver_adapter_scaffold.py"
    solver = tmp_path / "solver_scaffold_xyz_solver.py"
    demo = tmp_path / "run_register_scaffold_xyz.py"
    cp = subprocess.run(
        [
            sys.executable,
            str(script),
            "scaffold_xyz",
            "--output",
            str(solver),
            "--with-demo-register",
            "--demo-output",
            str(demo),
            "--force",
        ],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    assert cp.returncode == 0, cp.stderr
    demo_txt = demo.read_text(encoding="utf-8")
    assert "register_solver" in demo_txt
    assert "importlib.util" in demo_txt
    assert "scaffold_xyz" in demo_txt
    assert str(solver.resolve()) in demo_txt

    run = subprocess.run([sys.executable, str(demo)], cwd=str(root), capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
