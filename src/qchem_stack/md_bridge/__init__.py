from qchem_stack.md_bridge.classical_h2_ff import (
    ClassicalH2MorseHandle,
    build_classical_h2_handle,
    train_classical_h2_on_qmef,
)
from qchem_stack.md_bridge.contracts import (
    ForceFieldTrainerProtocol,
    StubTorchMLIPTrainer,
    TrainedModelArtifact,
)
from qchem_stack.md_bridge.exporter import export_extended_xyz, write_hdf5_stub
from qchem_stack.md_bridge.hooks import write_mace_yaml_stub, write_nequip_yaml_stub
from qchem_stack.md_bridge.md_validation_loop import (
    Ensemble,
    FrameValidationRecord,
    MdValidationLoopConfig,
    MdValidationRoundLog,
    run_md_validation_loop,
)
from qchem_stack.md_bridge.qchem_labeler import (
    EnergyReference,
    LabelingFailure,
    LabelingResult,
    TheoryLevel,
    label_base_geometry_only,
    label_geometries_with_pipeline,
    merge_qmef_datasets,
)
from qchem_stack.md_bridge.qmlff_adapter import (
    ForceFieldBackend,
    JaxMdTrajectory,
    QmlffModelHandle,
    atomic_number_to_symbol,
    build_force_field_handle,
    build_qmlff_model_angle,
    build_qmlff_model_from_preset,
    build_qmlff_model_quantum_ff,
    build_qmp_h2_model,
    predict_energy_forces_hartree,
    qmlff_handle_to_qmef_frame,
    run_jaxmd_trajectory,
    select_geometries_from_trajectory,
    symbol_to_atomic_number,
    train_force_field_on_qmef,
    train_qmlff_on_qmef,
    trajectory_to_extxyz,
)
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame

__all__ = [
    # Pre-existing surface (kept verbatim for backward compatibility)
    "QMFrame",
    "QMEFDataset",
    "ForceFieldTrainerProtocol",
    "TrainedModelArtifact",
    "StubTorchMLIPTrainer",
    "export_extended_xyz",
    "write_hdf5_stub",
    "write_nequip_yaml_stub",
    "write_mace_yaml_stub",
    # New (optional) qchem labeling helpers — pure qchem_stack, no external deps
    "EnergyReference",
    "TheoryLevel",
    "LabelingFailure",
    "LabelingResult",
    "label_base_geometry_only",
    "label_geometries_with_pipeline",
    "merge_qmef_datasets",
    # New (optional) classical H2 Morse — no qmlff training dependency
    "ClassicalH2MorseHandle",
    "build_classical_h2_handle",
    "train_classical_h2_on_qmef",
    # New (optional) QML-FF / JAX-MD adapter — soft-imports qmlff / jax_md
    "ForceFieldBackend",
    "QmlffModelHandle",
    "JaxMdTrajectory",
    "build_force_field_handle",
    "build_qmlff_model_from_preset",
    "build_qmlff_model_quantum_ff",
    "build_qmlff_model_angle",
    "build_qmp_h2_model",
    "train_force_field_on_qmef",
    "train_qmlff_on_qmef",
    "predict_energy_forces_hartree",
    "run_jaxmd_trajectory",
    "select_geometries_from_trajectory",
    "trajectory_to_extxyz",
    "qmlff_handle_to_qmef_frame",
    "atomic_number_to_symbol",
    "symbol_to_atomic_number",
    # New (optional) end-to-end active-learning loop
    "Ensemble",
    "MdValidationLoopConfig",
    "FrameValidationRecord",
    "MdValidationRoundLog",
    "run_md_validation_loop",
]
