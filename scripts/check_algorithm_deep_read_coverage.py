#!/usr/bin/env python3
"""Ensure registered quantum algorithms/ansatz/excited IDs are covered by deep-read docs.

Mapping lives in ALGORITHM_DOC_MAP below — update when adding registry entries or pages.

Exit 0 if coverage is complete; exit 1 listing gaps.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALG_DIR = ROOT / "docusaurus-site" / "docs" / "modules" / "quantum" / "algorithms"

# algorithm_id -> relative markdown under algorithms/ (may share a page)
ALGORITHM_DOC_MAP: dict[str, str] = {
    "vqe": "vqe-hea.md",
    "adapt": "adapt-vqe.md",
    "iqeb": "iqeb.md",
    "iqcc": "iqcc.md",
    "sa_vqe": "sa-vqe.md",
    "tetris_adapt": "research-ansatze.md",
    "qpe_deterministic": "qpe.md",
    "qpe_kitaev": "qpe.md",
    "qpe_info_theory": "qpe.md",
}

ANSATZ_DOC_MAP: dict[str, str] = {
    "hea": "vqe-hea.md",
    "uccsd": "uccsd.md",
    "uccgd": "uccgd.md",
    "qcc": "qcc-paired.md",
    "upccgsd": "qcc-paired.md",
    "puccd": "qcc-paired.md",
    "iqcc": "iqcc.md",
    "qite": "qite.md",
    "vsqs": "vsqs-ansatz.md",
    "fermionic_adapt": "adapt-vqe.md",
    "iqeb": "iqeb.md",
    "trotter_ucc_placeholder": "uccsd.md",
    "uccsd_closed_shell_reference": "uccsd.md",
}

EXCITED_DOC_MAP: dict[str, str] = {
    "vqd": "vqd.md",
    "qse": "qse.md",
    "sceom": "sceom.md",
}


def _gaps(ids: list[str], mapping: dict[str, str], label: str) -> list[str]:
    missing: list[str] = []
    for i in ids:
        rel = mapping.get(i)
        if rel is None:
            missing.append(f"{label}:{i} (no map entry)")
            continue
        path = ALG_DIR / rel
        if not path.is_file():
            missing.append(f"{label}:{i} -> missing file {rel}")
    return missing


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from qchem_stack.quantum.algorithm_registry import list_registered_algorithm_ids
    from qchem_stack.quantum.ansatz_registry import list_registered_ansatz_ids
    from qchem_stack.quantum.excited_plugins.registry import list_registered_excited_ids

    gaps = []
    gaps += _gaps(list(list_registered_algorithm_ids()), ALGORITHM_DOC_MAP, "algorithm")
    gaps += _gaps(list(list_registered_ansatz_ids()), ANSATZ_DOC_MAP, "ansatz")
    gaps += _gaps(list(list_registered_excited_ids()), EXCITED_DOC_MAP, "excited")

    # Extra mapped files that are stale (map points to missing) already caught.
    # Warn on orphan map keys not in registry (optional strictness):
    reg_a = set(list_registered_algorithm_ids())
    for k in ALGORITHM_DOC_MAP:
        if k not in reg_a:
            gaps.append(f"algorithm_map_orphan:{k}")

    if gaps:
        print("algorithm deep-read coverage gaps:")
        for g in gaps:
            print(" ", g)
        return 1
    print(
        "ok: algorithms",
        len(ALGORITHM_DOC_MAP),
        "ansatz",
        len(ANSATZ_DOC_MAP),
        "excited",
        len(EXCITED_DOC_MAP),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
