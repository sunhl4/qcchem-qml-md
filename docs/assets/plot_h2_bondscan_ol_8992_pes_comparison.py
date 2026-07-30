#!/usr/bin/env python3
"""Plot VQE vs QML-FF energy curves across full bond length range for H2 (job 8992)."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path('/home/sunhl/projects/qchem_qml_md')
RESULTS = ROOT / 'results/h2_bondscan_ol_statevector_r12_8992'
CKPT = RESULTS / 'qmlff_checkpoints' / 'round_09' / 'final.npz'

INK = "#142033"; MUTED = "#4E5D6C"; ACCENT = "#2A4F8A"; ACCENT2 = "#8A4333"
OK = "#246044"; WARN = "#B45309"; GRID = "#E2E8F0"
DISSOC = 3.0; CUTOFF = 11.33835674775462

for fp in ("/mnt/c/Windows/Fonts/msyh.ttc", "/usr/share/fonts/truetype/wqy/wq-microhei.ttc"):
    if Path(fp).exists():
        font_manager.fontManager.addfont(fp)
        plt.rcParams["font.sans-serif"] = [font_manager.FontProperties(fname=fp).get_name(), "DejaVu Sans"]
        break
plt.rcParams.update({"axes.unicode_minus": False, "figure.facecolor": "white",
                     "axes.facecolor": "white", "axes.edgecolor": "#C8D0DA",
                     "text.color": INK, "figure.dpi": 160})

# ---- Load FCI energies (computed by compute_fci_energies.py) ----
fci_data = json.loads((RESULTS / 'fci_energies.json').read_text())
train_fci = fci_data['train']
train_fci.sort(key=lambda x: x['R'])
R_ref = np.array([x['R'] for x in train_fci])
E_fci = np.array([x['E_fci'] for x in train_fci])
E_vqe = np.array([x['E_vqe'] for x in train_fci])
vqe_bad = np.abs(E_vqe - E_fci) > 0.01  # mask of VQE frames that failed to converge

# ---- Load QML-FF model and predict energies at same bond lengths ----
import sys
sys.path.insert(0, str(ROOT / 'src'))
from qchem_stack.md_bridge import build_force_field_handle, predict_energy_forces_hartree

handle = build_force_field_handle(
    ["H"], backend="qmlff_preset", preset="atomic_amplitude",
    builder_overrides={"n_qubits": 8, "n_layers": 3},
)
data = {k: np.asarray(v) for k, v in np.load(CKPT, allow_pickle=True).items()}
handle.model.set_parameters(data)
handle.params = data  # critical: predict_energy_forces_hartree uses handle.params

# Get energy shift from pretrain metrics
pm = json.loads((RESULTS / 'pretrain_metrics.json').read_text())
tm = pm.get('training_metrics', {})
norm_params = tm.get('energy_norm_params')
handle.energy_norm_params = norm_params  # critical for denormalization
shift = tm.get('validation_energy_shift_hartree', 0.0)
print(f'Energy norm_params = {norm_params}')
print(f'validation_energy_shift_hartree = {shift}')

E_qml = []
for R in R_ref:
    pos = np.array([[-R / 2, 0.0, 0.0], [R / 2, 0.0, 0.0]], dtype=np.float64)
    e_raw, _ = predict_energy_forces_hartree(
        handle, positions_bohr=pos, atomic_numbers=[1, 1])
    e_corr = e_raw + shift  # apply normalization shift
    E_qml.append(e_corr)
E_qml = np.array(E_qml)

# ---- Also get validation frame predictions (near equilibrium, FCI=VQE there) ----
val_fci = fci_data['validation']
val_data = [(x['R'], x['E_fci'], x['E_qml'], x['round']) for x in val_fci]

# ---- Create figure ----
fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))
fig.suptitle(r'H$_2$ 全 PES：FCI 精确解与 QML-FF 预测对比（HPC job 8992 · P3 · round_09）',
             fontsize=13, fontweight='bold', color=INK, y=0.97)

# Panel 1: Energy vs bond length (full PES)
ax = axes[0]
ax.scatter(R_ref, E_fci, c=ACCENT, s=40, alpha=0.9, label=f'FCI 精确解 ({len(R_ref)} 帧)',
           edgecolors='white', lw=0.3, zorder=3)
ax.scatter(R_ref, E_qml, c=ACCENT2, s=40, alpha=0.9, marker='x',
           label=f'QML-FF 预测 ({len(R_ref)} 帧)', zorder=4)
# Mark VQE-bad frames
if np.any(vqe_bad):
    ax.scatter(R_ref[vqe_bad], E_vqe[vqe_bad], c=WARN, s=60, alpha=0.8, marker='v',
               label=f'VQE 未收敛 ({int(vqe_bad.sum())} 帧)', zorder=5, edgecolors='white', lw=0.3)
if val_data:
    R_val = [x[0] for x in val_data]; E_fci_val = [x[1] for x in val_data]
    ax.scatter(R_val, E_fci_val, c=OK, s=25, alpha=0.6, marker='o',
               label=f'校验帧 FCI ({len(R_val)})', edgecolors='white', lw=0.2, zorder=2)
ax.axhline(-0.9332, color=MUTED, ls=':', lw=1, label='解离渐近线 -0.9332 Ha')
ax.axvline(DISSOC, color=WARN, ls='--', lw=1, alpha=0.4, label=f'解离阈值 {DISSOC} Bohr')
ax.set_xlabel('H-H 键长 (Bohr)'); ax.set_ylabel('能量 (Ha)')
ax.set_title('FCI vs QML-FF：全 PES 能量曲线', pad=12)
ax.grid(True, color=GRID, lw=0.8)
ax.legend(fontsize=8, loc='center right', framealpha=1.0, edgecolor='#C8D0DA')

# Panel 2: Parity plot (FCI reference — this is the real parity!)
ax = axes[1]
ax.scatter(E_fci, E_qml, c=ACCENT, s=40, alpha=0.9, label=f'训练帧 ({len(E_fci)})',
           edgecolors='white', lw=0.3, zorder=3)
if val_data:
    ax.scatter([x[1] for x in val_data], [x[2] for x in val_data], c=OK, s=30, alpha=0.7,
               label=f'校验帧 ({len(val_data)})', edgecolors='white', lw=0.2, zorder=4)
all_fci = np.concatenate([E_fci, [x[1] for x in val_data]])
all_qml = np.concatenate([E_qml, [x[2] for x in val_data]])
lo, hi = all_fci.min() - 0.05, all_fci.max() + 0.05
ax.plot([lo, hi], [lo, hi], '--', color=ACCENT2, lw=1.2, label='y = x (理想)')
ax.set_xlim(lo, hi); ax.set_ylim(lo, hi)
mae_train = np.mean(np.abs(E_qml - E_fci))
max_train = np.max(np.abs(E_qml - E_fci))
ax.text(0.05, 0.95, f'训练帧: MAE={mae_train:.4f} Ha\n  max|Δ|={max_train:.4f} Ha\n  N={len(E_fci)}',
        transform=ax.transAxes, fontsize=8, va='top', color=INK,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#C8D0DA', alpha=0.9))
ax.set_xlabel('FCI 参考能量 (Ha)'); ax.set_ylabel('QML-FF 预测能量 (Ha)')
ax.set_title('QML-FF parity（全范围，FCI 参考）', pad=12)
ax.grid(True, color=GRID, lw=0.8)
ax.legend(fontsize=8, loc='lower right', framealpha=1.0, edgecolor='#C8D0DA')
ax.set_aspect('equal')

fig.text(0.5, 0.01,
         f'Source: HPC job 8992 · P3 · round_09 checkpoint · FCI/STO-3G (PySCF) · 8q/3L QNN · '
         f'能量已校正 subtract_mean 归一化偏移 (shift={shift:.4f} Ha)',
         ha='center', fontsize=8, color=MUTED)
fig.tight_layout(rect=(0.01, 0.04, 0.99, 0.93))
out = RESULTS / 'figures' / 'h2_bondscan_ol_8992_pes_comparison.png'
fig.savefig(out, dpi=180, bbox_inches='tight', facecolor='white', pad_inches=0.3)
for alt in [ROOT / 'docs/assets/shuzhi_demo/uqc', Path('/tmp/shuzhi_unified/figures/uqc')]:
    alt.mkdir(parents=True, exist_ok=True)
    fig.savefig(alt / out.name, dpi=180, bbox_inches='tight', facecolor='white', pad_inches=0.3)
print(f'\nwrote {out}')
print(f'Train MAE = {mae_train:.4f} Ha, max|delta| = {max_train:.4f} Ha')
plt.close(fig)
