#!/usr/bin/env python3
"""Check if constraint files are up to date with pyproject.toml.

This script verifies that the pinned constraint files match what pip-compile
would generate. It's used in CI to ensure developers run update_constraints.py
before committing changes to dependencies.

Usage:
    python scripts/check_constraints_freshness.py

Exit codes:
    0: All constraint files are up to date
    1: Constraint files are outdated or missing

Requirements:
    pip install pip-tools
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path


def _pip_compile_exe() -> str:
    """Prefer pip-compile beside the active interpreter (avoids stale conda on PATH)."""
    for base in (Path(sys.executable).parent, Path(sys.executable).resolve().parent):
        candidate = base / "pip-compile"
        if candidate.is_file():
            return str(candidate)
    return "pip-compile"


def check_constraint_freshness(
    pyproject_toml: Path,
    constraint_file: Path,
    extras: list[str],
) -> bool:
    """Check if a constraint file matches what pip-compile would generate."""
    if not constraint_file.exists():
        print(f"✗ {constraint_file} does not exist")
        return False

    # Generate fresh constraints to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        cmd = [
            _pip_compile_exe(),
            "--output-file",
            tmp_path,
            "--no-header",
            "--no-annotate",
            "--strip-extras",
        ]

        for extra in extras:
            cmd.extend(["--extra", extra])

        cmd.append(str(pyproject_toml))

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"✗ Failed to generate fresh constraints for {constraint_file}")
            print(f"  stderr: {result.stderr}")
            return False

        # Compare generated constraints with existing file
        with open(constraint_file) as f:
            existing = f.read()

        with open(tmp_path) as f:
            generated = f.read()

        if existing != generated:
            print(f"✗ {constraint_file} is outdated")
            print("  Run: python scripts/update_constraints.py")
            return False

        print(f"✓ {constraint_file} is up to date")
        return True

    finally:
        # Clean up temporary file
        Path(tmp_path).unlink(missing_ok=True)


def main() -> int:
    """Check all constraint files."""
    project_root = Path(__file__).parent.parent
    constraints_dir = project_root / "constraints"
    pyproject_toml = project_root / "pyproject.toml"

    if not pyproject_toml.exists():
        print(f"ERROR: {pyproject_toml} not found")
        return 1

    # Check if pip-compile is available
    try:
        subprocess.run([_pip_compile_exe(), "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("ERROR: pip-compile not found. Install it with: pip install pip-tools")
        return 1

    print("Checking constraint file freshness...")
    print()

    all_fresh = True

    # Check dev.txt
    if not check_constraint_freshness(
        pyproject_toml,
        constraints_dir / "dev.txt",
        extras=["dev"],
    ):
        all_fresh = False

    # Check uqc.txt
    if not check_constraint_freshness(
        pyproject_toml,
        constraints_dir / "uqc.txt",
        extras=["uqc"],
    ):
        all_fresh = False

    print()
    if all_fresh:
        print("✓ All constraint files are up to date")
        return 0
    else:
        print("✗ Some constraint files are outdated")
        print()
        print("To fix:")
        print("  1. Run: python scripts/update_constraints.py")
        print("  2. Review changes: git diff constraints/")
        print("  3. Commit: git add constraints/ && git commit -m 'Update dependency constraints'")
        return 1


if __name__ == "__main__":
    sys.exit(main())
