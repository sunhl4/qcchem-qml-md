"""
Aggregate **open gap-closure references** (UCC policies, TKET optimize, Nexus blueprint, Qermit overlays, TN API, DMET toy recipe, L3 stub, driver matrix).

Merged into ``repro.parity_snapshot`` when :attr:`~qchem_stack.config.ParityIntegrationsSpec.gap_closure_reference_bundle` is True.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.backends.spec import CircuitIR
from qchem_stack.chem.kernels.spin_ucc import (
    GreedyCommutingFermionicLayers,
    SinglesBeforeDoublesLexicographic,
    build_spin_uccsd_fermion_generators,
)
from qchem_stack.config.active_space_helpers import resolve_n_electrons, resolve_n_orbitals
from qchem_stack.contracts.schema_ids import OPEN_GAP_CLOSURE_REFERENCE_V1
from qchem_stack.integrations.l3_statistics_reference import energy_bootstrap_ci_stub
from qchem_stack.integrations.nexus_optional import nexus_public_workflow_blueprint
from qchem_stack.integrations.open_driver_surface import open_driver_coverage_matrix
from qchem_stack.integrations.qermit_reference import qermit_mitigation_execution_overlays
from qchem_stack.integrations.tket_fullchain import circuit_ir_tket_peephole_optimize_stats_or_none
from qchem_stack.mitigation.qermit_analog import build_qermit_style_mitigation_report
from qchem_stack.tensornet.dense_expectation_reference import dense_expectation_api_descriptor

if TYPE_CHECKING:
    from qchem_stack.config import ExperimentConfig


def build_open_gap_closure_reference(cfg: ExperimentConfig) -> dict[str, Any]:
    """
    Single JSON blob listing **open-stack** counterparts to closed product areas.

    Epistemic bound: **L1 / engineered reference**, never L0 binary equivalence to closed vendor stacks or Nexus.
    """
    n_so = 2 * resolve_n_orbitals(cfg.active_space)
    ne = resolve_n_electrons(cfg.active_space)
    base_gens = build_spin_uccsd_fermion_generators(n_so, ne)
    layers_greedy = GreedyCommutingFermionicLayers().regroup_into_layers(base_gens)
    gens_sbd = SinglesBeforeDoublesLexicographic().regroup_generators(base_gens)

    probe_ir = CircuitIR(
        n_qubits=2,
        operations=[
            {"name": "H", "qubits": [0], "params": {}},
            {"name": "CX", "qubits": [0, 1], "params": {}},
        ],
    )
    tket_opt = circuit_ir_tket_peephole_optimize_stats_or_none(probe_ir)

    mit = build_qermit_style_mitigation_report(cfg)

    return {
        "schema": OPEN_GAP_CLOSURE_REFERENCE_V1,
        "epistemic_binding": (
            "Synthetic closure of publicly-documented *contract* gaps using peer-reviewable "
            "or explicitly labeled toy methods. Not Quantinuum closed binaries."
        ),
        "ucc": {
            "module": "qchem_stack.chem.kernels.spin_ucc",
            "chemically_aware_ucc_policy_protocol": "qchem_stack.chem.kernels.spin_ucc.ChemicallyAwareUCCPolicy",
            "build_spin_uccsd_fermion_generators_policy_param": (
                "Optional ``policy: ChemicallyAwareUCCPolicy``; default ``IdentityRegrouping`` when omitted."
            ),
            "active_space_generators_count": len(base_gens),
            "n_greedy_commuting_trotter_layers": len(layers_greedy),
            "singles_before_doubles_reorders": gens_sbd != base_gens,
            "policies_implemented": [
                "IdentityRegrouping",
                "SinglesBeforeDoublesLexicographic",
                "GreedyCommutingFermionicLayers",
            ],
        },
        "tket": {
            "peephole_optimise_probe_on_demo_ir": tket_opt,
            "note": "Ion-trap routing / vendor pass packages still out of scope; pytket local passes only.",
        },
        "nexus": nexus_public_workflow_blueprint(),
        "qermit": {
            "capability_matrix_row_ref": "integrations/qermit_reference.py",
            "execution_overlays": qermit_mitigation_execution_overlays(cfg),
            "sequential_mitigation_report_if_enabled": mit,
        },
        "tensornet": dense_expectation_api_descriptor(),
        "dmet": {
            "uniform_multifragment_toy": (
                "qchem_stack.integrations.dmet_multifragment_toy.run_uniform_hamiltonian_multifragment_toy"
            ),
            "note": "Bath DMET remains user-supplied; toy proves multi-fragment loop execution only.",
        },
        "l3_statistics": energy_bootstrap_ci_stub([-1.0, -1.02, -0.99], seed=cfg.random_seed),
        "driver_surface": open_driver_coverage_matrix(),
    }
