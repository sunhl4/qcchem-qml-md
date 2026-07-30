#!/usr/bin/env python3
"""Check tutorial pages have standardized verify + expected-output blocks.

Required headings (Chinese or English) on every runnable tutorial page:

  ## 验证命令   / ## Verify
  ## 期望输出   / ## Expected output

Index / overview pages listed in SKIP_IDS are exempt.

Also requires at least one fenced code block under the verify section.

Usage:
  python scripts/check_tutorial_verify_blocks.py
  python scripts/check_tutorial_verify_blocks.py --write-stub   # append stubs to missing pages
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TUTORIAL_DIR = ROOT / "docusaurus-site" / "docs" / "tutorial"

SKIP_IDS = {
    "index.md",
    "tutorial-index-three-paths.md",
    "verify-block-template.md",
}

VERIFY_HEADINGS = ("## 验证命令", "## Verify")
EXPECT_HEADINGS = ("## 期望输出", "## Expected output")

_FENCE_RE = re.compile(r"^```", re.MULTILINE)


def _section_after(text: str, headings: tuple[str, ...]) -> str | None:
    for h in headings:
        idx = text.find(h)
        if idx < 0:
            continue
        rest = text[idx + len(h) :]
        # next ## heading ends the section
        m = re.search(r"\n## ", rest)
        return rest if m is None else rest[: m.start()]
    return None


def _has_fence(section: str) -> bool:
    return bool(_FENCE_RE.search(section))


def _stub_block(*, verify_cmd: str, expected: list[str]) -> str:
    lines = [
        "",
        "## 验证命令",
        "",
        "```bash",
        verify_cmd,
        "```",
        "",
        "## 期望输出",
        "",
    ]
    for item in expected:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


# Sensible defaults when --write-stub is used on pages missing blocks.
_DEFAULT_STUBS: dict[str, tuple[str, list[str]]] = {
    "quickstart.md": (
        "python scripts/smoke_pipeline.py",
        [
            "进程退出码 `0`",
            "结果含 `pre_quantum_input.hamiltonian_fingerprint`",
            "`qchem-run --scenario minimal_vqe` 可替代烟测",
        ],
    ),
    "async-run-via-http.md": (
        'curl -sS "http://127.0.0.1:8000/v1/meta/product-surface" | head -c 200',
        [
            "API 返回 JSON（需先 `uvicorn qchem_stack.api.app:app`）",
            "异步 run 终态为 `DONE` / `FAILED`",
            "`/repro` 含 `run_summary`",
        ],
    ),
    "workflow.md": (
        "python scripts/smoke_pipeline.py --config configs/example_h2.yaml",
        ["退出码 `0`", "YAML 块 `molecule` / `quantum` / `backend` 可被加载"],
    ),
    "read-repro-keys.md": (
        "python scripts/check_parity_export_sample.py",
        ["退出码 `0`", "导出 JSON 含 `resource_estimation_preview_v1` 等契约键"],
    ),
    "switch-backend-compare.md": (
        "python scripts/smoke_pipeline.py --config configs/example_h2.yaml",
        ["退出码 `0`", "更换 `backend.provider` 后仍能完成管线"],
    ),
    "uccsd-trotter-export.md": (
        "python scripts/smoke_pipeline.py --config configs/example_h2_uccsd_trotter.yaml",
        ["退出码 `0`", "结果可导出 parity / circuit 相关字段"],
    ),
    "gqe-nakaji-h2.md": (
        "python examples/tutorial_gqe_h2_smoke.py",
        ["退出码 `0`", "写出 JSON 报告（若指定 `--out`）"],
    ),
    "zne-qiskit-repro.md": (
        "python scripts/smoke_pipeline.py --config configs/example_h2_zne_circuit_fold.yaml",
        ["退出码 `0`", "`repro` / run_summary 含 mitigation 相关键"],
    ),
    "projection-embedding-deep-dive.md": (
        "python scripts/smoke_pipeline.py --projection-trace",
        ["退出码 `0`", "projection 路径产出完整 pre-quantum / embedding 字段"],
    ),
    "case-study-h2-family.md": (
        "python scripts/smoke_pipeline.py",
        ["退出码 `0`", "H₂ 家族配置可按案例表逐项替换运行"],
    ),
    "casscf-audit-workflow.md": (
        "qchem-run configs/example_h2_casscf_audit.yaml",
        ["退出码 `0`", "审计相关 meta / repro 字段可检查"],
    ),
    "md-ml-active-learning.md": (
        "python -m pytest tests/test_p4_md_ml_kpi.py -q --no-cov -m l1_md_ml",
        ["测试通过（需 `jax_md`）", "或对照 `configs/example_h2_*_md.yaml` 跑 loop"],
    ),
    "decomposition-plugin-minimal.md": (
        "python -m pytest tests/chem/test_decomposition_plugin_pipeline.py -q --no-cov",
        ["测试通过", "parity export 对 toy 配置返回码 `0`"],
    ),
}


def check_file(path: Path, *, write_stub: bool) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    verify = _section_after(text, VERIFY_HEADINGS)
    expect = _section_after(text, EXPECT_HEADINGS)

    if verify is None or expect is None:
        if write_stub and path.name in _DEFAULT_STUBS:
            cmd, exp = _DEFAULT_STUBS[path.name]
            path.write_text(
                text.rstrip() + "\n" + _stub_block(verify_cmd=cmd, expected=exp), encoding="utf-8"
            )
            return []
        missing = []
        if verify is None:
            missing.append("验证命令/Verify")
        if expect is None:
            missing.append("期望输出/Expected output")
        errors.append(f"{path.relative_to(ROOT)}: missing section(s): {', '.join(missing)}")
        return errors

    if not _has_fence(verify):
        errors.append(f"{path.relative_to(ROOT)}: 验证命令 section needs a fenced code block")
    if not expect.strip():
        errors.append(f"{path.relative_to(ROOT)}: 期望输出 section is empty")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--write-stub",
        action="store_true",
        help="Append default verify/expected stubs to pages that lack them",
    )
    args = parser.parse_args()

    if not TUTORIAL_DIR.is_dir():
        print(f"missing {TUTORIAL_DIR}", file=sys.stderr)
        return 1

    errors: list[str] = []
    for path in sorted(TUTORIAL_DIR.glob("*.md")):
        if path.name in SKIP_IDS:
            continue
        errors.extend(check_file(path, write_stub=args.write_stub))

    if errors:
        print("Tutorial verify-block check failed:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        print(
            "hint: python scripts/check_tutorial_verify_blocks.py --write-stub",
            file=sys.stderr,
        )
        return 1

    print("tutorial verify-block check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
