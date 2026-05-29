from __future__ import annotations

import pytest
from pydantic import ValidationError

from qchem_stack.config.backend import BackendSpecConfig
from qchem_stack.config.compiler import CompilerSpec
from qchem_stack.config.nexus import NexusAnalogSpec, NexusCloudSpec
from qchem_stack.config.quantum import QuantumSpec


def test_backend_optional_endpoint_normalized_to_none() -> None:
    cfg = BackendSpecConfig(ionstack_endpoint="   ")
    assert cfg.ionstack_endpoint is None


def test_compiler_native_twoq_normalized_uppercase() -> None:
    cfg = CompilerSpec(native_twoq="  cx  ")
    assert cfg.native_twoq == "CX"


def test_compiler_native_twoq_rejects_blank() -> None:
    with pytest.raises(ValidationError, match="compiler.native_twoq"):
        CompilerSpec(native_twoq="   ")


def test_nexus_analog_project_label_rejects_blank() -> None:
    with pytest.raises(ValidationError, match="nexus_analog.project_label"):
        NexusAnalogSpec(project_label="   ")


def test_nexus_cloud_api_key_env_rejects_blank_after_strip() -> None:
    with pytest.raises(ValidationError, match="nexus_cloud.api_key_env"):
        NexusCloudSpec(api_key_env="   ")


def test_quantum_algorithm_factory_blank_normalized_to_none() -> None:
    cfg = QuantumSpec(algorithm="vqe", algorithm_factory="  ")
    assert cfg.algorithm_factory is None
