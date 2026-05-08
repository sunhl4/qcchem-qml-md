# Competitive positioning & roadmap

::: tip Product vs. public-doc map
**qchem-stack** is positioned as a **standalone competitive open orchestration product** (auditable, multi-backend, publication-ready Methods). `/mirror/` maps **published** Quantinuum documentation structure for gap tracking only — not closed-source InQuanto or Nexus/H-Series parity. Long-form analysis lives under `PandM/.../literature/` and `docs/architecture-report-quantinuum-inquanto-web/` in the repo, **outside** this site’s page tree.
:::

The authoritative narrative lives on the Chinese page ([`/concept/competitive-positioning`](/concept/competitive-positioning)): Quantinuum product landscape, our differentiable positioning (forkability, `parity_snapshot` / reproducibility exports, MD·ML surface), explicit non-goals, and staged engineering targets aligned with the parity matrix.

## Classical chemistry drivers (PySCF today, multi-backend contract)

Aligned with the Chinese hub [§5.1](/concept/competitive-positioning) (“经典化学驱动”):

- **Baseline:** End-to-end numerics and CI examples default to **`scf.driver=pyscf`** (restricted active space → qubit Hamiltonian, CASCI-class main path, most embedding branches).
- **Contract:** `ChemIntegralSolver` / `create_solver` → `ClassicalMeanFieldReference` (`upstream_classical_software_tag`); active-space metadata **`chem.active_space.mean_field_meta`**; post-HF benchmarks **`chem.classical_benchmarks`** — decoupled from any single program’s Python class names.
- **Extensibility:** Register adapters in **`chem/solvers/registry.py`** and set **`SolverCapabilities`** (especially **`supports_restricted_active_space_qubit_hamiltonian`**). **Psi4** can run **`compute_mean_field`** and return **RHF total energy** when installed (energy-only mean-field); it still does **not** provide the default active-space Hamiltonian path (`supports_restricted_active_space_qubit_hamiltonian=False`) and is **not** claimed numerically equivalent to the PySCF main line.
- **Docs (repo root):** [Roadmap §5.1 (ZH)](../../../../docs/竞争定位与路线图_对标Quantinuum产品与技术路线.md) · [ENGINEERING_ARCHITECTURE §1.1](../../../../docs/ENGINEERING_ARCHITECTURE.md#11-architecture-invariant-pinned) · [Public parity matrix §3](/en/parity/public-matrix).
