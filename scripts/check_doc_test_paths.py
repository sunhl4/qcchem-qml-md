#!/usr/bin/env python3
"""Fail when Tier-1 docs reference flat ``tests/test_*.py`` paths that no longer exist."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Tier 1 paths from docs/engineering/doc_tier_policy.md (relative to docs/).
TIER1_DOC_PREFIXES = (
    "ENGINEERING_ARCHITECTURE.md",
    "说明_config模块技术参考手册.md",
    "public_parity_matrix.md",
    "QUICKSTART_CONTRIBUTORS.md",
)

TIER1_ROOT_FILES = ("CONTRIBUTING.md",)

TIER1_DOC_DIRS = ("docusaurus-site/docs",)

# Tier 2 archive — warn only.
TIER2_ARCHIVE_MARKERS = ("execution/archive/",)

FLAT_TEST_RE = re.compile(r"tests/test_[a-z0-9_]+\.py")

# Manual overrides when multiple layer copies exist (prefer integration/orchestration).
PREFERRED_LAYER_PATHS: dict[str, str] = {
    "tests/test_run_build_cache.py": "tests/chem/test_run_build_cache.py",
    "tests/test_config_migration_strict.py": "tests/config/test_migrations.py",
    "tests/test_run_summary_key_registry.py": "tests/repro/test_repro_run_summary.py",
    "tests/test_api_health_ready_contract.py": "tests/api/test_api_runs.py",
    "tests/test_repro_includes_embedding_config_block.py": "tests/repro/test_repro_snapshot.py",
    "tests/test_gap_parity_matrix_anchors.py": "tests/api/test_api_runs.py",
    "tests/test_pyscf_driver_meta_contract.py": "tests/chem/test_pyscf_solver_adapter.py",
    "tests/test_job_flow.py": "tests/jobs/test_pipeline_job_store.py",
    "tests/test_psi4_full_pipeline_optional.py": "tests/chem/test_psi4_pre_quantum_pipeline.py",
    "tests/test_pyscf_driver_phase_b_interfaces.py": "tests/chem/test_pyscf_solver_adapter.py",
    "tests/test_mitigation_dag_trace_homology.py": "tests/mitigation/test_zne_fold.py",
}


def _is_tier1(rel: str) -> bool:
    if rel.startswith(TIER2_ARCHIVE_MARKERS):
        return False
    if rel in TIER1_ROOT_FILES:
        return True
    if rel.startswith("engineering/"):
        return True
    if rel.startswith("docusaurus-site/docs"):
        return True
    return any(rel == prefix or rel.endswith("/" + prefix) for prefix in TIER1_DOC_PREFIXES)


def _scan_files() -> list[Path]:
    paths: list[Path] = []
    for name in TIER1_ROOT_FILES:
        candidate = ROOT / name
        if candidate.is_file():
            paths.append(candidate)
    for root in (ROOT / "docs", ROOT / "docusaurus-site" / "docs"):
        if root.is_dir():
            paths.extend(root.rglob("*.md"))
    return paths


def _flat_test_exists(ref: str) -> bool:
    return (ROOT / ref).is_file()


def _resolve_layer_path(flat_ref: str) -> str | None:
    if flat_ref in PREFERRED_LAYER_PATHS:
        preferred = PREFERRED_LAYER_PATHS[flat_ref]
        if (ROOT / preferred).is_file():
            return preferred
    name = Path(flat_ref).name
    matches = sorted(ROOT.glob(f"tests/**/{name}"))
    matches = [m for m in matches if m.is_file()]
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0].relative_to(ROOT).as_posix()
    rels = [m.relative_to(ROOT).as_posix() for m in matches]
    return sorted(rels)[0]


def collect_violations() -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    for path in _scan_files():
        rel = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in FLAT_TEST_RE.finditer(text):
            ref = match.group(0)
            if _flat_test_exists(ref):
                continue
            msg = f"{rel}: stale flat test path {ref!r}"
            if _is_tier1(rel):
                errors.append(msg)
            else:
                warnings.append(msg)
    return errors, warnings


def apply_fixes() -> int:
    changed = 0
    for path in _scan_files():
        text = path.read_text(encoding="utf-8", errors="replace")
        original = text

        def _replace(match: re.Match[str]) -> str:
            ref = match.group(0)
            if _flat_test_exists(ref):
                return ref
            resolved = _resolve_layer_path(ref)
            return resolved if resolved else ref

        text = FLAT_TEST_RE.sub(_replace, text)
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
            print(f"fixed {path.relative_to(ROOT)}")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Rewrite stale flat paths to tests/<layer>/test_*.py when uniquely resolved",
    )
    args = parser.parse_args()

    if args.fix:
        n = apply_fixes()
        print(f"doc_test_paths_fix files_changed={n}")

    errors, warnings = collect_violations()
    for w in warnings:
        print(f"WARN {w}", file=sys.stderr)
    if errors:
        print("Tier-1 stale flat test paths (use tests/<layer>/test_*.py):", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print(f"doc_test_paths_ok warnings={len(warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
