#!/usr/bin/env python3
"""Fine-tune QML-FF on FCI-corrected data, warm-starting from round_09 checkpoint."""
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path('/home/sunhl/projects/qchem_qml_md')
RESULTS = ROOT / 'results/h2_bondscan_ol_statevector_r12_8992'
CKPT = RESULTS / 'qmlff_checkpoints' / 'round_09' / 'final.npz'
OUT_DIR = RESULTS / 'qmlff_checkpoints' / 'fci_finetune'

sys.path.insert(0, str(ROOT / 'src'))
from qchem_stack.md_bridge import build_force_field_handle, train_qmlff_on_qmef, predict_energy_forces_hartree
from qchem_stack.md_bridge.schema import QMEFDataset, QMFrame

# ---- Load FCI training data ----
fci_frames = json.loads((RESULTS / 'fci_training_data.json').read_text())
print(f'Loaded {len(fci_frames)} FCI frames')

# ---- Build QMEFDataset ----
qm_frames = []
for fr in fci_frames:
    qm_frames.append(QMFrame(
        atomic_numbers=[1, 1],
        positions_bohr=fr['positions_bohr'],
        energy_hartree=fr['E_fci'],
        forces_hartree_bohr=fr['forces_hartree_bohr'],
        charge=0,
        multiplicity=1,
        method_tag='FCI/STO-3G',
    ))
dataset = QMEFDataset(frames=qm_frames, provenance_yaml='FCI/STO-3G fine-tune from round_09')
print(f'QMEFDataset: {len(dataset.frames)} frames')

# ---- Build handle and load checkpoint ----
handle = build_force_field_handle(
    ["H"], backend="qmlff_preset", preset="atomic_amplitude",
    builder_overrides={"n_qubits": 8, "n_layers": 3},
)
data = {k: np.asarray(v) for k, v in np.load(CKPT, allow_pickle=True).items()}
handle.model.set_parameters(data)
handle.params = data
print(f'Loaded checkpoint: {CKPT}')

# ---- Fine-tune with warm start ----
OUT_DIR.mkdir(parents=True, exist_ok=True)
print('Starting fine-tune training (100 epochs, warm-start from round_09)...')
handle = train_qmlff_on_qmef(
    handle,
    dataset,
    n_epochs=100,
    batch_size=1,
    learning_rate=1.0e-3,
    force_weight=10.0,
    lr_scheduler='constant',
    checkpoint_dir=str(OUT_DIR),
    warm_start=True,
    warm_start_params_only=True,
    energy_normalization='subtract_mean',
    grad_clip=1.0,
    checkpoint_save_freq=0,
    seed=42,
)

# ---- Save new checkpoint ----
new_ckpt = OUT_DIR / 'final.npz'
np.savez(new_ckpt, **{k: np.asarray(v) for k, v in handle.params.items()})
print(f'Saved fine-tuned checkpoint: {new_ckpt}')

# ---- Evaluate on training frames ----
print('\n=== Evaluation: FCI vs QML-FF (fine-tuned) ===')
norm_params = handle.energy_norm_params or handle.train_meta.get('energy_norm_params')
shift = 0.0
if norm_params and norm_params.get('method') == 'subtract_mean':
    shift = float(norm_params['mean']) / 27.2114  # convert eV mean to Ha
# Actually the predict function already denormalizes, so no manual shift needed
# But we need to check what the function returns

errors = []
for fr in fci_frames:
    R = fr['R']
    pos = np.array(fr['positions_bohr'], dtype=np.float64)
    e_fci = fr['E_fci']
    e_qml, _ = predict_energy_forces_hartree(handle, positions_bohr=pos, atomic_numbers=[1, 1])
    delta = e_qml - e_fci
    errors.append(abs(delta))
    if abs(delta) > 0.05 or R < 1.0 or (1.5 < R < 3.0):
        print(f'  R={R:6.3f}  E_fci={e_fci:.6f}  E_qml={e_qml:.6f}  delta={delta:+.6f}')

errors = np.array(errors)
print(f'\nMAE = {np.mean(errors):.4f} Ha, max|delta| = {np.max(errors):.4f} Ha')
print(f'  R<1.0:  MAE = {np.mean(errors[:3]):.4f} Ha')
print(f'  1.0-1.5: MAE = {np.mean(errors[3:15]):.4f} Ha')
print(f'  1.5-3.0: MAE = {np.mean(errors[15:23]):.4f} Ha')
print(f'  >3.0:   MAE = {np.mean(errors[23:]):.4f} Ha')
