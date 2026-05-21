"""CLI demo: build Pauli protocol rows and print HQC-style cost estimate."""

from __future__ import annotations

import argparse

import numpy as np
from openfermion.ops import QubitOperator

from qchem_stack.backends.spec import BackendSpec, CompilerPassBundle, dataframe_circuit_shot
from qchem_stack.jobs.cost import CostEstimate
from qchem_stack.protocols.protocol import PauliAveragingProtocol


def main() -> None:
    ap = argparse.ArgumentParser(description="Pauli protocol resource rows (tabular dataframe).")
    ap.add_argument(
        "--pytket",
        action="store_true",
        help="If pytket is installed, add pytket_depth / pytket_twoq_count columns per compiled circuit.",
    )
    args = ap.parse_args()

    h = QubitOperator(((0, "Z"), (1, "Z")), 0.15) + QubitOperator((), 0.05)
    be = BackendSpec(name="sim", shots_per_circuit=512)
    p = PauliAveragingProtocol(
        hamiltonian=h,
        n_qubits=2,
        backend=be,
        pass_bundle=CompilerPassBundle(preoptimize_passes=["qubit_reuse_hint"]),
    )
    p.instantiate()
    p.build(np.zeros(8), hea_depth=2)
    p.compile()
    rows = p.dataframe_circuit_shot_rows()
    if args.pytket:
        from qchem_stack.backends.pytket_bridge import enrich_row_with_pytket

        rows = [enrich_row_with_pytket(p._compiled[i], dict(r)) for i, r in enumerate(rows)]
    print(dataframe_circuit_shot(rows).to_string(index=False))
    print("HQC proxy:", CostEstimate.from_resource_rows(rows))


if __name__ == "__main__":
    main()
