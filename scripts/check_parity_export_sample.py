#!/usr/bin/env python3
"""Smoke-check parity export JSON (config-only) for L1 regression.

Runs ``export_parity_criteria_table`` (config-only) on **every** ``configs/*.yaml``
that validates as :class:`~qchem_stack.config.ExperimentConfig` (``schema_version: 2``
with a ``molecule`` block). Also loads MD validation-loop YAMLs (``max_rounds`` +
``force_field_backend``) via :class:`~qchem_stack.md_bridge.md_loop_config.MdValidationLoopConfig`.

Does not require PySCF or a pipeline results file.

When adding a new **experiment** YAML under ``configs/``, it is picked up automatically;
no manual ``SAMPLE_CONFIGS_REL`` edit is required.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import yaml


def _discover_experiment_config_paths(configs_dir: Path) -> tuple[str, ...]:
    """All ``configs/*.yaml`` files that are ExperimentConfig-shaped (schema v2 + molecule)."""
    rels: list[str] = []
    for path in sorted(configs_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if (
            isinstance(raw, dict)
            and raw.get("schema_version") == "2"
            and isinstance(raw.get("molecule"), dict)
        ):
            rels.append(f"configs/{path.name}")
    return tuple(rels)


def _discover_md_loop_config_paths(configs_dir: Path) -> tuple[str, ...]:
    """All ``configs/*.yaml`` files that are MdValidationLoopConfig-shaped."""
    rels: list[str] = []
    for path in sorted(configs_dir.glob("*.yaml")):
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if (
            isinstance(raw, dict)
            and "max_rounds" in raw
            and "force_field_backend" in raw
            and "molecule" not in raw
        ):
            rels.append(f"configs/{path.name}")
    return tuple(rels)


# Backward-compatible alias: full auto-discovered experiment config list at import time.
# Tests and docs may reference this name; it is rebuilt from disk on each import.
_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_CONFIGS_REL = _discover_experiment_config_paths(_ROOT / "configs")
MD_LOOP_CONFIGS_REL = _discover_md_loop_config_paths(_ROOT / "configs")


def _run_export(root: Path, cfg_rel: str, env: dict[str, str]) -> tuple[int, dict]:
    script = root / "scripts" / "export_parity_criteria_table.py"
    proc = subprocess.run(
        [sys.executable, str(script), str(root / cfg_rel)],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    if proc.returncode != 0:
        return proc.returncode or 1, {}
    return 0, json.loads(proc.stdout)


def _sample_configs_unique_or_raise(samples: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    deduped: list[str] = []
    duplicated: list[str] = []
    for cfg in samples:
        if cfg in seen:
            duplicated.append(cfg)
            continue
        seen.add(cfg)
        deduped.append(cfg)
    if duplicated:
        d = ", ".join(sorted(set(duplicated)))
        raise ValueError(f"config list has duplicated entries: {d}")
    return tuple(deduped)


def _register_parity_export_solvers() -> None:
    from scripts.parity_export_solvers import register_parity_export_solvers

    register_parity_export_solvers()


# Backward-compatible alias for tests/docs.
_register_template_solvers_for_export = _register_parity_export_solvers


def _check_md_loop_configs(root: Path) -> int:
    from qchem_stack.md_bridge.md_loop_config import MdValidationLoopConfig

    md_samples = _sample_configs_unique_or_raise(MD_LOOP_CONFIGS_REL)
    for cfg_rel in md_samples:
        path = root / cfg_rel
        try:
            MdValidationLoopConfig.from_yaml(path)
        except Exception as exc:
            sys.stderr.write(f"md loop config failed for {cfg_rel}: {exc}\n")
            return 1
    return 0


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    src = root / "src"
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    from qchem_stack.protocols.product_contract import PARITY_EXPORT_V3_STABLE_KEYS

    _register_parity_export_solvers()

    env = {**os.environ, "PYTHONPATH": f"{src}" + os.pathsep + os.environ.get("PYTHONPATH", "")}
    try:
        samples = _sample_configs_unique_or_raise(SAMPLE_CONFIGS_REL)
    except ValueError as e:
        sys.stderr.write(str(e) + "\n")
        return 1
    if not samples:
        sys.stderr.write("no experiment configs discovered under configs/\n")
        return 1
    for cfg_rel in samples:
        code, data = _run_export(root, cfg_rel, env)
        if code != 0:
            sys.stderr.write(f"export failed for {cfg_rel}\n")
            return code
        missing = sorted(PARITY_EXPORT_V3_STABLE_KEYS - set(data.keys()))
        if missing:
            sys.stderr.write(f"{cfg_rel}: export missing stable keys: {missing}\n")
            return 1
        if data.get("parity_export_schema_version") != "3":
            sys.stderr.write(f"{cfg_rel}: unexpected parity_export_schema_version\n")
            return 1
        gaps = data.get("capability_gap_categories")
        if not isinstance(gaps, list) or not gaps:
            sys.stderr.write(f"{cfg_rel}: capability_gap_categories empty\n")
            return 1
        for g in gaps:
            if not isinstance(g, dict) or not g.get("release_anchor"):
                sys.stderr.write(f"{cfg_rel}: gap row missing release_anchor\n")
                return 1
    return _check_md_loop_configs(root)


if __name__ == "__main__":
    raise SystemExit(main())
