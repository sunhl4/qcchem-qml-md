#!/usr/bin/env python3
"""Generate a minimal ChemIntegralSolver scaffold for a new backend.

With ``--with-demo-register``, also emit a runnable script that registers the solver
and runs the same adapter-contract checks as ``scripts/check_solver_adapter_contract.py``
(without spawning a second Python process).
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def _snake(name: str) -> str:
    s = name.strip().lower().replace("-", "_")
    if not re.fullmatch(r"[a-z][a-z0-9_]*", s):
        raise ValueError(
            "backend id must match [a-z][a-z0-9_]* after lowercasing and '-' to '_' conversion"
        )
    return s


def _class_name(backend_id: str) -> str:
    return "".join(part.capitalize() for part in backend_id.split("_")) + "IntegralSolver"


def _package_import_for_solver_file(root: Path, out: Path) -> str | None:
    """Dotted import path for a file under ``src/`` (e.g. ``qchem_stack.chem.solvers.foo``)."""
    try:
        rel = out.resolve().relative_to(root.resolve())
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) >= 2 and parts[0] == "src":
        return ".".join(parts[1:]).removesuffix(".py")
    return None


def _render_demo_register_script(
    *,
    backend_id: str,
    class_name: str,
    solver_file: Path,
    module_name: str,
) -> str:
    path_literal = json.dumps(str(solver_file.resolve()))
    return f'''#!/usr/bin/env python3
"""Register ``{backend_id}`` and validate the adapter contract (same checks as ``scripts/check_solver_adapter_contract.py``, in-process).

Re-run ``create_solver_adapter_scaffold.py`` if you move the solver file.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def _repo_root() -> Path:
    """Resolve clone root containing ``scripts/check_solver_adapter_contract.py``."""
    start = Path(__file__).resolve()
    for parent in [start.parent] + list(start.parents):
        if (parent / "scripts" / "check_solver_adapter_contract.py").is_file():
            return parent
    cwd = Path.cwd()
    if (cwd / "scripts" / "check_solver_adapter_contract.py").is_file():
        return cwd
    raise RuntimeError(
        "Could not locate qchem-stack repo root. Run this script from the clone root "
        "or keep it under .../scripts/."
    )


_REPO = _repo_root()
_SOLVER_FILE = Path({path_literal})
_MODNAME = "{module_name}"


def _load_solver_class() -> type:
    spec = importlib.util.spec_from_file_location(_MODNAME, _SOLVER_FILE)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to create module spec for solver file")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[_MODNAME] = mod
    spec.loader.exec_module(mod)
    return getattr(mod, "{class_name}")


def main() -> int:
    from qchem_stack.chem.solvers import create_solver, register_solver, validate_solver_adapter_contract
    from qchem_stack.config import load_experiment_config

    cls = _load_solver_class()
    register_solver("{backend_id}", cls.from_experiment_config)
    cfg = load_experiment_config(_REPO / "configs" / "example_h2.yaml")
    cfg.scf.driver = "{backend_id}"
    solver = create_solver(cfg)
    for run_mf in (False, True):
        report = validate_solver_adapter_contract(solver, run_mean_field=bool(run_mf), periodic=False)
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
        if not report.ok:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''


def _render_solver_module(*, backend_id: str, class_name: str) -> str:
    return f'''from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from qchem_stack.chem.solvers.base import MolecularMeanFieldResult, SolverCapabilities
from qchem_stack.config import ExperimentConfig


@dataclass
class {class_name}:
    """Generated backend scaffold for ``scf.driver={backend_id}``."""

    _cfg: ExperimentConfig

    @property
    def capabilities(self) -> SolverCapabilities:
        # TODO[1]: set capabilities for your backend.
        return SolverCapabilities(
            backend_id="{backend_id}",
            supports_molecular_scf=False,
            supports_pbc_scf=False,
            supports_rhf=True,
            supports_rohf=False,
            supports_uhf=False,
            supports_implicit_solvent_ddcosmo=False,
            supports_qmmm=False,
            supports_restricted_active_space_qubit_hamiltonian=False,
        )

    @classmethod
    def from_experiment_config(cls, cfg: ExperimentConfig) -> {class_name}:
        inst = cls(cfg)
        inst.set_physical_data(cfg)
        return inst

    def set_physical_data(self, cfg: ExperimentConfig) -> None:
        self._cfg = cfg

    def compute_mean_field(self, *, periodic: bool = False) -> MolecularMeanFieldResult:
        if periodic:
            return self.run_periodic_mean_field()
        return self.run_molecular_mean_field()

    def run_molecular_mean_field(self) -> MolecularMeanFieldResult:
        # TODO[2]: replace with real backend SCF call + parsing.
        n_orb = max(1, int(self._cfg.active_space.n_active_orbitals))
        return MolecularMeanFieldResult(
            mf={{"backend": "{backend_id}", "scaffold": True}},
            e_tot=0.0,
            mo_energy=np.zeros(n_orb, dtype=float),
            driver_meta={{"generated_solver_scaffold": True}},
        )

    def run_periodic_mean_field(self) -> MolecularMeanFieldResult:
        raise NotImplementedError("{class_name} does not implement periodic SCF.")

    def get_integrals(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        # TODO[3]: implement when exposing AO/MO integrals.
        raise NotImplementedError("{class_name}.get_integrals not implemented yet.")

    def build_embedding_input_system(
        self,
        reference: Any,
        *,
        representation: str,
    ) -> dict[str, Any]:
        # TODO[4]: optional AO/Lowdin embedding input export.
        del reference, representation
        return {{}}
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backend_id", help="New scf.driver backend id (e.g. my_backend)")
    parser.add_argument(
        "--output",
        default=None,
        help="Output file path (default: src/qchem_stack/chem/solvers/<backend_id>_solver.py)",
    )
    parser.add_argument("--force", action="store_true", help="Overwrite existing file")
    parser.add_argument(
        "--with-demo-register",
        action="store_true",
        help="Also write scripts/register_<backend>_demo.py (register + in-process contract checks)",
    )
    parser.add_argument(
        "--demo-output",
        default=None,
        help="Path for demo script (default: scripts/register_<backend>_demo.py)",
    )
    args = parser.parse_args()

    backend_id = _snake(args.backend_id)
    class_name = _class_name(backend_id)
    root = Path(__file__).resolve().parents[1]
    default_out = root / "src" / "qchem_stack" / "chem" / "solvers" / f"{backend_id}_solver.py"
    out = Path(args.output).resolve() if args.output else default_out
    if out.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing file: {out} (use --force)")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        _render_solver_module(backend_id=backend_id, class_name=class_name), encoding="utf-8"
    )

    package_import = _package_import_for_solver_file(root, out)
    if package_import is not None:
        import_path = package_import
    else:
        import_path = f"<your.python.import.path.to.{out.stem}>"
    print(f"[scaffold] wrote: {out}")
    print("\n[register snippet]")
    print("from qchem_stack.chem.solvers import register_solver")
    print(f"from {import_path} import {class_name}")
    print(f'register_solver("{backend_id}", {class_name}.from_experiment_config)')
    print("\n[contract checks]")
    print(
        f"python scripts/check_solver_adapter_contract.py configs/example_h2.yaml --driver {backend_id}"
    )
    print(
        "python scripts/check_solver_adapter_contract.py "
        f"configs/example_h2.yaml --driver {backend_id} --run-mean-field"
    )

    if args.with_demo_register:
        demo_default = root / "scripts" / f"register_{backend_id}_demo.py"
        demo_out = Path(args.demo_output).resolve() if args.demo_output else demo_default
        if demo_out.exists() and not args.force:
            raise SystemExit(f"Refusing to overwrite existing demo: {demo_out} (use --force)")
        demo_out.parent.mkdir(parents=True, exist_ok=True)
        demo_out.write_text(
            _render_demo_register_script(
                backend_id=backend_id,
                class_name=class_name,
                solver_file=out,
                module_name=f"_qchem_scaffold_solver_{backend_id}",
            ),
            encoding="utf-8",
        )
        print(f"\n[demo] wrote: {demo_out}")
        try:
            print(f"python {demo_out.relative_to(root)}")
        except ValueError:
            print(f"python {demo_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
