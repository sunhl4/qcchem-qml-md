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

import subprocess
import sys
from pathlib import Path


def _pip_compile_exe() -> str:
    for base in (Path(sys.executable).parent, Path(sys.executable).resolve().parent):
        candidate = base / "pip-compile"
        if candidate.is_file():
            return str(candidate)
    return "pip-compile"


def run_pip_compile(input_file: str, output_file: str, extras: list[str]) -> None:
    """Run pip-compile to generate constraint file."""
    print(f"Generating {output_file}...")

    # Build pip-compile command
    cmd = [
        _pip_compile_exe(),
        "--output-file",
        output_file,
        "--upgrade",  # Resolve latest compatible pins (must match check_constraints_freshness)
        "--no-header",  # Omit header comment
        "--no-annotate",  # Omit annotations
        "--strip-extras",  # Remove [extras] from output
    ]

    # Add extras
    for extra in extras:
        cmd.extend(["--extra", extra])

    cmd.append(input_file)

    # Run pip-compile
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: pip-compile failed for {output_file}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        sys.exit(1)

    print(f"✓ Generated {output_file}")


def main() -> int:
    """Update all constraint files."""
    project_root = Path(__file__).parent.parent
    constraints_dir = project_root / "constraints"

    # Ensure constraints directory exists
    constraints_dir.mkdir(exist_ok=True)

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

    # Generate constraint files
    print("Updating dependency constraints...")
    print()

    # dev.txt: All dev dependencies
    run_pip_compile(
        str(pyproject_toml),
        str(constraints_dir / "dev.txt"),
        extras=["dev"],
    )

    # uqc.txt: UQC-specific dependencies
    run_pip_compile(
        str(pyproject_toml),
        str(constraints_dir / "uqc.txt"),
        extras=["uqc"],
    )

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
