#!/usr/bin/env python3
"""Plot FCI vs QML-FF(fine-tuned) energy vs bond length R."""
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path('/home/sunhl/projects/qchem_qml_md')
RESULTS = ROOT / 'results/h2_bondscan_ol_statevector_r12_8992'
CKPT = RESULTS / 'qmlff_checkpoints/fci_finetune/final.npz'
FIG_OUT = ROOT / 'docs/assets/h2_bondscan_ol_8992_fci_finetune_pes.png'

sys.path.insert(0, str(ROOT / 'src'))
from qchem_stack.md_bridge import build_force_field_handle, predict_energy_forces_hartree

# ---- Load FCI training data ----
fci_data = json.loads((RESULTS / 'fci_training_data.json').read_text())
R = np.array([f['R'] for f in fci_data])
E_fci = np.array([f['E_fci'] for f in fci_data])
E_vqe = np.array([f['E_vqe'] for f in fci_data])
positions = [np.array(f['positions_bohr'], dtype=np.float64) for f in fci_data]

# ---- Build handle and predict QML-FF energies ----
handle = build_force_field_handle(
    ["H"], backend="qmlff_preset", preset="atomic_amplitude",
    builder_overrides={"n_qubits": 8, "n_layers": 3},
)
data = {k: np.asarray(v) for k, v in np.load(CKPT, allow_pickle=True).items()}
handle.model.set_parameters(data)
handle.params = data
handle.energy_norm_params = {"method": "subtract_mean", "mean": float(np.mean(E_fci) * 27.2114)}

E_qml = np.array([
    predict_energy_forces_hartree(handle, positions_bohr=pos, atomic_numbers=[1, 1])[0]
    for pos in positions
])

# ---- Sort by R for clean lines ----
idx = np.argsort(R)
R_s, E_fci_s, E_qml_s, E_vqe_s = R[idx], E_fci[idx], E_qml[idx], E_vqe[idx]

# ---- Plot ----
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# Left: Full PES
ax = axes[0]
ax.plot(R_s, E_fci_s, 'k-', linewidth=2.5, label='FCI (exact)', zorder=3)
ax.plot(R_s, E_qml_s, 'r--', linewidth=2, label='QML-FF (FCI fine-tuned)', zorder=2)
ax.axhline(y=-0.933, color='gray', linestyle=':', alpha=0.5, label='Dissociation limit')
ax.set_xlabel('Bond Length R (Bohr)', fontsize=13)
ax.set_ylabel('Energy (Hartree)', fontsize=13)
ax.set_title(r'H$_2$ PES: FCI vs QML-FF', fontsize=14)
ax.legend(fontsize=11, loc='upper right', framealpha=0.9)
ax.set_xlim(0.3, 11)
ax.set_ylim(-1.25, 0.0)

# Right: Zoom into equilibrium region
ax2 = axes[1]
ax2.plot(R_s, E_fci_s, 'k-', linewidth=2.5, label='FCI (exact)', zorder=3)
ax2.plot(R_s, E_qml_s, 'r--', linewidth=2, label='QML-FF (FCI fine-tuned)', zorder=2)
ax2.set_xlabel('Bond Length R (Bohr)', fontsize=13)
ax2.set_ylabel('Energy (Hartree)', fontsize=13)
ax2.set_title(r'Equilibrium region zoom (1.0–3.0 Bohr)', fontsize=14)
ax2.legend(fontsize=11, loc='upper right', framealpha=0.9)
ax2.set_xlim(1.0, 3.0)
ax2.set_ylim(-1.15, -0.95)

plt.tight_layout()
plt.savefig(FIG_OUT, dpi=150, bbox_inches='tight')
print(f"Figure saved: {FIG_OUT}")
plt.close()

# Print summary
delta = E_qml - E_fci
print(f"\nMAE = {np.mean(np.abs(delta)):.6f} Ha = {np.mean(np.abs(delta))*27.2114:.4f} eV")
for lo, hi, label in [(0,1.0,'R<1.0'),(1.0,1.5,'1.0-1.5'),(1.5,3.0,'1.5-3.0'),(3.0,99,'>3.0')]:
    m = (R>=lo)&(R<hi)
    if np.any(m):
        print(f"  {label}: MAE = {np.mean(np.abs(delta[m])):.6f} Ha")
