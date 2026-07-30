#!/usr/bin/env python3
"""Generate comprehensive figure: training curves + PES comparison + parity, using FCI-fine-tuned model."""
import json
import sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path('/home/sunhl/projects/qchem_qml_md')
RESULTS = ROOT / 'results/h2_bondscan_ol_statevector_r12_8992'
CKPT_DIR = RESULTS / 'qmlff_checkpoints/fci_finetune'
CKPT = CKPT_DIR / 'final.npz'
FIG_OUT = ROOT / 'docs/assets/h2_bondscan_ol_8992_fci_finetune_overview.png'

sys.path.insert(0, str(ROOT / 'src'))
from qchem_stack.md_bridge import build_force_field_handle, predict_energy_forces_hartree

# ---- Load FCI training data ----
fci_data = json.loads((RESULTS / 'fci_training_data.json').read_text())
R_list = np.array([f['R'] for f in fci_data])
E_fci = np.array([f['E_fci'] for f in fci_data])
E_vqe = np.array([f['E_vqe'] for f in fci_data])
positions = [np.array(f['positions_bohr'], dtype=np.float64) for f in fci_data]

# ---- Load training history ----
hist = json.loads((CKPT_DIR / 'training_history.json').read_text())
train_hist = hist.get('train_history', [])
losses = [h['loss'] for h in train_hist]
e_maes = [h['energy_mae'] for h in train_hist]
f_rmses = [h['force_rmse'] for h in train_hist]
epochs = [h['epoch'] + 1 for h in train_hist]

# ---- Build handle and load checkpoint ----
handle = build_force_field_handle(
    ["H"], backend="qmlff_preset", preset="atomic_amplitude",
    builder_overrides={"n_qubits": 8, "n_layers": 3},
)
data = {k: np.asarray(v) for k, v in np.load(CKPT, allow_pickle=True).items()}
handle.model.set_parameters(data)
handle.params = data

# Get energy_norm_params from FCI mean
fci_mean_eV = float(np.mean(E_fci) * 27.2114)
handle.energy_norm_params = {"method": "subtract_mean", "mean": fci_mean_eV}
print(f"FCI mean energy: {fci_mean_eV:.6f} eV")
print(f"Loaded checkpoint: {CKPT}")

# ---- Predict QML-FF energies for all training frames ----
E_qml = []
for i, pos in enumerate(positions):
    e_qml, _ = predict_energy_forces_hartree(handle, positions_bohr=pos, atomic_numbers=[1, 1])
    E_qml.append(e_qml)
E_qml = np.array(E_qml)

# ---- Compute errors ----
delta = E_qml - E_fci
mae = np.mean(np.abs(delta))
print(f"\nOverall MAE: {mae:.6f} Ha = {mae*27.2114:.4f} eV")
for label, mask in [("R<1.0", R_list < 1.0), ("1.0-1.5", (R_list >= 1.0) & (R_list < 1.5)),
                    ("1.5-3.0", (R_list >= 1.5) & (R_list < 3.0)), (">3.0", R_list >= 3.0)]:
    if np.any(mask):
        print(f"  {label}: MAE = {np.mean(np.abs(delta[mask])):.6f} Ha")

# ---- Create figure ----
fig, axes = plt.subplots(1, 3, figsize=(18, 5.5))

# Panel 1: Training curves
ax1 = axes[0]
ax1t = ax1.twinx()
l1, = ax1.plot(epochs, losses, 'b-', alpha=0.8, label='Total Loss')
l2, = ax1t.plot(epochs, e_maes, 'r-', alpha=0.8, label='E_MAE (eV)')
l3, = ax1t.plot(epochs, f_rmses, 'g-', alpha=0.8, label='F_RMSE (eV/Å)')
ax1.set_xlabel('Epoch', fontsize=12)
ax1.set_ylabel('Total Loss', fontsize=12, color='b')
ax1t.set_ylabel('MAE / RMSE (eV)', fontsize=12, color='r')
ax1.set_title('FCI Fine-tune Training Curves', fontsize=13)
lines = [l1, l2, l3]
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper right', fontsize=9, framealpha=0.9)
ax1.tick_params(axis='y', labelcolor='b')

# Panel 2: PES comparison
ax2 = axes[1]
# Sort by R for clean plotting
sort_idx = np.argsort(R_list)
R_sorted = R_list[sort_idx]
E_fci_sorted = E_fci[sort_idx]
E_qml_sorted = E_qml[sort_idx]
E_vqe_sorted = E_vqe[sort_idx]

ax2.plot(R_sorted, E_fci_sorted, 'k-', linewidth=2, label='FCI (exact)', zorder=3)
ax2.plot(R_sorted, E_qml_sorted, 'r.--', linewidth=1, markersize=4, alpha=0.7, label='QML-FF (FCI fine-tuned)', zorder=2)
ax2.plot(R_sorted, E_vqe_sorted, 'b.--', linewidth=1, markersize=4, alpha=0.4, label='VQE (original, noisy)', zorder=1)
ax2.axhline(y=-0.933, color='gray', linestyle=':', alpha=0.5, label='Dissociation limit')
ax2.set_xlabel('Bond Length R (Bohr)', fontsize=12)
ax2.set_ylabel('Energy (Hartree)', fontsize=12)
ax2.set_title('H₂ PES: FCI vs QML-FF vs VQE', fontsize=13)
ax2.legend(loc='upper right', fontsize=9, framealpha=0.9)
ax2.set_xlim(0.3, 11)

# Panel 3: Parity plot
ax3 = axes[2]
# Use FCI as reference
ax3.scatter(E_fci, E_qml, c='red', s=30, alpha=0.7, edgecolors='darkred', linewidths=0.5, label='Training frames', zorder=2)
# Diagonal line
all_E = np.concatenate([E_fci, E_qml])
min_e, max_e = all_E.min(), all_E.max()
ax3.plot([min_e, max_e], [min_e, max_e], 'k--', linewidth=1, alpha=0.5, label='y = x (ideal)', zorder=1)
ax3.set_xlabel('FCI Energy (Hartree)', fontsize=12)
ax3.set_ylabel('QML-FF Energy (Hartree)', fontsize=12)
ax3.set_title(f'Parity: FCI vs QML-FF\nMAE = {mae*27.2114:.3f} eV = {mae:.5f} Ha', fontsize=13)
ax3.legend(loc='upper left', fontsize=9, framealpha=0.9)
ax3.set_aspect('equal')

plt.tight_layout()
plt.savefig(FIG_OUT, dpi=150, bbox_inches='tight')
print(f"\nFigure saved: {FIG_OUT}")
plt.close()
