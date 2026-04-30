from __future__ import annotations

from pathlib import Path


def write_nequip_yaml_stub(path: str | Path, dataset_npz: str) -> None:
    """Emit a minimal NequIP-compatible training YAML pointing at NPZ frames."""
    p = Path(path)
    body = f"""# Stub NequIP config — replace with official template for your NequIP version.
run_name: qchem_stack_stub
dataset_config:
  npz_path: {dataset_npz}
network:
  model: NequIP
"""
    p.write_text(body, encoding="utf-8")
