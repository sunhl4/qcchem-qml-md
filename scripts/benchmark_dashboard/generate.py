#!/usr/bin/env python3
"""Generate static HTML dashboard from L3 algorithm benchmark JSON.

Input is the JSON emitted by ``scripts/l3_algorithm_benchmark_report.py``::

    python scripts/l3_algorithm_benchmark_report.py --merged > /tmp/l3.json
    python scripts/benchmark_dashboard/generate.py --input /tmp/l3.json --output /tmp/l3.html

Stdin is supported when ``--input`` is omitted::

    python scripts/l3_algorithm_benchmark_report.py --merged | \\
        python scripts/benchmark_dashboard/generate.py --output /tmp/l3.html
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any


def load_report_json(*, input_path: Path | None) -> dict[str, Any]:
    raw = input_path.read_text(encoding="utf-8") if input_path is not None else sys.stdin.read()
    obj = json.loads(raw)
    if not isinstance(obj, dict):
        raise ValueError("L3 report root must be a JSON object")
    return obj


def _bundle_rows(report: dict[str, Any]) -> list[dict[str, Any]]:
    bundle = report.get("algorithm_benchmark_bundle_v1")
    if not isinstance(bundle, dict):
        return []
    rows_raw = bundle.get("rows")
    if not isinstance(rows_raw, list):
        return []
    return [r for r in rows_raw if isinstance(r, dict)]


def _merged_summary(report: dict[str, Any]) -> dict[str, Any] | None:
    merged = report.get("merged_experiment_benchmark_v1")
    return merged if isinstance(merged, dict) else None


def render_md_al_section(summary: dict[str, Any]) -> str:
    """Render HTML table + KPI line from ``md_validation_summary.json`` (C-10)."""
    rounds = summary.get("rounds") or []
    if not rounds:
        return ""
    kpi = summary.get("science_kpi_met")
    max_de = summary.get("max_abs_delta_hartree")
    threshold = summary.get("accuracy_threshold_hartree")
    lines = [
        "<h2>MD/ML active learning (UQC mock path)</h2>",
        '<p class="summary">'
        f"science_kpi_met={html.escape(str(kpi))} · "
        f"max|ΔE|={html.escape(_fmt_float(max_de))} Ha · "
        f"threshold={html.escape(_fmt_float(threshold))} Ha"
        "</p>",
        "<table><thead><tr>"
        "<th>round</th><th>n_train_after</th><th>max |ΔE| (Ha)</th><th>converged</th>"
        "</tr></thead><tbody>",
    ]
    for r in rounds:
        if not isinstance(r, dict):
            continue
        lines.append(
            "<tr>"
            f"<td>{html.escape(str(r.get('round_index', '')))}</td>"
            f"<td>{html.escape(str(r.get('n_train_after', '')))}</td>"
            f"<td>{html.escape(_fmt_float(r.get('max_abs_delta_hartree')))}</td>"
            f"<td>{html.escape(str(r.get('converged', '')))}</td>"
            "</tr>"
        )
    lines.append("</tbody></table>")
    return "\n".join(lines)


def render_html(report: dict[str, Any], *, md_summary: dict[str, Any] | None = None) -> str:
    rows = _bundle_rows(report)
    merged = _merged_summary(report)
    bundle = report.get("algorithm_benchmark_bundle_v1")
    schema = bundle.get("schema") if isinstance(bundle, dict) else None

    summary_bits: list[str] = []
    if schema:
        summary_bits.append(f"schema: {html.escape(str(schema))}")
    summary_bits.append(f"rows: {len(rows)}")
    if merged:
        summary_bits.append(f"n_configs: {merged.get('n_configs')}")
        tw = merged.get("total_wall_time_ms")
        if tw is not None:
            summary_bits.append(f"total_wall_time_ms: {float(tw):.1f}")

    thead = (
        "<tr>"
        "<th>experiment_id</th>"
        "<th>config</th>"
        "<th>algorithm</th>"
        "<th>scf (au)</th>"
        "<th>variational (au)</th>"
        "<th>nfev</th>"
        "<th>wall (ms)</th>"
        "</tr>"
    )
    body_rows: list[str] = []
    for row in rows:
        body_rows.append(
            "<tr>"
            f"<td>{html.escape(str(row.get('experiment_id', '')))}</td>"
            f"<td><code>{html.escape(str(row.get('config_rel', '')))}</code></td>"
            f"<td>{html.escape(str(row.get('quantum_algorithm_yaml', '')))}</td>"
            f"<td>{html.escape(_fmt_float(row.get('scf_energy_au')))}</td>"
            f"<td>{html.escape(_fmt_float(row.get('energy_after_variational_au')))}</td>"
            f"<td>{html.escape(str(row.get('nfev', '')))}</td>"
            f"<td>{html.escape(_fmt_float(row.get('wall_time_ms')))}</td>"
            "</tr>"
        )

    algo_section = ""
    if merged:
        algo_rows = merged.get("by_quantum_algorithm_yaml")
        if isinstance(algo_rows, list) and algo_rows:
            algo_lines = [
                "<h2>By quantum algorithm (YAML)</h2>",
                "<table><thead><tr>"
                "<th>algorithm</th><th>n_configs</th>"
                "<th>total wall (ms)</th><th>mean wall (ms)</th>"
                "</tr></thead><tbody>",
            ]
            for g in algo_rows:
                if not isinstance(g, dict):
                    continue
                algo_lines.append(
                    "<tr>"
                    f"<td>{html.escape(str(g.get('quantum_algorithm_yaml', '')))}</td>"
                    f"<td>{html.escape(str(g.get('n_configs', '')))}</td>"
                    f"<td>{html.escape(_fmt_float(g.get('total_wall_time_ms')))}</td>"
                    f"<td>{html.escape(_fmt_float(g.get('mean_wall_time_ms')))}</td>"
                    "</tr>"
                )
            algo_lines.append("</tbody></table>")
            algo_section = "\n".join(algo_lines)

    md_section = render_md_al_section(md_summary) if md_summary else ""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>L3 Algorithm Benchmark Dashboard</title>
  <style>
    body {{ font-family: system-ui, sans-serif; margin: 2rem; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
    th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; text-align: left; }}
    th {{ background: #f4f4f4; }}
    code {{ font-size: 0.9em; }}
    .summary {{ color: #444; }}
  </style>
</head>
<body>
  <h1>L3 Algorithm Benchmark</h1>
  <p class="summary">{" · ".join(summary_bits)}</p>
  <table>
    <thead>{thead}</thead>
    <tbody>
      {"".join(body_rows) if body_rows else '<tr><td colspan="7">No rows</td></tr>'}
    </tbody>
  </table>
  {algo_section}
  {md_section}
</body>
</html>
"""


def _fmt_float(value: Any) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.6g}"
    except (TypeError, ValueError):
        return str(value)


def main() -> None:
    ap = argparse.ArgumentParser(description="Render L3 benchmark JSON as static HTML.")
    ap.add_argument("--input", type=Path, help="L3 JSON file (default: stdin)")
    ap.add_argument(
        "--md-summary",
        type=Path,
        help="Optional md_validation_summary.json for MD/ML AL section (C-10)",
    )
    ap.add_argument("--output", type=Path, help="HTML output path (default: stdout)")
    args = ap.parse_args()

    if args.input is not None:
        raw = args.input.read_text(encoding="utf-8").strip()
        report = (
            json.loads(raw)
            if raw
            else {
                "algorithm_benchmark_bundle_v1": {
                    "schema": "algorithm_benchmark_bundle_v1",
                    "rows": [],
                }
            }
        )
        if not isinstance(report, dict):
            raise ValueError("L3 report root must be a JSON object")
    else:
        report = load_report_json(input_path=None)
    md_summary = None
    if args.md_summary is not None:
        md_summary = json.loads(args.md_summary.read_text(encoding="utf-8"))
    html_doc = render_html(report, md_summary=md_summary)
    if args.output:
        args.output.write_text(html_doc, encoding="utf-8")
    else:
        sys.stdout.write(html_doc)


if __name__ == "__main__":
    main()
