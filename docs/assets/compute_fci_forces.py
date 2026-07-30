#!/usr/bin/env python3
"""Compute FCI/STO-3G energies AND forces for all training geometries, save as QMEFDataset."""
import json
from pathlib import Path
import numpy as np
from pyscf import gto, scf, mcscf
from pyscf.grad import casci as casci_grad

ROOT = Path('/home/sunhl/projects/qchem_qml_md')
RESULTS = ROOT / 'results/h2_bondscan_ol_statevector_r12_8992'

def fci_energy_forces_h2(R_bohr):
    """Compute FCI energy and forces for H2 at bond length R (Bohr)."""
    mol = gto.M(atom=f'H 0 0 0; H 0 0 {R_bohr}', basis='sto3g', unit='Bohr', verbose=0)
    mf = scf.RHF(mol).run()
    mc = mcscf.CASCI(mf, 2, 2)  # CASCI(2e,2o) = FCI for H2/STO-3G
    mc.kernel()
    e_fci = float(mc.e_tot)
    grad = casci_grad.Gradients(mc).kernel(ci=mc.ci)
    forces = (-np.array(grad)).tolist()
    return e_fci, forces

# Parse training geometries from train_round_9.xyz
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

print(f'Computing FCI energy + forces for {len(bf)} training frames...')
frames = []
for idx, (R, E_vqe, pos) in enumerate(bf):
    E_fci, forces = fci_energy_forces_h2(R)
    frames.append({
        'R': R, 'E_vqe': E_vqe, 'E_fci': E_fci,
        'positions_bohr': pos.tolist(),
        'forces_hartree_bohr': forces,
        'delta_vqe_fci': E_vqe - E_fci,
    })
    flag = '***' if abs(E_vqe - E_fci) > 0.01 else 'OK'
    print(f'  [{idx+1}/{len(bf)}] R={R:6.3f}  E_fci={E_fci:.6f}  F_norm={np.linalg.norm(forces):.4f}  {flag}')

out_path = RESULTS / 'fci_training_data.json'
out_path.write_text(json.dumps(frames, indent=2))
print(f'\nSaved {len(frames)} FCI frames to {out_path}')
