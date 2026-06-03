"""Compatibility shim: UQC executor lives in optional ``qchem-stack-uqc`` package."""

from qchem_stack_uqc.uqc_executor import UQCCloudHeaExecutor

__all__ = ["UQCCloudHeaExecutor"]
