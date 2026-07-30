#!/usr/bin/env python3
"""H2 QML-FF job 8992: training curves + VQE PES + QML-FF parity (corrected) + residual."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path('/home/sunhl/projects/qchem_qml_md/results/h2_bondscan_ol_statevector_r12_8992')
INK = "#142033"; MUTED = "#4E5D6C"; ACCENT = "#2A4F8A"; ACCENT2 = "#8A4333"
OK = "#246044"; WARN = "#B45309"; GRID = "#E2E8F0"
CUTOFF = 11.33835674775462; DISSOC = 3.0

for fp in ("/mnt/c/Windows/Fonts/msyh.ttc", "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"):
    if Path(fp).exists():
        font_manager.fontManager.addfont(fp)
        plt.rcParams["font.sans-serif"] = [font_manager.FontProperties(fname=fp).get_name(), "DejaVu Sans"]
        break
plt.rcParams.update({"axes.unicode_minus": False, "figure.facecolor": "white",
                     "axes.facecolor": "white", "axes.edgecolor": "#C8D0DA",
                     "text.color": INK, "figure.dpi": 160})
LEG_KW = dict(fontsize=8, framealpha=1.0, edgecolor='#C8D0DA', fancybox=False, borderpad=0.8)

# ---- Collect training curve data ----
pm = json.loads((ROOT / 'pretrain_metrics.json').read_text())
tm = pm.get('training_metrics', {})
fm = tm.get('final_metrics', {})
round_labels = ['pretrain']
e_mae = [fm.get('energy_mae', np.nan)]
f_rmse = [fm.get('force_rmse', np.nan)]
loss = [fm.get('loss', np.nan)]
for p in sorted(ROOT.glob('validation_round_*.json'), key=lambda x: int(x.stem.split('_')[-1])):
    d = json.loads(p.read_text()); r = d['round']; ri = r['round_index']
    m = (r.get('training_metrics') or {}).get('final_metrics') or {}
    round_labels.append(f'r{ri}')
    e_mae.append(m.get('energy_mae', np.nan))
    f_rmse.append(m.get('force_rmse', np.nan))
    loss.append(m.get('loss', np.nan))

# ---- Collect VQE PES (training frames) ----
def parse_xyz(p):
    if not p.exists(): return []
    lines = p.read_text().splitlines(); i = 0; out = []
    while i < len(lines):
        if not lines[i].strip(): i += 1; continue
        n = int(lines[i]); i += 1; comment = lines[i]; i += 1; pos = []
        for _ in range(n):
            parts = lines[i].split(); pos.append([float(x) for x in parts[1:4]]); i += 1
        a = np.asarray(pos, float); E = float('nan')
        for tok in comment.split():
            if tok.startswith('energy='): E = float(tok.split('=')[1])
        if a.shape[0] == 2:
            out.append((float(np.linalg.norm(a[0] - a[1])), E))
    return out

tr = sorted(ROOT.glob('train_round_*.xyz'), key=lambda p: int(p.stem.split('_')[-1]))
bf = parse_xyz(tr[-1]) if tr else parse_xyz(ROOT / 'train_after_pretrain.xyz')

# ---- Collect parity data with CORRECTED QML energies ----
# corrected QML energy = VQE + delta_hartree (the corrected delta, not raw)
parity_data = []
residual_data = []  # (round, delta_corr, VQE)
for p in sorted(ROOT.glob('validation_round_*.json'), key=lambda x: int(x.stem.split('_')[-1])):
    d = json.loads(p.read_text()); r = d['round']; ri = r['round_index']
    for fr in r.get('frames') or []:
        e_vqe = float(fr['energy_qchem_hartree'])
        d_corr = float(fr['delta_hartree'])
        e_qml_corr = e_vqe + d_corr
        parity_data.append((e_vqe, e_qml_corr, ri))
        residual_data.append((ri, d_corr, e_vqe))

# ---- Create figure (1x3 layout, no VQE PES — already in P3 overview) ----
fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
fig.suptitle('H2 QML-FF 训练过程与量子计算验证（HPC job 8992 · P3）',
             fontsize=13, fontweight='bold', color=INK, y=0.98)

# Panel 1: Training curves
ax = axes[0]
x = np.arange(len(round_labels))
ax2 = ax.twinx()
l1, = ax.plot(x, e_mae, 'o-', color=ACCENT, lw=2, ms=5, label='E-MAE (归一化尺度)')
l2, = ax.plot(x, f_rmse, 's--', color=ACCENT2, lw=1.5, ms=4, label='F-RMSE (Ha/Bohr)')
ax.set_xlabel('阶段（预训练 + 在线学习轮次）')
ax.set_ylabel('E-MAE / F-RMSE', color=INK)
ax.set_xticks(x); ax.set_xticklabels(round_labels, fontsize=8, rotation=30, ha='right')
ax.grid(True, color=GRID, lw=0.8)
l3, = ax2.plot(x, loss, '^:', color=MUTED, lw=1.5, ms=4, label='total loss')
ax2.set_ylabel('total loss', color=MUTED); ax2.tick_params(axis='y', labelcolor=MUTED)
ax.legend([l1, l2, l3], [l1.get_label(), l2.get_label(), l3.get_label()],
          fontsize=7.5, loc='center right', framealpha=1.0, edgecolor='#C8D0DA')
ax.set_title('训练曲线（预训练 → r9）', pad=12)
ax.text(0.03, 0.97, '注：E-MAE 为归一化尺度\n（subtract_mean, mean=-24.11 Ha）\n物理误差见右下残差图',
        transform=ax.transAxes, fontsize=7, va='top', color=MUTED,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#C8D0DA', alpha=0.9))

# Panel 2: QML-FF parity plot (corrected) — zoom x to FCI range, y to QML range
ax = axes[1]
if parity_data:
    E_fci = np.array([x[0] for x in parity_data])
    E_qml = np.array([x[1] for x in parity_data])
    rounds = np.array([x[2] for x in parity_data])
    scatter = ax.scatter(E_fci, E_qml, c=rounds, cmap='viridis', s=50, alpha=0.9,
                         edgecolors='white', lw=0.3, zorder=3)
    cbar = fig.colorbar(scatter, ax=ax, shrink=0.8, pad=0.02)
    cbar.set_label('OL 轮次', fontsize=8)
    # Zoom x to FCI range, y to QML range (different scales — not a square parity)
    fci_lo, fci_hi = E_fci.min() - 0.0005, E_fci.max() + 0.0005
    qml_lo, qml_hi = E_qml.min() - 0.005, E_qml.max() + 0.005
    ax.set_xlim(fci_lo, fci_hi); ax.set_ylim(qml_lo, qml_hi)
    # Horizontal reference line at FCI mean (ideal: all QML == FCI mean)
    fci_mean = float(E_fci.mean())
    ax.axhline(fci_mean, color=ACCENT2, ls='--', lw=1.2,
               label=f'FCI 均值 = {fci_mean:.4f} Ha')
    mae = np.mean(np.abs(E_qml - E_fci)); max_ae = np.max(np.abs(E_qml - E_fci))
    fci_spread = E_fci.max() - E_fci.min()
    ax.text(0.05, 0.95,
            f'MAE={mae:.4f} Ha\nmax|Δ|={max_ae:.4f} Ha\nN={len(parity_data)}\n'
            f'FCI spread={fci_spread:.4f} Ha',
            transform=ax.transAxes, fontsize=8, va='top', color=INK,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                      edgecolor='#C8D0DA', alpha=0.9))
ax.set_xlabel('FCI 参考能量 (Ha，缩放至实际范围)')
ax.set_ylabel('QML-FF 预测能量 (Ha)')
ax.set_title('QML-FF parity（预测 vs FCI 参考，已校正归一化偏移）', pad=12)
ax.grid(True, color=GRID, lw=0.8)
ax.legend(loc='lower right', **LEG_KW)

# Panel 3: Residual plot (delta vs round) — the real error
ax = axes[2]
if residual_data:
    r_arr = np.array([x[0] for x in residual_data])
    d_arr = np.array([x[1] for x in residual_data])
    ax.scatter(r_arr, d_arr, c=r_arr, cmap='viridis', s=60, alpha=0.9,
               edgecolors='white', lw=0.4, zorder=3)
    ax.axhline(0, color=ACCENT2, ls='--', lw=1.2, label='Δ = 0 (理想)')
    # per-round max|delta|
    for ri in sorted(set(r_arr.tolist())):
        mask = r_arr == ri
        mx = np.max(np.abs(d_arr[mask]))
        ax.annotate(f'{mx:.3f}', xy=(ri, d_arr[mask][np.argmax(np.abs(d_arr[mask]))]),
                    fontsize=7, color=MUTED, ha='center',
                    xytext=(0, 8), textcoords='offset points')
    ax.set_xlabel('在线学习轮次'); ax.set_ylabel('ΔE = QML − VQE (Ha)')
    ax.set_title('残差图（模型真实误差，物理尺度）', pad=12)
    ax.set_xticks(sorted(set(r_arr.tolist())))
    ax.grid(True, color=GRID, lw=0.8)
    ax.legend(loc='upper left', **LEG_KW)
    # chemical accuracy reference
    ax.axhline(0.0016, color=OK, ls=':', lw=1, alpha=0.6)
    ax.axhline(-0.0016, color=OK, ls=':', lw=1, alpha=0.6)
    ax.text(0.02, 0.0016, '化学精度 1 kcal/mol', fontsize=7, color=OK, va='bottom')

fig.text(0.5, 0.005,
         'Source: HPC job 8992 · P3 · 9/12 rounds · statevector VQE · 8q/3L QNN · '
         '能量已校正 subtract_mean 归一化偏移 (shift=0.1434 Ha) · VQE PES 见总览图',
         ha='center', fontsize=8, color=MUTED)
fig.tight_layout(rect=(0.01, 0.04, 0.99, 0.93))
fig.subplots_adjust(wspace=0.38)
out = ROOT / 'figures' / 'h2_bondscan_ol_8992_training_parity.png'
fig.savefig(out, dpi=180, bbox_inches='tight', facecolor='white', pad_inches=0.3)
for alt in [Path('/home/sunhl/projects/qchem_qml_md/docs/assets/shuzhi_demo/uqc'),
            Path('/tmp/shuzhi_unified/figures/uqc')]:
    alt.mkdir(parents=True, exist_ok=True)
    fig.savefig(alt / out.name, dpi=180, bbox_inches='tight', facecolor='white', pad_inches=0.3)
print(f'wrote {out}')
print(f'Parity MAE (corrected) = {mae:.4f} Ha, max|delta| = {max_ae:.4f} Ha')
print(f'VQE spread = {vqe_spread:.4f} Ha')
plt.close(fig)
