"""D4/D47: gap parity_matrix_anchor ↔ docs/inquanto_public_parity_matrix.md headings."""

from __future__ import annotations

import re
from pathlib import Path

from qchem_stack.protocols.inquanto_contract import inquanto_gap_categories

_ROOT = Path(__file__).resolve().parents[1]
_MATRIX = _ROOT / "docs" / "inquanto_public_parity_matrix.md"
_SECTION_HEADING = re.compile(r"^## (\d+)\.", re.MULTILINE)
_SECTION_REF = re.compile(r"§(\d+)(?:[–-](\d+))?")


def _matrix_section_numbers(text: str) -> set[int]:
    return {int(m.group(1)) for m in _SECTION_HEADING.finditer(text)}


def _section_nums_from_anchor(anchor: str) -> set[int]:
    out: set[int] = set()
    for m in _SECTION_REF.finditer(anchor):
        a = int(m.group(1))
        b = m.group(2)
        if b is None:
            out.add(a)
        else:
            hi = int(b)
            out.update(range(min(a, hi), max(a, hi) + 1))
    return out


def _require_docs_md_exists(rel: str) -> None:
    rel_path = rel.split("§", 1)[0].strip()
    p = (_ROOT / rel_path).resolve()
    assert p.is_file(), f"missing docs anchor path: {rel}"


def test_every_gap_has_matrix_anchor() -> None:
    for g in inquanto_gap_categories():
        assert g.get("parity_matrix_anchor"), f"gap {g.get('id')} missing parity_matrix_anchor"


def test_gap_anchors_reference_existing_docs_or_matrix_sections() -> None:
    matrix_text = _MATRIX.read_text(encoding="utf-8")
    sections = _matrix_section_numbers(matrix_text)
    assert sections, "expected ## N. headings in inquanto_public_parity_matrix.md"

    for g in inquanto_gap_categories():
        anchor = str(g["parity_matrix_anchor"])
        first_path = anchor.split(";")[0].strip()

        if first_path.startswith("docs/"):
            _require_docs_md_exists(first_path)
        elif "inquanto_public_parity_matrix.md" in anchor:
            nums = _section_nums_from_anchor(anchor)
            assert nums, f"gap {g['id']}: no §N in anchor {anchor!r}"
            missing = nums - sections
            assert not missing, f"gap {g['id']}: sections {missing} not in matrix headings"
