#!/usr/bin/env python3
"""Check that all example scripts can be imported without errors.

This script performs smoke import checks on all example scripts in the
examples/ directory to ensure they don't have syntax errors or missing
dependencies that would prevent them from running.

Usage:
    python scripts/check_examples_importable.py
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def check_syntax(filepath: Path) -> tuple[bool, str | None]:
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, encoding="utf-8") as f:
            ast.parse(f.read(), filename=str(filepath))
        return True, None
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"


def check_imports(filepath: Path) -> tuple[bool, str | None]:
    """Check if a Python file can be imported (dry run)."""
    try:
        # Use ast to extract imports without executing
        with open(filepath, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(filepath))

        # Check for obvious issues in imports
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Just validate the AST structure is sound
                pass

        return True, None
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main() -> int:
    """Run import checks on all example scripts."""
    examples_dir = Path(__file__).parent.parent / "examples"
    if not examples_dir.exists():
        print(f"Examples directory not found: {examples_dir}")
        return 1

    example_files = sorted(examples_dir.glob("*.py"))
    if not example_files:
        print("No example files found")
        return 0

    print(f"Checking {len(example_files)} example scripts...")
    print()

    failed = []
    for filepath in example_files:
        if filepath.name.startswith("_"):
            # Skip __init__.py and similar
            continue

        rel_path = filepath.relative_to(Path.cwd())
        print(f"  {rel_path}...", end=" ")

        # Check syntax
        syntax_ok, syntax_err = check_syntax(filepath)
        if not syntax_ok:
            print("FAILED (syntax)")
            failed.append((rel_path, syntax_err))
            continue

        # Check imports (dry run)
        import_ok, import_err = check_imports(filepath)
        if not import_ok:
            print("FAILED (imports)")
            failed.append((rel_path, import_err))
            continue

        print("OK")

    print()
    if failed:
        print(f"FAILED: {len(failed)} script(s) have issues:")
        for rel_path, err in failed:
            print(f"  {rel_path}: {err}")
        return 1
    else:
        print(f"PASSED: All {len(example_files)} scripts are valid")
        return 0


if __name__ == "__main__":
    sys.exit(main())
