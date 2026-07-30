"""Public blueprint for the additive GQE integration (no private API)."""

from __future__ import annotations

from typing import Any

from qchem_stack.contracts.schema_ids import GQE_BLUEPRINT_V1


def gqe_integration_blueprint() -> dict[str, Any]:
    """Describe Plan-B layout: native JAX core + optional cudaq probe."""
    return {
        "schema": GQE_BLUEPRINT_V1,
        "plan": "B",
        "summary": (
            "Native GQE core inside qchem_stack.integrations.gqe; "
            "energy oracle via HamiltonianExpectationExecutor; "
            "generative model via optional JAX/optax extra."
        ),
        "stages": [
            {"id": "operator_pool", "description": "Build token pool from chem/UCCSD registry"},
            {"id": "proposal", "description": "JAX transformer samples token sequences"},
            {"id": "oracle", "description": "Apply pool unitaries → executor.expectation_state"},
            {"id": "replay", "description": "Store (sequence, energy); mix into train batch"},
            {
                "id": "update",
                "description": "Train generative params (loss_mode=lm|grpo) on classical side only",
            },
            {
                "id": "paper_repro",
                "description": (
                    "Nakaji arXiv:2401.09253 path: paper_uccsd pool, "
                    "dispersion β, LM Eq.6 / GRPO Eq.9, FIFO buffer "
                    "(examples/gqe_nakaji_paper_repro.py)"
                ),
            },
            {
                "id": "train_modes",
                "description": (
                    "gqe.train_mode: gpt (warmup+GPT), prefill (warmup-only N≈200), "
                    "condition (instance-conditioned GPT; chemistry v1)"
                ),
            },
        ],
        "modules": {
            "probe_jax": "qchem_stack.integrations.gqe.probe_jax",
            "probe_cudaq": "qchem_stack.integrations.gqe.probe_cudaq",
            "native": "qchem_stack.integrations.gqe.native",
            "problem_bridge": "qchem_stack.integrations.gqe.native.problem_bridge",
            "paper_spec": "qchem_stack.integrations.gqe.native.paper_spec",
            "paper_trainer": "qchem_stack.integrations.gqe.native.paper_trainer",
            "conditional_trainer": "qchem_stack.integrations.gqe.native.conditional_trainer",
            "cudaq_adapter": "qchem_stack.integrations.gqe.cudaq_adapter (optional PoC)",
            "demo": "examples/gqe_h2_plan_b_demo.py",
            "paper_repro": "examples/gqe_nakaji_paper_repro.py",
            "train_modes": "examples/tutorial_gqe_train_modes.py",
        },
        "product_entry": "qchem_stack.integrations.gqe.api.run_gqe_from_config",
        "yaml_block": "gqe (top-level ExperimentConfig; not quantum.algorithm)",
        "non_goals": [
            "Do not register GQE as quantum.algorithm / variational_plugins (JAX stays optional)",
            "Do not place JAX transformer under quantum/algorithms (import boundary)",
            "Do not add torch/cuda-quantum to core dependencies",
            "ibm_kawasaki hardware run (paper §3.3) requires external QPU access",
            "Full Conditional-GQE GNN+DPO combinatorial solver (DOI:10.1039/D5DD00138B) — chemistry v1 only",
            "Nakaji §3.2 N2 75k pretrain mix decay — trainer hooks exist, not fully wired via YAML",
        ],
    }
