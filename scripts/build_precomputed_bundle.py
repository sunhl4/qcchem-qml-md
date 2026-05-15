#!/usr/bin/env python3
"""Build a ``classical_reference_bundle_v1`` JSON for offline-classical pipeline runs.

Typical usage:

1) Start from a decomposition-plugin JSON with Pauli terms.
2) Attach externally computed ``e_tot`` and ``mo_energy``.
3) Write a bundle consumable by ``scf.driver='precomputed'``.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return data


def _extract_terms_from_decomposition_payload(
    payload: dict[str, Any],
) -> tuple[int, list[dict[str, Any]], str]:
    schema = str(payload.get("schema") or "")
    if schema not in ("decomposition_plugin_toy_v1", "decomposition_plugin_contract_v1"):
        raise ValueError(f"Unsupported decomposition plugin schema: {schema!r}")
    frags = payload.get("fragments")
    if not isinstance(frags, dict) or not frags:
        raise ValueError("decomposition payload requires non-empty fragments.")
    primary = str(payload.get("primary_fragment_id") or "")
    if primary not in frags:
        raise ValueError("primary_fragment_id missing from fragments map.")
    block = frags[primary]
    if not isinstance(block, dict):
        raise ValueError("primary fragment block must be object.")
    n_qubits = int(block["n_qubits"])
    rows = block.get("pauli_coefficients")
    if not isinstance(rows, list) or not rows:
        raise ValueError("primary fragment pauli_coefficients must be non-empty list.")
    terms: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("pauli_coefficients rows must be objects.")
        label = str(row.get("label") or "").strip()
        coeff = float(row["coeff"])
        if not label:
            raise ValueError("pauli coefficient label must be non-empty.")
        terms.append({"label": label, "coeff": coeff})
    return n_qubits, terms, schema


def _parse_mo_energy(raw: str) -> list[float]:
    vals: list[float] = []
    for token in [x.strip() for x in raw.split(",")]:
        if not token:
            continue
        vals.append(float(token))
    if not vals:
        raise ValueError("--mo-energy must provide at least one numeric value.")
    return vals


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--decomposition-json", required=True, help="Input decomposition plugin JSON path."
    )
    p.add_argument("--output", required=True, help="Output bundle JSON path.")
    p.add_argument("--e-tot", type=float, required=True, help="Classical total energy (Hartree).")
    p.add_argument(
        "--mo-energy",
        required=True,
        help="Comma-separated MO energies, e.g. '-0.58,0.67'.",
    )
    p.add_argument(
        "--upstream-tag",
        default="external_dataset",
        help="driver_meta.upstream_classical_software_tag value (default: external_dataset).",
    )
    args = p.parse_args()

    dec_path = Path(args.decomposition_json).resolve()
    out_path = Path(args.output).resolve()
    payload = _read_json(dec_path)
    n_qubits, terms, source_schema = _extract_terms_from_decomposition_payload(payload)
    mo_energy = _parse_mo_energy(args.mo_energy)

    bundle = {
        "schema": "classical_reference_bundle_v1",
        "classical_reference": {
            "e_tot": float(args.e_tot),
            "mo_energy": mo_energy,
            "driver_meta": {
                "upstream_classical_software_tag": str(args.upstream_tag),
                "energy_accounting_model": "mf_e_tot_direct",
                "bundle_generator": "scripts/build_precomputed_bundle.py",
                "source_decomposition_schema": source_schema,
                "source_decomposition_json": str(dec_path),
            },
        },
        "pre_quantum_input": {
            "schema": "pre_quantum_input_v1",
            "meta": {"source": "offline_bundle_generator"},
            "qubit_hamiltonian": {
                "n_qubits": int(n_qubits),
                "meta": {"fermion_to_qubit_map": "jordan_wigner"},
                "terms": terms,
            },
        },
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[ok] wrote bundle: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
