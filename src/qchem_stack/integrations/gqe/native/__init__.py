"""Native GQE core (Plan B): pool → cost → JAX LM/GRPO trainer.

Prefer the stable package entry :func:`qchem_stack.integrations.gqe.run_gqe_from_config`
for applications; this submodule exports lower-level pool/trainer primitives.
"""

from __future__ import annotations

from qchem_stack.integrations.gqe.native.cost_bridge import (
    GQECostFn,
    apply_pool_sequence,
    make_gqe_cost,
    make_gqe_oracle,
)
from qchem_stack.integrations.gqe.native.operator_pool import (
    GQEOperatorPool,
    build_gqe_operator_pool,
)
from qchem_stack.integrations.gqe.native.paper_molecules import build_paper_gqe_problem
from qchem_stack.integrations.gqe.native.paper_pool import build_paper_uccsd_pool
from qchem_stack.integrations.gqe.native.paper_spec import (
    paper_reproduction_checklist,
)
from qchem_stack.integrations.gqe.native.paper_trainer import (
    PaperTrainConfig,
    run_paper_gqe_loop,
)
from qchem_stack.integrations.gqe.native.pauli_features import (
    reweight_dataset_energies,
)
from qchem_stack.integrations.gqe.native.problem_bridge import (
    GQEProblemBundle,
    build_gqe_problem_from_config,
    build_gqe_problems_bond_scan,
    transfer_dataset_to_bundle,
)
from qchem_stack.integrations.gqe.native.schedules import (
    CHEMICAL_ACCURACY_HARTREE,
    BetaSchedule,
    chemical_accuracy_report,
)
from qchem_stack.integrations.gqe.native.trainer import (
    GQETrainConfig,
    run_gqe_lm_loop,
    run_random_baseline,
)

__all__ = [
    "CHEMICAL_ACCURACY_HARTREE",
    "BetaSchedule",
    "GQECostFn",
    "GQEOperatorPool",
    "GQEProblemBundle",
    "GQETrainConfig",
    "PaperTrainConfig",
    "apply_pool_sequence",
    "build_gqe_operator_pool",
    "build_gqe_problem_from_config",
    "build_gqe_problems_bond_scan",
    "build_paper_gqe_problem",
    "build_paper_uccsd_pool",
    "chemical_accuracy_report",
    "make_gqe_cost",
    "make_gqe_oracle",
    "paper_reproduction_checklist",
    "reweight_dataset_energies",
    "run_gqe_lm_loop",
    "run_paper_gqe_loop",
    "run_random_baseline",
    "transfer_dataset_to_bundle",
]
