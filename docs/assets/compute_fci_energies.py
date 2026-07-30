#!/usr/bin/env python3
"""Compute FCI/STO-3G energies for all training and validation geometries."""
import json
from pathlib import Path
import numpy as np
from pyscf import gto, scf, fci

ROOT = Path('/home/sunhl/projects/qchem_qml_md')
RESULTS = ROOT / 'results/h2_bondscan_ol_statevector_r12_8992'

def fci_energy_h2(R_bohr):
    mol = gto.M(atom=f'H 0 0 0; H 0 0 {R_bohr}', basis='sto3g', unit='Bohr', verbose=0)
    mf = scf.RHF(mol).run()
    e_fci = fci.FCI(mf.mol, mf.mo_coeff).kernel()[0]
    return float(e_fci)

# ---- Training frames ----
def parse_xyz(p):
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
            out.append((float(np.linalg.norm(a[0]-a[1])), E, a))
    return out

tr = sorted(RESULTS.glob('train_round_*.xyz'), key=lambda p: int(p.stem.split('_')[-1]))
bf = parse_xyz(tr[-1]) if tr else parse_xyz(RESULTS / 'train_after_pretrain.xyz')
bf.sort(key=lambda x: x[0])

print('=== Computing FCI for training frames ===')
train_data = []
for R, E_vqe, pos in bf:
    E_fci = fci_energy_h2(R)
    train_data.append({'R': R, 'E_vqe': E_vqe, 'E_fci': E_fci, 'delta_vqe_fci': E_vqe - E_fci})
    flag = '***' if abs(E_vqe - E_fci) > 0.01 else 'OK'
    print(f'  R={R:6.3f}  E_vqe={E_vqe:.6f}  E_fci={E_fci:.6f}  delta={E_vqe-E_fci:+.6f}  {flag}')

# ---- Validation frames ----
print('\n=== Computing FCI for validation frames ===')
val_data = []
for p in sorted(RESULTS.glob('validation_round_*.json'), key=lambda x: int(x.stem.split('_')[-1])):
    d = json.loads(p.read_text()); r = d['round']; ri = r['round_index']
    dbg = d.get('frames_debug') or {}
    for fr in r.get('frames') or []:
        fi = str(fr['frame_index'])
        qml_pred = (dbg.get(fi, {}) or {}).get('qml_prediction') or {}
        pos = np.asarray(qml_pred.get('positions_bohr') or [], float)
        if pos.shape != (2, 3): continue
        R = float(np.linalg.norm(pos[0] - pos[1]))
        E_vqe = float(fr['energy_qchem_hartree'])
        E_fci = fci_energy_h2(R)
        d_corr = float(fr['delta_hartree'])
        E_qml = E_vqe + d_corr
        val_data.append({'R': R, 'E_vqe': E_vqe, 'E_fci': E_fci,
                         'E_qml': E_qml, 'round': ri,
                         'delta_vqe_fci': E_vqe - E_fci})
        flag = '***' if abs(E_vqe - E_fci) > 0.01 else 'OK'
        print(f'  r{ri} R={R:6.3f}  E_vqe={E_vqe:.6f}  E_fci={E_fci:.6f}  delta={E_vqe-E_fci:+.6f}  {flag}')

# ---- Save ----
out = {'train': train_data, 'validation': val_data}
out_path = RESULTS / 'fci_energies.json'
out_path.write_text(json.dumps(out, indent=2))
print(f'\nSaved {len(train_data)} train + {len(val_data)} val FCI energies to {out_path}')
