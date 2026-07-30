"""Build GQE problem inputs from ExperimentConfig without touching pipeline."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import numpy as np
from openfermion.linalg import get_sparse_operator
from scipy.sparse.linalg import eigsh

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.molecular_problem_build import (
    restricted_active_space_quantum_problem_from_config,
)
from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.integrations.gqe.native.cost_bridge import (
    GQECostFn,
    make_gqe_cost,
    make_gqe_oracle,
)
from qchem_stack.integrations.gqe.native.operator_pool import (
    GQEOperatorPool,
    build_gqe_operator_pool,
    pool_summary,
)
from qchem_stack.integrations.gqe.native.pauli_features import (
    hamiltonian_coefficients,
    pauli_basis_from_hamiltonian,
)


@dataclass(frozen=True)
class GQEProblemBundle:
    """Hamiltonian + HF reference + pool + cost callable for native GQE."""

    config_path: str | None
    experiment_id: str
    n_qubits: int
    n_electrons: int
    scf_energy: float | None
    fci_energy: float | None
    pool: GQEOperatorPool
    cost_fn: GQECostFn
    oracle_fn: Any
    qubit_hamiltonian: Any
    meta: dict[str, Any]


def _fci_energy(qh: Any, *, n_electrons: int) -> float | None:
    """Exact diagonalization of active-space qubit H (small systems only)."""
    n = int(qh.n_qubits)
    if n > 12:
        return None
    try:
        mat = get_sparse_operator(qh.operator, n_qubits=n)
        # Prefer particle-number sector via dense eig if tiny; else eigsh
        if mat.shape[0] <= 256:
            vals = np.linalg.eigvalsh(mat.toarray())
            return float(np.min(np.real(vals)))
        vals = eigsh(mat, k=1, which="SA", return_eigenvectors=False)
        return float(np.real(vals[0]))
    except Exception:
        return None


def _scf_from_meta(qh: Any) -> float | None:
    if not isinstance(qh.meta, dict):
        return None
    for key in (
        "scf_energy_au",
        "reference_energy_au",
        "scf_energy",
        "reference_energy",
        "hf_energy",
    ):
        if key in qh.meta and qh.meta[key] is not None:
            return float(qh.meta[key])
    return None


def build_gqe_problem_from_config(
    cfg: ExperimentConfig | str | Path,
    *,
    pool_id: str = "fermionic_uccsd",
    default_angle: float = 0.1,
    angle_grid: tuple[float, ...] | None = None,
    include_identity: bool = True,
    cfg_path: str | Path | None = None,
    store_pauli_features: bool = True,
    compute_fci: bool = True,
) -> GQEProblemBundle:
    """Resolve active-space H and UCCSD pool via chem APIs (additive; no pipeline)."""
    path: str | None
    if isinstance(cfg, (str, Path)):
        path = str(cfg)
        experiment = load_experiment_config(cfg)
    else:
        path = str(cfg_path) if cfg_path is not None else None
        experiment = cfg

    problem = restricted_active_space_quantum_problem_from_config(experiment)
    qh = problem.qubit_hamiltonian
    fs = problem.fermion_space
    n_electrons = int(fs.n_electrons)
    pool = build_gqe_operator_pool(
        qh,
        pool_id=pool_id,
        default_angle=float(default_angle),
        angle_grid=angle_grid,
        include_identity=include_identity,
    )
    exe = StatevectorHeaExecutor()
    cost = make_gqe_cost(
        exe,
        qh.operator,
        pool,
        reference=problem.hartree_fock_state_jw,
        n_electrons=n_electrons,
    )
    oracle = make_gqe_oracle(
        exe,
        qh.operator,
        pool,
        reference=problem.hartree_fock_state_jw,
        n_electrons=n_electrons,
        store_pauli_features=store_pauli_features,
    )
    scf_e = _scf_from_meta(qh)
    fci_e = _fci_energy(qh, n_electrons=n_electrons) if compute_fci else None

    return GQEProblemBundle(
        config_path=path,
        experiment_id=str(getattr(experiment, "experiment_id", "unknown")),
        n_qubits=int(qh.n_qubits),
        n_electrons=n_electrons,
        scf_energy=scf_e,
        fci_energy=fci_e,
        pool=pool,
        cost_fn=cost,
        oracle_fn=oracle,
        qubit_hamiltonian=qh,
        meta={
            "pool": pool_summary(pool),
            "problem_schema": problem.meta.get("schema"),
            "fermion_qubit_mapping": problem.meta.get(
                "fermion_qubit_mapping_used_for_qubit_hamiltonian"
            ),
            "hamiltonian_meta_keys": sorted(qh.meta.keys()) if isinstance(qh.meta, dict) else [],
            "store_pauli_features": bool(store_pauli_features),
        },
    )


def build_gqe_problems_bond_scan(
    base_cfg: ExperimentConfig | str | Path,
    *,
    bond_lengths_bohr: list[float],
    pool_id: str = "fermionic_uccsd",
    default_angle: float = 0.1,
    angle_grid: tuple[float, ...] | None = None,
    include_identity: bool = True,
    store_pauli_features: bool = True,
) -> list[GQEProblemBundle]:
    """Build GQE problems for H2-like diatomics at multiple bond lengths (bohr).

    Assumes molecule has two atoms along z with the second atom at ``[0,0,R]``.
    """
    if isinstance(base_cfg, (str, Path)):
        experiment = load_experiment_config(base_cfg)
        base_path = str(base_cfg)
    else:
        experiment = base_cfg
        base_path = None

    out: list[GQEProblemBundle] = []
    for r in bond_lengths_bohr:
        cfg = deepcopy(experiment)
        # pydantic model: mutate coordinates
        coords = [[0.0, 0.0, 0.0], [0.0, 0.0, float(r)]]
        mol = cfg.molecule.model_copy(update={"coordinates": coords, "coordinate_unit": "bohr"})
        cfg = cfg.model_copy(update={"molecule": mol, "experiment_id": f"{cfg.experiment_id}_R{r}"})
        bundle = build_gqe_problem_from_config(
            cfg,
            pool_id=pool_id,
            default_angle=default_angle,
            angle_grid=angle_grid,
            include_identity=include_identity,
            cfg_path=base_path,
            store_pauli_features=store_pauli_features,
        )
        out.append(
            replace(
                bundle,
                meta={**bundle.meta, "bond_length_bohr": float(r)},
            )
        )
    return out


def transfer_dataset_to_bundle(
    records: list[dict[str, Any]],
    target: GQEProblemBundle,
) -> list[dict[str, Any]]:
    """Coefficient-reweight oracle records onto ``target`` Hamiltonian."""
    from qchem_stack.integrations.gqe.native.pauli_features import reweight_dataset_energies

    basis = pauli_basis_from_hamiltonian(target.qubit_hamiltonian.operator)
    identity, h = hamiltonian_coefficients(target.qubit_hamiltonian.operator, basis)
    # Align feature labels if needed: require same Pauli basis order
    if records and "pauli_features" in records[0]:
        src_labels = records[0]["pauli_features"].get("labels")
        if src_labels is not None and list(src_labels) != list(basis.labels):
            raise ValueError(
                "Pauli basis mismatch between source dataset and target Hamiltonian; "
                "use a shared operator pool / active space."
            )
    return reweight_dataset_energies(records, identity_coeff=identity, h_coeffs=h)
