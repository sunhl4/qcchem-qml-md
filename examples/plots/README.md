# Example plot outputs

PNG figures in this directory are produced by:

```bash
cd /path/to/repo
export PYTHONPATH=src
python examples/render_example_plots.py
```

Requires **PySCF** (`pip install qchem-stack[chem]`) and **matplotlib** (`pip install matplotlib` or `pip install "qchem-stack[examples_viz]"` from repo root).

Regenerate after changing `configs/example_*.yaml` or pipeline chemistry so plots stay in sync.
