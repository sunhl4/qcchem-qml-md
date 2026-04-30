from __future__ import annotations

from pathlib import Path


def write_mace_yaml_stub(path: str | Path, dataset_npz: str) -> None:
    p = Path(path)
    body = f"""# Stub MACE CLI config — replace with mace.tools.run_train arguments.
name: qchem_stack_stub
data_path: {dataset_npz}
"""
    p.write_text(body, encoding="utf-8")
