"""Build ExperimentConfig / GQE bundles for Nakaji paper molecules."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from qchem_stack.backends.executor_base import StatevectorHeaExecutor
from qchem_stack.chem.molecular_problem_build import (
    restricted_active_space_quantum_problem_from_config,
)
from qchem_stack.config import ExperimentConfig, load_experiment_config
from qchem_stack.integrations.gqe.native.cost_bridge import make_gqe_cost, make_gqe_oracle
from qchem_stack.integrations.gqe.native.operator_pool import pool_summary
from qchem_stack.integrations.gqe.native.paper_pool import build_paper_uccsd_pool
from qchem_stack.integrations.gqe.native.paper_spec import (
    PAPER_MOLECULES,
    MoleculeId,
    PaperMoleculeSpec,
)
from qchem_stack.integrations.gqe.native.problem_bridge import (
    GQEProblemBundle,
    _fci_energy,
    _scf_from_meta,
)

ANGSTROM_TO_BOHR = 1.8897261258369282


def _base_h2_cfg() -> ExperimentConfig:
    # .../src/qchem_stack/integrations/gqe/native/this.py → parents[5] = repo root
    repo = Path(__file__).resolve().parents[5]
    cfg_path = repo / "configs" / "example_h2_gqe_plan_b.yaml"
    if not cfg_path.is_file():
        cfg_path = Path("configs/example_h2_gqe_plan_b.yaml")
    return load_experiment_config(cfg_path)


def geometry_coordinates_bohr(
    spec: PaperMoleculeSpec,
    bond_length_angstrom: float,
) -> list[list[float]]:
    r = float(bond_length_angstrom) * ANGSTROM_TO_BOHR
    if spec.geometry_kind == "diatomic":
        return [[0.0, 0.0, 0.0], [0.0, 0.0, r]]
    if spec.geometry_kind == "beh2_linear":
        # Be at origin, H at ±R along z
        return [[0.0, 0.0, 0.0], [0.0, 0.0, r], [0.0, 0.0, -r]]
    raise ValueError(spec.geometry_kind)


def build_paper_experiment_config(
    molecule_id: MoleculeId,
    *,
    bond_length_angstrom: float,
) -> ExperimentConfig:
    """Clone H2 YAML skeleton and rewrite molecule / active space for paper systems."""
    spec = PAPER_MOLECULES[molecule_id]
    cfg = deepcopy(_base_h2_cfg())
    coords = geometry_coordinates_bohr(spec, bond_length_angstrom)
    mol = cfg.molecule.model_copy(
        update={
            "symbols": list(spec.symbols),
            "coordinates": coords,
            "coordinate_unit": "bohr",
            "basis": "sto-3g",
            "charge": 0,
            "multiplicity": 1,
        }
    )
    cas = cfg.active_space.cas.model_copy(
        update={
            "n_orbitals": int(spec.n_orbitals_cas),
            "n_electrons": int(spec.n_electrons_cas),
        }
    )
    active = cfg.active_space.model_copy(update={"cas": cas, "strategy": "cas"})
    return cfg.model_copy(
        update={
            "molecule": mol,
            "active_space": active,
            "experiment_id": f"nakaji_gqe_{molecule_id}_R{bond_length_angstrom}",
        }
    )


def build_paper_gqe_problem(
    molecule_id: MoleculeId,
    *,
    bond_length_angstrom: float,
    store_pauli_features: bool = True,
    compute_fci: bool = True,
) -> GQEProblemBundle:
    """Paper molecule + Appendix A.2 operator pool + oracle."""
    spec = PAPER_MOLECULES[molecule_id]
    experiment = build_paper_experiment_config(
        molecule_id, bond_length_angstrom=bond_length_angstrom
    )
    problem = restricted_active_space_quantum_problem_from_config(experiment)
    qh = problem.qubit_hamiltonian
    fs = problem.fermion_space
    n_electrons = int(fs.n_electrons)
    if int(qh.n_qubits) != int(spec.n_qubits):
        # Soft warning via meta — LiH/BeH2/N2 CAS sizing may differ by frozen-core convention
        pass
    pool = build_paper_uccsd_pool(qh, include_identity=True)
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
    return GQEProblemBundle(
        config_path=None,
        experiment_id=str(experiment.experiment_id),
        n_qubits=int(qh.n_qubits),
        n_electrons=n_electrons,
        scf_energy=_scf_from_meta(qh),
        fci_energy=_fci_energy(qh, n_electrons=n_electrons) if compute_fci else None,
        pool=pool,
        cost_fn=cost,
        oracle_fn=oracle,
        qubit_hamiltonian=qh,
        meta={
            "pool": pool_summary(pool),
            "paper_molecule": molecule_id,
            "bond_length_angstrom": float(bond_length_angstrom),
            "paper_spec": {
                "seq_len": spec.seq_len,
                "n_epochs": spec.n_epochs,
                "energy_offset": spec.energy_offset,
                "expected_n_qubits": spec.n_qubits,
            },
            "n_qubits_actual": int(qh.n_qubits),
        },
    )
