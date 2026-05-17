"""Generated markdown snippets for pre-quantum docs."""

from __future__ import annotations

import ast
from pathlib import Path

_SOURCE_DESCRIPTIONS: dict[str, str] = {
    "canonical_active_space_integral_pack": (
        "在线经典主路径：`ClassicalMeanFieldReference` → "
        "`CanonicalActiveSpaceIntegralPack` → `QubitHamiltonian`"
    ),
    "precomputed_bundle": "离线 bundle 直接提供 pre-quantum Hamiltonian",
    "embedding_plugin": (
        "`embedding.mode=plugin` 的 decomposition JSON / 外部 fragment payload"
    ),
    "projection_fragment_mulliken_mo": "PySCF Mulliken MO projection 分支",
    "schmidt_atomic_production": "Schmidt impurity Hamiltonian 分支",
}


def _pre_quantum_path_source_values() -> tuple[str, ...]:
    path = Path(__file__).resolve().parent / "pre_quantum_path.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    class_node = None
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == "PreQuantumPath":
            class_node = node
            break
    if class_node is None:
        raise ValueError("PreQuantumPath class not found in pre_quantum_path.py")
    values: list[str] = []
    for node in class_node.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            value = node.value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                values.append(value.value)
    if not values:
        raise ValueError("No PreQuantumPath enum values found in pre_quantum_path.py")
    return tuple(values)


def generated_pre_quantum_source_table_markdown() -> str:
    """Generate markdown table for pre-quantum source→path descriptions."""
    lines = [
        "| source | 路径 |",
        "|---|---|",
    ]
    for source in _pre_quantum_path_source_values():
        desc = _SOURCE_DESCRIPTIONS.get(source)
        if desc is None:
            raise ValueError(f"Missing source description mapping for pre-quantum path {source!r}")
        lines.append(f"| `{source}` | {desc} |")
    return "\n".join(lines)


def generated_pre_quantum_path_registry_markdown() -> str:
    """Generate markdown bullet list for path registry snapshots."""
    lines = [
        "- `PreQuantumPath` 枚举值（稳定顺序）：",
    ]
    for source in _pre_quantum_path_source_values():
        lines.append(f"  - `{source}`")
    return "\n".join(lines)

