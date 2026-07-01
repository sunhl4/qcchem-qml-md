#!/usr/bin/env python3
"""Update dependency constraint files using pip-compile.

This script generates pinned dependency constraint files from pyproject.toml
using pip-compile (from pip-tools). The generated files ensure reproducible
installs across different environments.

Usage:
    python scripts/update_constraints.py

This will generate:
    - constraints/dev.txt: Pinned dependencies for [dev] extra
    - constraints/uqc.txt: Pinned dependencies for [uqc] extra

Requirements:
    pip install pip-tools
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _constraints_normalize():
    path = Path(__file__).resolve().parent / "_constraints_normalize.py"
    spec = importlib.util.spec_from_file_location("_constraints_normalize", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_norm = _constraints_normalize()
normalize_constraints_text = _norm.normalize_constraints_text
pip_compile_base_cmd = _norm.pip_compile_base_cmd


def _pip_compile_exe() -> str:
    for base in (Path(sys.executable).parent, Path(sys.executable).resolve().parent):
        candidate = base / "pip-compile"
        if candidate.is_file():
            return str(candidate)
    return "pip-compile"


def run_pip_compile(input_file: str, output_file: str, extras: list[str]) -> None:
    """Run pip-compile to generate constraint file."""
    print(f"Generating {output_file}...")

    cmd = pip_compile_base_cmd(_pip_compile_exe(), output_file)
    for extra in extras:
        cmd.extend(["--extra", extra])
    cmd.append(input_file)

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: pip-compile failed for {output_file}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    Path(output_file).write_text(
        normalize_constraints_text(Path(output_file).read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    print(f"✓ Generated {output_file}")


def main() -> int:
    """Update all constraint files."""
    project_root = Path(__file__).parent.parent
    constraints_dir = project_root / "constraints"

    constraints_dir.mkdir(exist_ok=True)

    pyproject_toml = project_root / "pyproject.toml"
    if not pyproject_toml.exists():
        print(f"ERROR: {pyproject_toml} not found")
        return 1

    try:
        subprocess.run([_pip_compile_exe(), "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: pip-compile not found. Install it with: pip install pip-tools")
        return 1

    print("Updating dependency constraints...")
    print()

    run_pip_compile(str(pyproject_toml), str(constraints_dir / "dev.txt"), extras=["dev"])
    run_pip_compile(str(pyproject_toml), str(constraints_dir / "uqc.txt"), extras=["uqc"])

    print()
    print("✓ All constraint files updated successfully")
    print()
    print("Next steps:")
    print("  1. Review the changes: git diff constraints/")
    print(
        "  2. Commit if satisfied: git add constraints/ && git commit -m 'Update dependency constraints'"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
