"""PySCF classical post-HF benchmarks (HF reference energies + MP2 / CCSD / CASCI)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from qchem_stack.chem.classical_benchmarks.schema import CLASSICAL_POST_HF_BENCHMARKS_SCHEMA_V1
from qchem_stack.chem.drivers.pyscf_driver_types import unwrap_pyscf_rhf_for_backend_operations

if TYPE_CHECKING:
    from qchem_stack.chem.classical_benchmarks.context import ClassicalBenchmarkContext


def run_classical_post_hf_pyscf(ctx: ClassicalBenchmarkContext) -> dict[str, Any]:
    """Requires ``ctx.mean_field_reference.backend_tag() == "pyscf"`` (enforced by registry)."""
    ref = ctx.mean_field_reference
    if ref is None or ref.backend_tag() != "pyscf":
        raise RuntimeError(
            "run_classical_post_hf_pyscf expects a PySCF-tagged ClassicalMeanFieldReference"
        )
    pr = unwrap_pyscf_rhf_for_backend_operations(ref.as_pyscf_rhf_result())
    mf = pr.mf
    method = ctx.reference_scf_method

    out: dict[str, Any] = {
        "schema": CLASSICAL_POST_HF_BENCHMARKS_SCHEMA_V1,
        "backend_id": "pyscf",
        "reference_scf_method": method,
        "hf": {
            "status": "ok",
            "value": float(pr.e_tot),
            "reason": None,
        },
    }

    def _ok(v: float) -> dict[str, Any]:
        return {"status": "ok", "value": float(v), "reason": None}

    def _na(reason: str) -> dict[str, Any]:
        return {"status": "unavailable", "value": None, "reason": reason}

    def _failed(reason: str) -> dict[str, Any]:
        return {"status": "failed", "value": None, "reason": reason}

    try:
        from pyscf import mp

        emp2 = float(mp.UMP2(mf).kernel()[0]) if method == "UHF" else float(mp.MP2(mf).kernel()[0])
        out["mp2"] = _ok(emp2)
    except ImportError as e:
        out["mp2"] = _na(f"pyscf.mp unavailable: {e}")
    except (MemoryError, RuntimeError, ValueError, ArithmeticError) as e:
        out["mp2"] = _failed(str(e))
    except Exception as e:  # noqa: BLE001 - keep pipeline resilient to unexpected backend errors
        out["mp2"] = _failed(f"unexpected: {e}")

    try:
        from pyscf import cc

        mycc = cc.UCCSD(mf) if method == "UHF" else cc.CCSD(mf)
        ecc, *_ = mycc.kernel()
        out["ccsd"] = _ok(float(mf.e_tot) + float(ecc))
    except ImportError as e:
        out["ccsd"] = _na(f"pyscf.cc unavailable: {e}")
    except (MemoryError, RuntimeError, ValueError, ArithmeticError) as e:
        out["ccsd"] = _failed(str(e))
    except Exception as e:  # noqa: BLE001 - keep pipeline resilient to unexpected backend errors
        out["ccsd"] = _failed(f"unexpected: {e}")

    na_o = ctx.n_active_orbitals
    na_e = ctx.n_active_electrons
    if na_o is None or na_e is None:
        out["casci"] = _na(
            "n_active_orbitals and n_active_electrons are required for CASCI benchmark."
        )
    else:
        try:
            from pyscf import mcscf

            from qchem_stack.chem.pyscf_typing import as_pyscf_cas, as_pyscf_mf

            mc = as_pyscf_cas(mcscf.CASCI(as_pyscf_mf(mf), int(na_o), int(na_e)))
            ecas, *_ = mc.kernel()
            out["casci"] = _ok(float(ecas))
        except ImportError as e:
            out["casci"] = _na(f"pyscf.mcscf unavailable: {e}")
        except (MemoryError, RuntimeError, ValueError, ArithmeticError) as e:
            out["casci"] = _failed(str(e))
        except Exception as e:  # noqa: BLE001 - keep pipeline resilient to unexpected backend errors
            out["casci"] = _failed(f"unexpected: {e}")

    return out
