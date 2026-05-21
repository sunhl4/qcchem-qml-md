#!/usr/bin/env python3
"""
Toy finite-system DMRG for an open-boundary spin-1/2 Heisenberg XXZ chain.

This file is an educational, numpy/scipy-only implementation adapted from the
MIT-licensed tutorial code by James R. Garrison and Ryan V. Mishmash
(`simple-dmrg`, https://github.com/simple-dmrg/simple-dmrg). It is intentionally
compact and omits production features (quantum numbers, MPO/MPS bookkeeping).

Suggested reading order alongside:
  - docs/tensor_network_qchem_self_study.md
"""

from __future__ import annotations

import argparse
from collections import namedtuple
from dataclasses import dataclass

import numpy as np
from scipy.sparse import csr_matrix, identity, kron
from scipy.sparse.linalg import eigsh

Block = namedtuple("Block", ["length", "basis_size", "operator_dict"])
EnlargedBlock = namedtuple("EnlargedBlock", ["length", "basis_size", "operator_dict"])

model_d = 2

Sz1 = np.array([[0.5, 0.0], [0.0, -0.5]], dtype=np.float64)
Sp1 = np.array([[0.0, 1.0], [0.0, 0.0]], dtype=np.float64)
H1 = np.zeros((2, 2), dtype=np.float64)


def _H2(
    Sz1_: np.ndarray, Sp1_: np.ndarray, Sz2_: np.ndarray, Sp2_: np.ndarray, j: float, jz: float
) -> csr_matrix:
    sm1 = Sp1_.T
    sm2 = Sp2_.T
    return (j / 2.0) * (kron(Sp1_, sm2, format="csr") + kron(sm1, Sp2_, format="csr")) + jz * kron(
        Sz1_, Sz2_, format="csr"
    )


initial_block = Block(
    length=1,
    basis_size=model_d,
    operator_dict={
        "H": csr_matrix(H1),
        "conn_Sz": csr_matrix(Sz1),
        "conn_Sp": csr_matrix(Sp1),
    },
)


def _is_valid_block(block: Block) -> bool:
    for op in block.operator_dict.values():
        if op.shape[0] != block.basis_size or op.shape[1] != block.basis_size:
            return False
    return True


_is_valid_enlarged_block = _is_valid_block


def _enlarge_block(block: Block, j: float, jz: float) -> EnlargedBlock:
    mblock = block.basis_size
    o = block.operator_dict
    enlarged_operator_dict = {
        "H": kron(o["H"], identity(model_d), format="csr")
        + kron(identity(mblock), H1, format="csr")
        + _H2(o["conn_Sz"], o["conn_Sp"], Sz1, Sp1, j=j, jz=jz),
        "conn_Sz": kron(identity(mblock), Sz1, format="csr"),
        "conn_Sp": kron(identity(mblock), Sp1, format="csr"),
    }
    return EnlargedBlock(
        length=block.length + 1,
        basis_size=block.basis_size * model_d,
        operator_dict=enlarged_operator_dict,
    )


def _rotate_and_truncate(op: csr_matrix, transformation_matrix: np.ndarray) -> csr_matrix:
    return transformation_matrix.conj().T @ (op @ transformation_matrix)


def _single_dmrg_step(sys: Block, env: Block, m: int, j: float, jz: float) -> tuple[Block, float]:
    assert _is_valid_block(sys)
    assert _is_valid_block(env)

    sys_enl = _enlarge_block(sys, j=j, jz=jz)
    env_enl = sys_enl if sys is env else _enlarge_block(env, j=j, jz=jz)
    assert _is_valid_enlarged_block(sys_enl)
    assert _is_valid_enlarged_block(env_enl)

    m_sys_enl = sys_enl.basis_size
    m_env_enl = env_enl.basis_size
    sys_enl_op = sys_enl.operator_dict
    env_enl_op = env_enl.operator_dict

    superblock_hamiltonian = (
        kron(sys_enl_op["H"], identity(m_env_enl), format="csr")
        + kron(identity(m_sys_enl), env_enl_op["H"], format="csr")
        + _H2(
            sys_enl_op["conn_Sz"],
            sys_enl_op["conn_Sp"],
            env_enl_op["conn_Sz"],
            env_enl_op["conn_Sp"],
            j=j,
            jz=jz,
        )
    )

    (energy,), psi0 = eigsh(superblock_hamiltonian, k=1, which="SA")
    psi0 = np.asarray(psi0).reshape([sys_enl.basis_size, -1], order="C")
    rho = psi0 @ psi0.conj().T

    evals, evecs = np.linalg.eigh(rho)
    order = np.argsort(evals)[::-1]
    evals = evals[order]
    evecs = evecs[:, order]

    my_m = int(min(evecs.shape[1], m))
    transformation_matrix = np.asfortranarray(evecs[:, :my_m])

    truncation_error = float(1.0 - np.sum(evals[:my_m]))
    new_operator_dict = {
        name: _rotate_and_truncate(op, transformation_matrix)
        for name, op in sys_enl.operator_dict.items()
    }

    newblock = Block(length=sys_enl.length, basis_size=my_m, operator_dict=new_operator_dict)
    return newblock, float(energy), truncation_error


def finite_system_dmrg(
    *,
    chain_length: int,
    m_warmup: int,
    m_sweep_list: list[int],
    j: float = 1.0,
    jz: float = 1.0,
    verbose: bool = False,
) -> tuple[float, dict[str, float]]:
    """
    Finite-system DMRG for even `chain_length` (open boundary), following the
    warm-up + sweep pattern from `simple-dmrg`.
    """
    if chain_length % 2 != 0:
        raise ValueError("chain_length must be even for this toy driver")

    block_disk: dict[tuple[str, int], Block] = {}
    block = initial_block
    block_disk["l", block.length] = block
    block_disk["r", block.length] = block

    last_trunc = 0.0
    while 2 * block.length < chain_length:
        if verbose:
            print(
                "warmup:",
                "=" * block.length + "**" + "-" * block.length,
                "L=",
                2 * block.length + 2,
            )
        block, energy, last_trunc = _single_dmrg_step(block, block, m=m_warmup, j=j, jz=jz)
        if verbose:
            print("  E/(sites so far) =", energy / (2 * block.length))
        block_disk["l", block.length] = block
        block_disk["r", block.length] = block

    sys_label, env_label = "l", "r"
    sys_block = block
    energy = 0.0

    for m in m_sweep_list:
        while True:
            env_block = block_disk[env_label, chain_length - sys_block.length - 2]
            if env_block.length == 1:
                sys_block, env_block = env_block, sys_block
                sys_label, env_label = env_label, sys_label

            if verbose:
                graphic = ("=" * sys_block.length) + "**" + ("-" * env_block.length)
                if sys_label == "r":
                    graphic = graphic[::-1]
                print(f"sweep m={m}: {graphic}")

            sys_block, energy, last_trunc = _single_dmrg_step(sys_block, env_block, m=m, j=j, jz=jz)
            if verbose:
                print("  E/L =", energy / chain_length, "trunc_err=", last_trunc)

            block_disk[sys_label, sys_block.length] = sys_block

            if sys_label == "l" and 2 * sys_block.length == chain_length:
                break

    meta = {"truncation_error": float(last_trunc)}
    return float(energy), meta


def exact_heisenberg_obc_energy(chain_length: int, *, j: float = 1.0, jz: float = 1.0) -> float:
    """Dense ED reference (exponential cost; only for small `chain_length`)."""
    if chain_length > 16:
        raise ValueError("exact reference is only intended for small chain_length")

    dim = 2**chain_length
    # Sum of open-chain nearest-neighbor bonds (same convention as `_H2`).
    h_tot = csr_matrix((dim, dim), dtype=np.float64)
    for site in range(chain_length - 1):
        terms: list[csr_matrix] = []
        for s in range(chain_length):
            if s < site:
                terms.append(identity(2, format="csr", dtype=np.float64))
        terms.append(csr_matrix(Sz1))
        terms.append(csr_matrix(Sz1))
        for _ in range(site + 2, chain_length):
            terms.append(identity(2, format="csr", dtype=np.float64))
        h_tot += jz * _kron_chain(terms)

        terms_sp: list[csr_matrix] = []
        for s in range(chain_length):
            if s < site:
                terms_sp.append(identity(2, format="csr", dtype=np.float64))
        terms_sp.append(csr_matrix(Sp1))
        terms_sp.append(csr_matrix(Sp1.T))
        for _ in range(site + 2, chain_length):
            terms_sp.append(identity(2, format="csr", dtype=np.float64))
        h_tot += (j / 2.0) * _kron_chain(terms_sp)

        terms_sm: list[csr_matrix] = []
        for s in range(chain_length):
            if s < site:
                terms_sm.append(identity(2, format="csr", dtype=np.float64))
        terms_sm.append(csr_matrix(Sp1.T))
        terms_sm.append(csr_matrix(Sp1))
        for _ in range(site + 2, chain_length):
            terms_sm.append(identity(2, format="csr", dtype=np.float64))
        h_tot += (j / 2.0) * _kron_chain(terms_sm)

    e0 = eigsh(h_tot, k=1, which="SA", return_eigenvectors=False)
    return float(np.asarray(e0).reshape(-1)[0])


def _kron_chain(ops: list[csr_matrix]) -> csr_matrix:
    out = ops[0]
    for op in ops[1:]:
        out = kron(out, op, format="csr")
    return out


@dataclass(frozen=True)
class ToyDmrgResult:
    energy: float
    energy_per_site: float
    meta: dict[str, float]


def run_toy_dmrg(
    *,
    chain_length: int,
    m_warmup: int,
    m_sweep_list: list[int],
    j: float = 1.0,
    jz: float = 1.0,
    verbose: bool = False,
) -> ToyDmrgResult:
    energy, meta = finite_system_dmrg(
        chain_length=chain_length,
        m_warmup=m_warmup,
        m_sweep_list=m_sweep_list,
        j=j,
        jz=jz,
        verbose=verbose,
    )
    return ToyDmrgResult(energy=energy, energy_per_site=energy / chain_length, meta=meta)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Toy finite-system DMRG for spin-1/2 Heisenberg/XXZ chain (OBC)."
    )
    p.add_argument("--L", type=int, default=20, help="Even chain length (open boundary).")
    p.add_argument("--m-warmup", type=int, default=10)
    p.add_argument(
        "--m-sweeps",
        type=str,
        default="10,20,30",
        help="Comma-separated bond dimensions per sweep pass.",
    )
    p.add_argument("--J", type=float, default=1.0)
    p.add_argument("--Jz", type=float, default=1.0)
    p.add_argument(
        "--exact",
        action="store_true",
        help="Also compute exact ground state energy for small L (<=16).",
    )
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()

    m_sweep_list = [int(x) for x in args.m_sweeps.split(",") if x.strip()]
    res = run_toy_dmrg(
        chain_length=args.L,
        m_warmup=args.m_warmup,
        m_sweep_list=m_sweep_list,
        j=args.J,
        jz=args.Jz,
        verbose=args.verbose,
    )
    print(f"E_total={res.energy:.12f}")
    print(f"E_per_site={res.energy_per_site:.12f}")
    print(f"meta={res.meta}")

    if args.exact:
        e0 = exact_heisenberg_obc_energy(args.L, j=args.J, jz=args.Jz)
        print(f"E_exact={e0:.12f}")
        print(f"delta_E={res.energy - e0:.3e}")


if __name__ == "__main__":
    main()
