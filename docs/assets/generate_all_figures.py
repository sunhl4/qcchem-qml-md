#!/usr/bin/env python3
"""
Unified figure generation for qchem-stack group meeting report.
Regenerates **13** PNG assets from one script (`active_space_convergence` included for MD parity).

Typography：正文四号 14 pt；**插图内**统一用更大磅值，补偿 MD/Word 里图片缩放后「比正文小一号」的现象。

| 用途 | pt | 常量 |
|------|-----|------|
| Markdown 正文（与 `<style>` 一致） | 14 | 文档说明中记为 **PT_DOC** |
| **曲线 / SCI 等非流程图 PNG** | **16** | **FS_*** 取自 **PT_FIG** |
| **流程图类** (`comparison_flow`、driver、InQuanto、Tangelo、philosophy) | **PT_FIG_FLOW** | 字号 **WF_FS**；画布 inch 乘 **_FLOW_FIG_K** |

说明：**PT_FIG** 与 **PT_DOC** 相差约「一格」；流程图再放大一档，与 `comparison_flow` 统一比例。

Serif：拉丁文优先 Times New Roman；中文回退 Songti SC / SimSun / Noto Serif CJK（与 MD 一致）。
"""

import json
import math
import textwrap
from pathlib import Path

import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, Ellipse

# ─── Typography：正文 PT_DOC=14；插图 PT_FIG=16（嵌入后视觉对齐正文） ──
PT_DOC = 14.0             # Word / MD 四号（仅作注释对照；FS_* 不用此值）
PT_FIG = 16.0             # 曲线 / 条形图等通用插图
PT_FIG_FLOW = 19.5        # 流程图类：与 comparison_flow 统一（嵌入后仍清晰）
_FLOW_FIG_K = PT_FIG_FLOW / PT_FIG
WF_FS = PT_FIG_FLOW       # 流程图内各级文字同一磅值，靠加粗/颜色分层

# 全部 FS_* 仅为 PT_FIG（非流程图）。
FS_DISPLAY = PT_FIG
FS_HEAD = PT_FIG
FS_SUB = PT_FIG
FS_BODY = PT_FIG
FS_INBOX = PT_FIG
FS_CAPTION = PT_FIG
FS_LEGEND = PT_FIG

# Multiplier line spacing inside rounded workflow / driver / pipeline boxes (not font pt).
LS_BOX_TITLE = 1.12   # bold heading line(s) at top of block
LS_BOX_BODY = 1.18    # body / bullets / wrapped description (slightly airier than title)

_FONT_SERIF_STACK = ['Times New Roman', 'Times', 'Songti SC', 'SimSun', 'Noto Serif CJK SC',
                     'DejaVu Serif', 'Liberation Serif', 'Nimbus Roman']

plt.rcParams.update({
    # Matplotlib prefers named families in this order when rendering
    'font.family': 'serif',
    'font.serif': _FONT_SERIF_STACK,
    'font.size': FS_BODY,
    'axes.titlesize': FS_HEAD,
    'axes.labelsize': FS_SUB,
    'xtick.labelsize': FS_BODY,
    'ytick.labelsize': FS_BODY,
    'legend.fontsize': FS_LEGEND,
    'mathtext.fontset': 'stix',
    # STIX aligns well with serif body; keeps H_2 readable.
    'axes.linewidth': 1.5,
    'xtick.major.width': 1.5,
    'ytick.major.width': 1.5,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
})


def _wrap(s: str, width_chars: int) -> str:
    """Manual line breaks inside boxes."""
    chunks = []
    for block in str(s).split('\n'):
        block = block.strip()
        if not block:
            chunks.append('')
            continue
        chunks.append(
            '\n'.join(
                textwrap.wrap(
                    block,
                    width=width_chars,
                    break_long_words=True,
                    break_on_hyphens=True,
                    replace_whitespace=False,
                )
            )
        )
    return '\n'.join(chunks)


def _serif():
    """Force Times/s-serif stack on Text (matplotlib may drop rcParams on some backends)."""
    return {'family': 'serif'}


def _nl(s: str) -> int:
    """Line count after wrapping helper (ASCII / Latin)."""
    t = str(s).strip()
    return (t.count('\n') + 1) if t else 1


# Single-line spacing in transAxes fractions for ~FS_SUB on typical fig heights.
_AX_LH = 0.036
_AX_LH_FLOW = _AX_LH * _FLOW_FIG_K

C = {
    'navy':    '#1d3557',
    'blue':    '#457b9d',
    'lblue':   '#a8dadc',
    'cream':   '#f1faee',
    'red':     '#e63946',
    'green':   '#2a9d8f',
    'lgreen':  '#d4f1ec',
    'amber':   '#e9c46a',
    'lamber':  '#fdf6d8',
    'gray':    '#6c757d',
    'lgray':   '#f0f0f0',
    'white':   '#ffffff',
}

ASSETS = '/Users/shl/nvidia/qcchem-qml-md/docs/assets'


def save(fig, name, dpi=260):
    fig.savefig(f'{ASSETS}/{name}', dpi=dpi,
                bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f'  saved: {name}')


def _subplots_finalize(fig, **kwargs):
    """
    Prefer explicit margins over tight_layout alone so suptitles / dual panels / footnotes align.
    """
    dfl = {'left': 0.06, 'right': 0.98, 'top': 0.92, 'bottom': 0.10}
    dfl.update(kwargs)
    fig.subplots_adjust(**dfl)


# ─── 1. Why quantum chemistry ─────────────────────────────────────────────────

def fig_why_quantum():
    """
    Left: classical *exact* many-body — Slater determinant basis size (half-filled
    active space) grows combinatorially in n_so. Not comparable to DFT O(M³).

    Right: same active spin-orbital count — qubit count is linear in n_so (JW/BK);
    typical second-quantized two-body Hamiltonian has O(n_so⁴) one-/two-electron
    integrals / Pauli-term budget (still polynomial). State dimension 2^n_so is
    encoded implicitly in qubits, not as a classical amplitude list.

    Layout matches dual-panel benchmarks (classical_quantum_comparison): no
    long transAxes callouts inside axes; footnotes via fig.text; legends placed
    to avoid curve overlap.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14.2, 7.55))
    fig.patch.set_facecolor('white')

    n_so = np.arange(4, 33, 2, dtype=int)
    det_count = np.array([math.comb(int(n), int(n) // 2) for n in n_so], dtype=float)

    # ── Left: FCI-type Slater basis ──
    ax = axes[0]
    ax.set_title(
        r'FCI-type Slater basis ($\frac{1}{2}$-filled active space)',
        fontsize=FS_HEAD,
        fontweight='bold',
        color=C['red'],
        pad=12,
    )
    ax.semilogy(n_so, det_count, 'o-', color=C['red'], lw=2.5, ms=6,
                mfc='white', mew=2, label='CI / FCI basis size')
    ax.fill_between(n_so, 1.0, det_count, alpha=0.12, color=C['red'])
    ax.axhline(1e12, color=C['gray'], ls='--', lw=1.5,
               label=r'$\sim 10^{12}$ coefficients (illustrative cutoff)')
    ax.set_xlabel(r'Active spin-orbitals $n_{\mathrm{so}}$', fontsize=FS_SUB)
    ax.set_ylabel(r'Slater determinants (half-filled)', fontsize=FS_SUB)
    ax.legend(
        fontsize=FS_LEGEND - 1,
        framealpha=0.94,
        loc='lower right',
        borderaxespad=0.8,
        borderpad=0.5,
    )
    ax.set_xlim(2, 34)
    ymin = max(1.0, float(det_count.min()) * 0.35)
    ymax = float(det_count.max()) * 4.0
    ax.set_ylim(ymin, ymax)
    ax.margins(x=0.02)
    ax.grid(True, alpha=0.25, ls='--')

    # ── Right: quantum — linear qubits, polynomial shell ──
    ax = axes[1]
    ax.set_title(
        r'Quantum encoding: qubits $\sim n_{\mathrm{so}}$, shell $\sim n_{\mathrm{so}}^4$',
        fontsize=FS_HEAD,
        fontweight='bold',
        color=C['green'],
        pad=12,
    )
    qubits = n_so.astype(float)
    ham_terms = n_so.astype(float) ** 4
    scale = qubits.max() / ham_terms.max()
    ax.plot(n_so, qubits, 'o-', color=C['green'], lw=2.5, ms=6, mfc='white', mew=2,
            label=r'Physical qubits $\approx n_{\mathrm{so}}$ (JW / BK)')
    ax.plot(n_so, ham_terms * scale, 's--', color=C['amber'], lw=2.0, ms=5,
            mfc='white', mew=1.5,
            label=r'Two-body shell $\propto n_{\mathrm{so}}^4$ (scaled)')
    ax.set_xlabel(r'Active spin-orbitals $n_{\mathrm{so}}$', fontsize=FS_SUB)
    ax.set_ylabel('Resource (arb. units, same scale)', fontsize=FS_SUB)
    ax.legend(
        fontsize=FS_LEGEND - 1,
        framealpha=0.94,
        loc='lower left',
        bbox_to_anchor=(0.04, 0.06),
        borderaxespad=0.0,
        borderpad=0.45,
    )
    ax.set_xlim(2, 34)
    ax.set_ylim(0.0, float(qubits.max()) * 1.22)
    ax.grid(True, alpha=0.25, ls='--')

    fig.subplots_adjust(left=0.09, right=0.985, top=0.84, bottom=0.21, wspace=0.30)

    fig.suptitle(
        'Exact Many-Body Basis vs Quantum Encoding (Active Spin-Orbitals)',
        fontsize=FS_DISPLAY,
        fontweight='bold',
        color=C['navy'],
        y=0.965,
    )

    fig.text(
        0.5,
        0.095,
        'Left: DFT / Kohn–Sham scales as $O(M^3)$ in basis size but is a mean-field + XC model — not this FCI determinant basis.',
        ha='center',
        va='top',
        fontsize=FS_CAPTION - 1,
        color=C['gray'],
        style='italic',
        wrap=True,
        **_serif(),
    )
    fig.text(
        0.5,
        0.048,
        r'Right: Hilbert space $\sim \mathbb{C}^{2^{n_{\mathrm{so}}}}$ is not stored as classical amplitudes; '
        r'VQE / QPE target observables (e.g., energy), not full tomography.',
        ha='center',
        va='top',
        fontsize=FS_CAPTION - 1,
        color=C['gray'],
        style='italic',
        wrap=True,
        **_serif(),
    )

    save(fig, 'why_quantum_chemistry.png')


# ─── 2. Active space and embedding ───────────────────────────────────────────

def fig_active_space():
    fig, ax = plt.subplots(figsize=(14.2, 7.35))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_title('Quantum Embedding: Classical Background + Quantum Active Core',
                 fontsize=FS_DISPLAY, fontweight='bold', color=C['navy'], pad=20)

    # ── Outer molecule (classical region) ──
    outer = FancyBboxPatch((0.4, 0.5), 11.2, 6, boxstyle='round,pad=0.3',
                           facecolor='#f5f5f5', edgecolor=C['gray'], lw=2.5)
    ax.add_patch(outer)
    ax.text(6, 6.2, 'Classical region  (Hartree-Fock / DFT)', ha='center',
            fontsize=FS_BODY, color=C['gray'], style='italic')

    # Draw scattered "background" atoms
    np.random.seed(7)
    for _ in range(28):
        x = np.random.uniform(0.6, 11.6)
        y = np.random.uniform(0.7, 5.8)
        # avoid active core area
        if 3.8 < x < 8.2 and 1.8 < y < 5.2:
            continue
        c = Circle((x, y), 0.18, facecolor='#c8c8c8', edgecolor='#9e9e9e', lw=1.2)
        ax.add_patch(c)

    # ── Active core (quantum region) ──
    core = FancyBboxPatch((3.8, 1.8), 4.4, 3.4, boxstyle='round,pad=0.3',
                          facecolor='#eaf4fb', edgecolor=C['blue'], lw=3)
    ax.add_patch(core)
    ax.text(6, 5.0, 'Quantum active space', ha='center',
            fontsize=FS_SUB, fontweight='bold', color=C['blue'])

    # Draw "active" atoms with orbital lobes
    for (cx, cy, col) in [(5.0, 3.5, C['blue']), (7.0, 3.5, C['red']),
                           (6.0, 2.5, C['green'])]:
        for sign, angle in [(1, 0), (-1, 0), (1, 90), (-1, 90)]:
            lobe = Ellipse((cx + sign * 0.45 * np.cos(np.radians(angle)),
                            cy + sign * 0.45 * np.sin(np.radians(angle))),
                           0.55, 0.28, angle=angle,
                           facecolor=col, alpha=0.4, edgecolor=col, lw=1)
            ax.add_patch(lobe)
        nucleus = Circle((cx, cy), 0.18, facecolor=col, edgecolor='white', lw=1.5)
        ax.add_patch(nucleus)

    # ── Arrows and labels ──
    ax.annotate('', xy=(3.85, 3.5), xytext=(2.0, 3.5),
                arrowprops=dict(arrowstyle='->', color=C['blue'], lw=2.5))
    ax.text(1.4, 3.7, 'Embed\ninterface', ha='center', fontsize=FS_BODY,
            color=C['blue'], fontweight='bold')

    ax.annotate('', xy=(8.15, 3.5), xytext=(10.0, 3.5),
                arrowprops=dict(arrowstyle='<-', color=C['blue'], lw=2.5))
    ax.text(10.6, 3.7, 'Return\nenergy', ha='center', fontsize=FS_BODY,
            color=C['blue'], fontweight='bold')

    # ── Legend boxes ──
    # Legend callouts sized for PT_FIG (~16 pt)
    for (bx, by, bw, bh, fc, ec, label) in [
        (0.48, 0.48, 2.52, 0.95, '#f5f5f5', C['gray'],
         'Classical\n(HF / DFT)'),
        (9.12, 0.48, 2.52, 0.95, '#eaf4fb', C['blue'],
         'Quantum VQE\n(high accuracy)'),
    ]:
        ax.add_patch(FancyBboxPatch((bx, by), bw, bh,
                                   boxstyle='round,pad=0.1',
                                   facecolor=fc, edgecolor=ec, lw=2))
        ax.text(bx + bw / 2, by + bh / 2, label, ha='center', va='center',
                fontsize=FS_INBOX, color=C['navy'])

    plt.tight_layout(pad=0.8)
    save(fig, 'active_space_embedding_sci.png')


def fig_active_space_convergence():
    """
    Schematic convergence of ground-state energy vs active-space size (H2-style trend).
    """
    fig, ax = plt.subplots(figsize=(12.2, 6.55))
    n_orbitals = np.array([2, 4, 6, 8, 10, 12, 14])
    energies = np.array([-1.125, -1.134, -1.137, -1.1372, -1.13725, -1.13728, -1.1373])

    ax.plot(n_orbitals, energies, 's-', color='#7b5295', lw=3.0,
           ms=11, markerfacecolor='white', markeredgewidth=2,
           markeredgecolor='#7b5295', label='VQE-style energy trajectory')

    ax.axvspan(2, 8, alpha=0.14, color=C['blue'], label='NISQ-feasible (2–8 orbitals)')
    ax.axvspan(8.0, 14.05, alpha=0.09, color=C['gray'], label='Larger chemical space')

    fci_lim = energies[-1]
    ax.axhline(fci_lim, color=C['green'], ls='--', lw=2.2,
               label=f'Full CI asymptote  ({fci_lim:.5f} Ha)')

    ax.set_xlabel('Active-space orbitals', fontsize=FS_SUB)
    ax.set_ylabel('Energy  (Hartree)', fontsize=FS_SUB)
    ax.set_title('Energy vs Active Space Size\n(schematic; H$_2$-like trend, JW mapping)',
                fontsize=FS_HEAD, fontweight='bold', color=C['navy'], pad=14)

    lg = ax.legend(
        fontsize=FS_LEGEND,
        framealpha=0.94,
        loc='upper left',
        bbox_to_anchor=(0.01, 0.99),
        borderaxespad=0.35,
        ncol=1,
        borderpad=0.55,
    )
    lg.get_frame().set_edgecolor('#ddd')

    ax.grid(True, alpha=0.28, ls='--')
    ax.set_xlim(0.5, 14.75)
    ax.set_ylim(-1.140, -1.119)

    ax.annotate(
        'Chemical\naccuracy (~1 mHa)',
        xy=(10.0, energies[4]),
        xytext=(11.8, -1.1215),
        fontsize=FS_INBOX, fontweight='bold', color='#6b4899',
        arrowprops=dict(
            arrowstyle='->', color='#6b4899', lw=1.6,
            connectionstyle='arc3,rad=0.25',
            shrinkA=5, shrinkB=4,
        ),
        bbox=dict(boxstyle='round,pad=0.35', facecolor='#f3eefa', edgecolor='#6b4899'),
    )

    _subplots_finalize(fig, bottom=0.12, top=0.90, left=0.10, right=0.98)
    save(fig, 'active_space_convergence.png')


# ─── 3. Molecular orbitals ────────────────────────────────────────────────────

def fig_molecular_orbitals():
    fig, axes_arr = plt.subplots(1, 3, figsize=(15.5, 7.05))
    fig.patch.set_facecolor('white')

    titles = ['HOMO-1\n(bonding σ)', 'HOMO\n(non-bonding π)', 'LUMO\n(anti-bonding π*)']
    colors_pos = [C['blue'], C['blue'], C['red']]
    colors_neg = [C['red'], C['red'], C['blue']]
    shapes = ['ellipse', 'lobe', 'lobe_anti']

    for col, (title, cp, cn, ax) in enumerate(zip(titles, colors_pos, colors_neg, axes_arr)):
        ax.set_xlim(-3, 3)
        ax.set_ylim(-2.5, 2.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(title, fontsize=FS_SUB, fontweight='bold',
                     color=C['navy'], pad=10)

        # nuclei
        for nx in [-0.9, 0.9]:
            ax.add_patch(Circle((nx, 0), 0.22,
                                facecolor=C['amber'], edgecolor=C['navy'], lw=2))

        if shapes[col] == 'ellipse':
            # sigma bonding: single lobe spanning both nuclei
            ax.add_patch(Ellipse((0, 0), 2.8, 1.2,
                                 facecolor=cp, alpha=0.45,
                                 edgecolor=cp, lw=1.5))
        elif shapes[col] == 'lobe':
            # pi bonding: two lobes above/below
            for dy, fc in [(0.9, cp), (-0.9, cn)]:
                ax.add_patch(Ellipse((0, dy), 2.4, 0.9,
                                     facecolor=fc, alpha=0.45,
                                     edgecolor=fc, lw=1.5))
        elif shapes[col] == 'lobe_anti':
            # pi anti-bonding: lobes split left/right with node
            for (lx, fc) in [(-0.9, cp), (0.9, cn)]:
                for dy in [0.9, -0.9]:
                    ax.add_patch(Ellipse((lx, dy), 1.1, 0.9,
                                         facecolor=fc, alpha=0.4,
                                         edgecolor=fc, lw=1.5))
            # node line
            ax.axvline(0, color=C['gray'], lw=1.5, ls='--', alpha=0.6)
            ax.text(0.08, -2.2, 'node', fontsize=FS_INBOX,
                    color=C['gray'], style='italic')

        # legend patches
        pos_patch = mpatches.Patch(facecolor=cp, alpha=0.6, label='+  phase')
        neg_patch = mpatches.Patch(facecolor=cn, alpha=0.6, label='–  phase')
        ax.legend(handles=[pos_patch, neg_patch], loc='lower center',
                  fontsize=FS_LEGEND,
                  framealpha=0.92, bbox_to_anchor=(0.5, -0.04), ncol=2,
                  columnspacing=0.85)

    fig.suptitle('Molecular Orbitals: Electron Probability Distributions',
                 fontsize=FS_DISPLAY, fontweight='bold', color=C['navy'], y=0.98)
    plt.tight_layout(rect=[0, 0.05, 1, 0.94], pad=1.05, w_pad=2.8)
    save(fig, 'molecular_orbitals_sci.png')


# ─── 4. InQuanto architecture ─────────────────────────────────────────────────

def fig_inquanto_workflow():
    """Three pillars only (no bottom 'Key characteristics' panel)."""
    # Text block vertically centered in each pillar; uniform line spacing (transAxes units).
    fig, ax = plt.subplots(figsize=(12.5 * _FLOW_FIG_K, 5.45 * _FLOW_FIG_K))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title(
        'InQuanto — Three-Pillar Commercial Workflow  (Quantinuum)',
        fontsize=WF_FS, fontweight='bold', color='#c0392b', pad=10,
    )

    pillar_floor = 0.128
    pillar_top_budget = 0.848
    ph = pillar_top_budget - pillar_floor - 0.016
    y0 = pillar_floor
    pw = 0.252
    item_wrap = 22
    # Uniform inter-line step; last-line descent ~ one step for vertical centering.
    lh_line = _AX_LH_FLOW * 1.06
    gap_title_items = _AX_LH_FLOW * 0.62
    gap_bullets = _AX_LH_FLOW * 0.48

    pillar_cfg = [
        (0.168, 'Chemical Specification', '#fde8e8', '#c0392b',
         ['FermionSpace', 'Active space selection', 'InQuanto-PySCF extensions',
          'Geometry · charge · spin']),
        (0.50, 'Program Construction', '#fef9e7', '#d4ac0d',
         ['AlgorithmVQE / ADAPT', 'Computable objects', 'TKET pass bundles', 'Noise models']),
        (0.83, 'Execution & Analysis', '#e9f7ef', '#1e8449',
         ['Nexus cloud submit', 'H-Series hardware', 'HQC billing / credits',
          'Results · error mitigation']),
    ]

    def _pillar_lines(title, items):
        """List of (kind, text) in order; compute block height for centering."""
        ordered = []
        for line in _wrap(title, item_wrap).split('\n'):
            ordered.append(('title', line))
        ordered.append(('gap', gap_title_items))
        for bi, item in enumerate(items):
            for line in _wrap(f'· {item}', item_wrap).split('\n'):
                ordered.append(('body', line))
            if bi < len(items) - 1:
                ordered.append(('gap', gap_bullets))
        down = 0.0
        placements = []  # (kind, text, y_from_first_top) y increases downward in "layout space"
        for kind, val in ordered:
            if kind == 'gap':
                down += val
            else:
                placements.append((kind, val, down))
                down += lh_line
        block_h = down
        return placements, block_h

    y_arrow = y0 + ph * 0.44
    for cx, title, fc, ec, items in pillar_cfg:
        x0 = cx - pw / 2
        ax.add_patch(
            FancyBboxPatch(
                (x0, y0), pw, ph,
                transform=ax.transAxes,
                boxstyle='round,pad=0.010', facecolor=fc, edgecolor=ec, lw=1.85,
            )
        )
        placements, block_h = _pillar_lines(title, items)
        box_cy = y0 + ph / 2
        # First line top (va='top'): center block of height block_h in [y0, y0+ph].
        y_first_top = box_cy + block_h / 2
        for kind, text, d in placements:
            y = y_first_top - d
            ax.text(
                cx, y, text, transform=ax.transAxes,
                ha='center', va='top', fontsize=WF_FS,
                fontweight='bold' if kind == 'title' else 'normal',
                color='#2c3e50' if kind == 'title' else '#444',
                linespacing=LS_BOX_TITLE if kind == 'title' else LS_BOX_BODY,
                **_serif(),
            )

    # Arrows in the gaps between narrower pillars (centers 0.168 / 0.50 / 0.83, pw=0.252)
    for x0, x1 in [(0.308, 0.362), (0.638, 0.692)]:
        ax.annotate(
            '', xy=(x1, y_arrow), xytext=(x0, y_arrow),
            xycoords=ax.transAxes, textcoords=ax.transAxes,
            arrowprops=dict(
                arrowstyle='-|>',
                color=C['gray'],
                lw=2.1,
                mutation_scale=11,
                shrinkA=2,
                shrinkB=2,
            ),
        )

    plt.tight_layout()
    save(fig, 'inquanto_workflow.png')


# ─── 5. Tangelo workflow ──────────────────────────────────────────────────────

def fig_tangelo_workflow():
    """TransAxes layout; taller step boxes separate title vs description to avoid overlap at 14 pt."""
    fig, (ax_main, ax_side) = plt.subplots(
        1, 2, figsize=(15.4 * _FLOW_FIG_K, 9.55 * _FLOW_FIG_K),
        gridspec_kw={'width_ratios': [2.12, 1], 'wspace': 0.055},
    )

    ax_main.set_xlim(0, 1)
    ax_main.set_ylim(0, 1)
    ax_main.axis('off')
    # pad: distance (pt) from axes top to title — smaller ⇒ title sits closer / lower to first row.
    ax_main.set_title(
        'Tangelo — Research Toolbox Workflow  (SandboxAQ)',
        fontsize=WF_FS, fontweight='bold', color=C['blue'], pad=2,
    )

    step_specs = [
        ('SecondQuantizedMolecule', '#dbe4ff', C['blue'],
         'xyz / SMILES | charge | spin | basis set | PySCF / Psi4 backend'),
        ('Solver options (Python dict)', '#d3f9d8', C['green'],
         'ansatz: UCCSD / HEA / ADAPT | mapping: JW / BK | backend: qulacs / qiskit'),
        ('solver.build()', '#fff3bf', '#e67700',
         'mean-field SCF → fermionic H → ansatz circuit → simulator init'),
        ('solver.simulate()', '#ffc9c9', C['red'],
         'optimizer loop (L-BFGS-B / COBYLA) → converged energy'),
        ('Post-analysis', '#ffd8a8', '#d4520d',
         'get_resources() | get_rdm() | export circuit | plot'),
    ]

    n = len(step_specs)
    top_band = 0.908
    bot_band = 0.068
    span = max(0.001, top_band - bot_band)
    min_gap = 0.024  # vertical gap between boxes (transAxes)
    bh = min(0.168, (span - min_gap * (n - 1)) / n)
    centers_span = bot_band + bh / 2 + 0.012, top_band - bh / 2 - 0.006
    # transAxes: larger y is visually higher — first step (index 0) must sit at the TOP.
    cys = np.linspace(centers_span[1], centers_span[0], n)
    bw = 0.86
    cx = 0.5
    # Step subtitles: keep each logical line on one row (avoid premature wrap at 46 chars).
    _wrap_main_desc = 88
    # Right column bullets: 34 was breaking lines like "· Black-box: …" mid-sentence.
    _wrap_side_item = 54
    # Right-hand rail so flow arrows never cross centered text
    x_rail = cx + bw / 2 + 0.032

    for cy, (title, fc, ec, desc) in zip(cys, step_specs):
        ax_main.add_patch(
            FancyBboxPatch(
                (cx - bw / 2, cy - bh / 2), bw, bh,
                transform=ax_main.transAxes,
                boxstyle='round,pad=0.022', facecolor=fc, edgecolor=ec, lw=2,
            )
        )
        y_top_inside = cy + bh / 2 - 0.032
        ax_main.text(
            cx, y_top_inside, title, ha='center', va='top', fontsize=WF_FS,
            fontweight='bold', color='#2c3e50',
            linespacing=LS_BOX_TITLE, **_serif(),
        )
        wdesc = _wrap(desc.replace('  ', ' '), _wrap_main_desc)
        ax_main.text(
            cx,
            y_top_inside - 0.050,
            wdesc,
            ha='center',
            va='top',
            fontsize=WF_FS,
            linespacing=LS_BOX_BODY,
            color='#444',
            style='italic',
            **_serif(),
        )

    for cy_u, cy_d in zip(cys[:-1], cys[1:]):
        y_a = cy_u - bh / 2 - 0.003
        y_b = cy_d + bh / 2 + 0.003
        ax_main.annotate(
            '',
            xy=(x_rail, y_b),
            xytext=(x_rail, y_a),
            xycoords=ax_main.transAxes,
            textcoords=ax_main.transAxes,
            arrowprops=dict(
                arrowstyle='->',
                color=C['blue'],
                lw=2.4,
                shrinkA=0,
                shrinkB=0,
            ),
        )

    # Right column: total height matches left workflow band (from first box top to last box bottom).
    y_flow_top = cys[0] + bh / 2
    y_flow_bot = cys[-1] - bh / 2
    flow_span = max(0.02, y_flow_top - y_flow_bot)
    gap_mid = 0.022
    h_each = (flow_span - gap_mid) / 2
    bx = 0.042
    bw_box = 0.916
    # Lower box = Limitations, upper = Strengths (same order as before, tops aligned to flow).
    by_lim = y_flow_bot
    bh_lim = h_each
    by_str = y_flow_bot + h_each + gap_mid
    bh_str = h_each

    ax_side.set_xlim(0, 1)
    ax_side.set_ylim(0, 1)
    ax_side.axis('off')

    lh_s = _AX_LH_FLOW * 1.05
    pad_x = 0.038
    for by, bh_box, fc, ec, title, items in [
        (by_str, bh_str, '#eaf4fb', C['blue'], 'Strengths',
         ['Easy to prototype', 'Flexible dict config', '20+ built-in solvers',
          'Multi-backend (linq)', 'VQE/ADAPT/QPE/DMET']),
        (by_lim, bh_lim, '#fff5f5', C['red'], 'Limitations',
         ['Loose contracts (easy to mistype)', 'Black-box: PySCF hidden inside solver',
          'Hard to extract intermediate logs', 'No production job management',
          'Weak repro / audit trail']),
    ]:
        ax_side.add_patch(
            FancyBboxPatch(
                (bx, by), bw_box, bh_box,
                transform=ax_side.transAxes,
                boxstyle='round,pad=0.024', facecolor=fc, edgecolor=ec, lw=2,
            )
        )
        color = C['blue'] if title == 'Strengths' else C['red']
        ax_side.text(
            bx + bw_box / 2,
            by + bh_box - 0.036,
            title,
            ha='center',
            va='top',
            fontsize=WF_FS,
            fontweight='bold',
            color=color,
            linespacing=LS_BOX_TITLE,
            **_serif(),
        )
        y_cur = by + bh_box - 0.082
        for item in items:
            for line in _wrap(f'· {item}', _wrap_side_item).split('\n'):
                ax_side.text(
                    bx + pad_x,
                    y_cur,
                    line,
                    fontsize=WF_FS,
                    color='#333',
                    va='top',
                    ha='left',
                    **_serif(),
                )
                y_cur -= lh_s
            y_cur -= 0.012

    fig.subplots_adjust(left=0.04, right=0.99, top=0.94, bottom=0.05, wspace=0.055)
    save(fig, 'tangelo_workflow_detailed.png')


# ─── 6. Three-platform capability comparison ─────────────────────────────────

def fig_three_platform():
    categories = ['Algorithm\nbreadth', 'Config\ndiscipline', 'Auditability\n& Repro',
                  'Hardware\nfreedom', 'MD / ML\nintegration', 'Cloud\nmaturity']
    scores = {
        'InQuanto\n(Commercial)': [4, 5, 2, 2, 2, 5],
        'Tangelo\n(Open Source)': [5, 2, 2, 4, 3, 2],
        'qchem-stack\n(Our Platform)': [3, 5, 5, 4, 4, 3],
    }
    colors = [C['red'], C['blue'], C['green']]

    fig, ax = plt.subplots(figsize=(14.2, 7.55))
    n_cats = len(categories)
    n_plat = len(scores)
    x = np.arange(n_cats)
    width = 0.22

    for i, (name, sc, col) in enumerate(zip(scores, scores.values(), colors)):
        offset = (i - 1) * (width + 0.03)
        bars = ax.bar(x + offset, sc, width, label=name,
                      color=col, alpha=0.82, edgecolor='white', lw=1.2)
        for bar, s in zip(bars, sc):
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.08, str(s),
                    ha='center', va='bottom', fontsize=FS_BODY,
                    fontweight='bold', color=col)

    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=FS_BODY)
    ax.set_yticks(range(6))
    ax.set_ylim(0, 6.0)
    ax.set_ylabel('Score  (1 = weak  …  5 = strong)', fontsize=FS_SUB)
    ax.set_title('Platform Capability Comparison  (qualitative scores)',
                 fontsize=FS_DISPLAY, fontweight='bold', color=C['navy'], pad=16)
    ax.legend(loc='upper left', fontsize=FS_LEGEND, framealpha=0.92)
    ax.grid(axis='y', alpha=0.3, ls='--')
    ax.set_facecolor('#fafafa')
    for spine in ax.spines.values():
        spine.set_linewidth(1.2)
        spine.set_color(C['gray'])

    plt.setp(ax.get_xticklabels(), rotation=11, ha='right', rotation_mode='anchor')
    _subplots_finalize(fig, bottom=0.20, left=0.07, top=0.93, right=0.98)
    save(fig, 'three_platform_radar.png')


# ─── 7. Workflow philosophy comparison ───────────────────────────────────────

def fig_workflow_philosophy():
    """
    Three stacked rows (one platform each): horizontal L→R workflow in each row,
    [+]/[-] trade-offs below the flow. Typography uses WF_FS (flow-diagram scale).
    """
    fig = plt.figure(figsize=(15.35 * _FLOW_FIG_K, 7.75 * _FLOW_FIG_K))
    # Very tight vertical gutter between the three workflow rows.
    gs = fig.add_gridspec(3, 1, height_ratios=[1, 1, 1],
                          left=0.055, right=0.983, top=0.912, bottom=0.028,
                          hspace=0.032)
    fig.suptitle('Three Workflow Philosophies', fontsize=WF_FS,
                 fontweight='bold', color=C['navy'], y=0.962)

    rows = [
        (C['red'], 'InQuanto', 'Enterprise Cloud-Native',
         ['YAML / Config', 'FermionSpace', 'Nexus Cloud', 'H-Series HW'],
         'Complete product ecosystem, deeply vendor-integrated.',
         'Closed ecosystem, HQC billing, hard to use outside Quantinuum infra.'),
        (C['blue'], 'Tangelo', 'Research Notebook-Centric',
         ['Python dict', 'Solver object', 'build()', 'simulate()'],
         'Maximum flexibility for quick prototyping in Jupyter notebooks.',
         'Loose contracts, black-box internals, weak audit / repro trail.'),
        (C['green'], 'qchem-stack', 'Engineered Open Platform',
         ['Strict YAML', 'Explicit pipeline', 'Multi-backend', 'Strict repro'],
         'Industrial discipline plus open architecture: reproducible, portable science.',
         'More upfront design cost; pays back at scale and for publications.'),
    ]

    step_w, step_h = 0.206, 0.132
    gap_h = 0.018
    x0_row = 0.024
    mid_y = 0.548
    # ≥17 chars keeps "Explicit pipeline" on one line (wrap 16 broke after "Explicit").
    wrap_step = 22
    wrap_prose = 114
    prose_gap_below_flow = 0.034

    for row_i, row in enumerate(rows):
        ax = fig.add_subplot(gs[row_i])
        col, name, subtitle, flow_steps, pro, con = row
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')

        # Platform name vs subtitle: keep a clear vertical gap (was 0.936 / 0.864 — too tight).
        ax.text(
            0.026, 0.940, name,
            fontsize=WF_FS, fontweight='bold', color=col,
            transform=ax.transAxes, va='top',
        )
        ax.text(
            0.026, 0.818, subtitle,
            fontsize=WF_FS,
            style='italic', color=C['gray'], transform=ax.transAxes,
            va='top',
        )

        for i, step in enumerate(flow_steps):
            bx = x0_row + i * (step_w + gap_h)
            ax.add_patch(
                FancyBboxPatch(
                    (bx, mid_y - step_h / 2), step_w, step_h,
                    transform=ax.transAxes,
                    boxstyle='round,pad=0.019',
                    facecolor=col,
                    alpha=0.17,
                    edgecolor=col,
                    lw=1.8,
                )
            )
            ax.text(
                bx + step_w / 2, mid_y,
                _wrap(step, wrap_step),
                ha='center', va='center', fontsize=WF_FS,
                linespacing=LS_BOX_TITLE,
                fontweight='bold', color='#2c3e50',
                **_serif(),
            )
            if i < len(flow_steps) - 1:
                ax.annotate(
                    '',
                    xy=(bx + step_w + gap_h - 0.002, mid_y),
                    xytext=(bx + step_w + 0.002, mid_y),
                    xycoords=ax.transAxes, textcoords=ax.transAxes,
                    arrowprops=dict(
                        arrowstyle='-|>',
                        color=col,
                        lw=2.05,
                        mutation_scale=10,
                        shrinkA=2,
                        shrinkB=2,
                    ),
                )

        box_bottom = mid_y - step_h / 2
        prose_anchor = box_bottom - prose_gap_below_flow
        wp = '[+] ' + _wrap(pro, wrap_prose)
        wm = '[-] ' + _wrap(con, wrap_prose)

        wrapped_len_p = max(1, _nl(wp))
        ax.text(
            0.024, prose_anchor,
            wp, fontsize=WF_FS,
            color='#1e8449', va='top', transform=ax.transAxes,
            linespacing=LS_BOX_BODY, **_serif(),
        )
        gap_pro_con = 0.066
        y_con_start = prose_anchor - wrapped_len_p * _AX_LH_FLOW * LS_BOX_BODY - gap_pro_con
        ax.text(
            0.024,
            y_con_start,
            wm,
            fontsize=WF_FS,
            color='#c0392b',
            va='top',
            transform=ax.transAxes,
            linespacing=LS_BOX_BODY,
            **_serif(),
        )

    save(fig, 'workflow_philosophy_comparison.png')


# ─── 8. qchem-stack pipeline flow ────────────────────────────────────────────

def fig_qchem_pipeline():
    """Saves ``comparison_flow.png`` — WF_FS typography; canvas scaled by `_FLOW_FIG_K`."""
    # Figure-specific balance: align with other workflow figures while keeping this
    # dense 6-stage canvas readable after document embedding.
    _pipe_k = 1.08
    _pipe_fs = 18.2
    fig, ax = plt.subplots(figsize=(17.9 * _pipe_k, 8.85 * _pipe_k))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_title(
        'qchem-stack: End-to-End Pipeline Architecture',
        fontsize=_pipe_fs + 0.8, fontweight='bold', color=C['navy'], pad=-11,
    )

    n_stages = 6
    bw = 0.136
    g_gap = 0.019
    span = n_stages * bw + (n_stages - 1) * g_gap
    pad_side = (1 - span) / 2
    centers_x = [pad_side + bw / 2 + i * (bw + g_gap) for i in range(n_stages)]
    # Six main stage boxes: slightly taller than previous compact variant for better
    # semantic grouping between stage title and stage detail.
    _bh_prev = 0.432
    bh = _bh_prev * 0.63
    cy = 0.662
    # Title in upper half, body in lower half of the shorter box.
    y_title = cy + bh * 0.200
    y_body = cy - bh * 0.200

    stages_meta = [
        ('YAML Config\n(Pydantic)', C['navy'], '#e8eef7',
         'ExperimentConfig schema\nstrict validation + defaults'),
        ('Classical Driver\n(PySCF)', C['blue'], '#dbe4ff',
         'RHF / ROHF / UHF | ddCOSMO / PBC\nchemistry context extraction'),
        ('Hamiltonian\nCompiler', '#d4520d', '#fdebd0',
         'Active-space integrals\nJW / BK / SCBK mapping'),
        ('Quantum Algorithm\nLayer', C['green'], '#d4f1ec',
         'VQE / ADAPT / IQEB\nUCCSD / VQD / QSE'),
        ('Pauli Measurement\nProtocol', '#b8860b', '#fdf6d8',
         'Commuting groups + shot budget\ncircuit IR / execution plan'),
        ('Reproducibility\nExport', C['gray'], '#f0f0f0',
         'SHA-256 fingerprint\nstrict JSON artifact log'),
    ]

    for cx, (title, ec, fc, desc) in zip(centers_x, stages_meta):
        ax.add_patch(
            FancyBboxPatch(
                (cx - bw / 2, cy - bh / 2), bw, bh,
                transform=ax.transAxes,
                boxstyle='round,pad=0.014',
                facecolor=fc,
                edgecolor=ec,
                lw=2.2,
            )
        )
        ax.text(
            cx, y_title, title, ha='center', va='bottom',
            fontsize=_pipe_fs,
            fontweight='bold',
            color='#2c3e50',
            linespacing=LS_BOX_TITLE,
            **_serif(),
        )
        ax.text(
            cx, y_body, desc,
            ha='center',
            va='top',
            fontsize=_pipe_fs,
            style='italic',
            color='#555',
            linespacing=LS_BOX_BODY,
            **_serif(),
        )

    ay = cy
    for i in range(n_stages - 1):
        x0 = centers_x[i] + bw / 2 + 0.008
        x1 = centers_x[i + 1] - bw / 2 - 0.008
        ax.annotate(
            '',
            xy=(x1, ay),
            xytext=(x0, ay),
            xycoords=ax.transAxes,
            textcoords=ax.transAxes,
            arrowprops=dict(
                arrowstyle='-|>',
                color=C['gray'],
                lw=2.15,
                mutation_scale=14,
                shrinkA=4,
                shrinkB=4,
            ),
        )

    _bx_h_prev = 0.288
    bx_h = _bx_h_prev * 0.6
    # Vertical gap between pipeline row (bottom) and footer row (top) → 1/3 of previous layout.
    y_pipeline_bottom = cy - bh / 2
    _bx_yy_prev = 0.036
    y_footer_top_prev = _bx_yy_prev + bx_h
    gap_prev = y_pipeline_bottom - y_footer_top_prev
    gap_new = max(0.012, gap_prev / 3.0)
    bx_yy = y_pipeline_bottom - gap_new - bx_h
    bx_yy = max(0.02, bx_yy)

    bx_w = 0.434
    gap_pair = 0.038
    bx_lo = (1.0 - (2 * bx_w + gap_pair)) / 2
    bx_r = bx_lo + bx_w + gap_pair
    head_inset = 0.026
    body_y_frac = 0.42
    # Footer API lines: keep on one row (match driver/tangelo wrap width); `{id}` needs parse_math=False.
    wrap_footer = 96
    ax.add_patch(
        FancyBboxPatch(
            (bx_lo, bx_yy), bx_w, bx_h,
            transform=ax.transAxes,
            boxstyle='round,pad=0.02',
            facecolor='#f5fff5',
            edgecolor=C['green'],
            lw=2,
        )
    )
    ax.text(
        bx_lo + bx_w / 2,
        bx_yy + bx_h - head_inset,
        'FastAPI Job Orchestrator',
        ha='center',
        va='top',
        fontsize=_pipe_fs,
        fontweight='bold',
        color=C['green'],
        linespacing=LS_BOX_TITLE,
        **_serif(),
    )
    ax.text(
        bx_lo + bx_w / 2,
        bx_yy + bx_h * body_y_frac,
        _wrap(
            'POST /v1/runs  |  GET /v1/jobs/{id}  |  workflow preview',
            wrap_footer,
        ),
        ha='center',
        va='center',
        fontsize=_pipe_fs,
        color='#444',
        linespacing=LS_BOX_BODY,
        parse_math=False,
        **_serif(),
    )
    ax.add_patch(
        FancyBboxPatch(
            (bx_r, bx_yy),
            bx_w,
            bx_h,
            transform=ax.transAxes,
            boxstyle='round,pad=0.02',
            facecolor='#f0f4ff',
            edgecolor=C['blue'],
            lw=2,
        )
    )
    ax.text(
        bx_r + bx_w / 2,
        bx_yy + bx_h - head_inset,
        'Pluggable Execution Backends',
        ha='center',
        va='top',
        fontsize=_pipe_fs,
        fontweight='bold',
        color=C['blue'],
        linespacing=LS_BOX_TITLE,
        **_serif(),
    )
    ax.text(
        bx_r + bx_w / 2,
        bx_yy + bx_h * body_y_frac,
        _wrap(
            'statevector (exact)  |  Qiskit Aer (shots)  |  IonStack (real hardware)',
            wrap_footer,
        ),
        ha='center',
        va='center',
        fontsize=_pipe_fs,
        linespacing=LS_BOX_BODY,
        color='#444',
        parse_math=False,
        **_serif(),
    )

    y_conn = cy - bh / 2 - 0.026
    dash_kw = dict(arrowstyle='<->', color=C['green'], lw=1.95, ls='dashed',
                   shrinkA=5, shrinkB=5)
    dash_kw_blue = dict(arrowstyle='<->', color=C['blue'], lw=1.95, ls='dashed',
                       shrinkA=5, shrinkB=5)
    ax.annotate(
        '',
        xy=(bx_lo + bx_w / 2, bx_yy + bx_h + 0.012),
        xytext=(centers_x[1], y_conn),
        xycoords=ax.transAxes,
        textcoords=ax.transAxes,
        arrowprops=dash_kw,
    )
    ax.annotate(
        '',
        xy=(bx_r + bx_w / 2, bx_yy + bx_h + 0.012),
        xytext=(centers_x[4], y_conn),
        xycoords=ax.transAxes,
        textcoords=ax.transAxes,
        arrowprops=dash_kw_blue,
    )

    fig.subplots_adjust(left=0.055, right=0.985, top=0.994, bottom=0.052)
    save(fig, 'comparison_flow.png')


# ─── 9. Driver interface design ───────────────────────────────────────────────

def fig_driver_interface():
    """
    One pipeline layer per subplot row so headings / body text cannot spill onto
    neighbouring layers (overlap seen when everything shared one axes 0–1 frame).
    """
    fig = plt.figure(figsize=(14.35 * _FLOW_FIG_K, 10.45 * _FLOW_FIG_K))
    gs = fig.add_gridspec(
        1,
        2,
        figure=fig,
        width_ratios=[3.15, 1.06],
        left=0.048,
        right=0.96,
        top=0.90,
        bottom=0.055,
        wspace=0.15,
    )
    # Left: shorter boxes (centered in each row) + tighter gutter vs right silhouette.
    _bh_left = 0.52
    _bb_left = (1 - _bh_left) / 2
    sub_main = gs[0, 0].subgridspec(5, 1, hspace=0.050)
    # Same wide wrap as Tangelo workflow body — avoid mid-sentence breaks (was 46).
    _wrap_driver_body = 88
    fig.suptitle(
        'qchem-stack: Classical-to-Quantum Pipeline',
        fontsize=WF_FS,
        fontweight='bold',
        color=C['navy'],
        y=0.965,
        **_serif(),
    )

    layers = [
        ('#e8eef7', C['navy'],
         'ExperimentConfig  (YAML, Pydantic)',
         'molecule | scf.method | active_space | chemistry_extended'),
        ('#d4f1ec', C['green'],
         'PySCFDriver  (Unified Interface)',
         'from_config(cfg) → run_rhf() / ROHF / UHF / PBC gamma-k\n'
         'Extensions: ddCOSMO solvent | k-mesh | CASSCF audit'),
        ('#fdebd0', '#d4520d',
         'Hamiltonian + Mapping',
         'active_space_integrals() → InteractionOperator\n'
         'JW / BK / symmetry-conserving BK → QubitHamiltonian'),
        ('#efe6ff', '#7b2cbf',
         'Quantum Algorithm Layer',
         'VQE / ADAPT-VQE / IQEB | UCCSD / VQD / QSE\n'
         'Algorithms consume QubitHamiltonian, not PySCF objects'),
        ('#fde8e8', C['red'],
         'Measurement + Repro Export',
         'Pauli grouping | shot budget | backend execution plan\n'
         'energy trace + SHA-256 fingerprint + strict JSON log'),
    ]

    for i, (fc, ec, title, desc) in enumerate(layers):
        ax = fig.add_subplot(sub_main[i, 0])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.add_patch(
            FancyBboxPatch(
                (0.034, _bb_left),
                0.932,
                _bh_left,
                transform=ax.transAxes,
                boxstyle='round,pad=0.028',
                facecolor=fc,
                edgecolor=ec,
                lw=2.1,
            ),
        )
        if '\n' in desc:
            dtxt = '\n'.join(
                _wrap(part.replace('  ', ' '), _wrap_driver_body)
                for part in desc.split('\n')
            )
        else:
            dtxt = _wrap(desc.replace('  ', ' '), _wrap_driver_body)
        yt = _bb_left + _bh_left - 0.030
        yc = _bb_left + _bh_left / 2
        ax.text(
            0.5,
            yt,
            title,
            ha='center',
            va='top',
            fontsize=WF_FS,
            fontweight='bold',
            color='#2c3e50',
            linespacing=LS_BOX_TITLE,
            **_serif(),
        )
        ax.text(
            0.5,
            yc,
            dtxt,
            ha='center',
            va='center',
            fontsize=WF_FS,
            color='#444',
            style='italic',
            linespacing=LS_BOX_BODY,
            **_serif(),
        )
        if i < len(layers) - 1:
            ax.annotate(
                '',
                xy=(0.52, -0.055),
                xytext=(0.52, -0.020),
                xycoords='axes fraction',
                textcoords='axes fraction',
                arrowprops=dict(
                    arrowstyle='-|>',
                    color=C['gray'],
                    lw=2.05,
                    mutation_scale=10,
                    shrinkA=2,
                    shrinkB=2,
                ),
                clip_on=False,
            )

    ax_sb = fig.add_subplot(gs[0, 1])
    ax_sb.set_xlim(0, 1)
    ax_sb.set_ylim(0, 1)
    ax_sb.axis('off')
    ax_sb.add_patch(
        FancyBboxPatch(
            (0.06, 0.10),
            0.88,
            0.80,
            transform=ax_sb.transAxes,
            boxstyle='round,pad=0.034',
            facecolor='#f8fbff',
            edgecolor=C['blue'],
            lw=1.65,
        ),
    )
    scx = 0.5
    ax_sb.text(
        scx,
        0.875,
        'Key design',
        ha='center',
        va='top',
        fontsize=WF_FS,
        fontweight='bold',
        color=C['blue'],
        linespacing=LS_BOX_TITLE,
        **_serif(),
    )
    # Heading → bullets air (aligned with Tangelo / workflow_philosophy panel spacing).
    y_b = 0.690
    _key_line_step = 0.145
    for t in [
        'Classical tools\nstop at boundary',
        'Algorithms see\nQubitHamiltonian',
        'Backend + measurement\nare pluggable',
        'Full audit via\nrepro log',
    ]:
        ax_sb.text(
            scx,
            y_b,
            f'· {t}',
            ha='center',
            va='top',
            fontsize=WF_FS - 2.6,
            color='#333',
            linespacing=LS_BOX_BODY,
            **_serif(),
        )
        y_b -= _key_line_step

    save(fig, 'driver_interface_design.png')


# ─── 10. VQE convergence (reference data) ────────────────────────────────────

def fig_vqe_convergence():
    """
    H$_2$ / sto-3g **UCCSD** (JW): bounded **L-BFGS-B** energy-evaluation trace for the packaged figure
    config (see ``configs/example_h2_vqe_figure_near_casci.yaml`` + export script).

    Data: ``docs/assets/data/vqe_h2_sto3g_jw_near_casci_trace.json`` (regenerate with
    ``PYTHONPATH=src python docs/assets/export_vqe_convergence_trace.py``).
    """
    data_path = Path(__file__).resolve().parent / "data" / "vqe_h2_sto3g_jw_near_casci_trace.json"
    if not data_path.is_file():
        raise FileNotFoundError(
            f"Missing {data_path}; run from repo root:\n"
            "  PYTHONPATH=src python docs/assets/export_vqe_convergence_trace.py"
        )
    js = json.loads(data_path.read_text(encoding="utf-8"))
    energies = [float(x) for x in js["energy_trace_ha"]]
    ref = float(js["reference_casci_total_ha"]) if js.get("reference_casci_total_ha") is not None else float(
        js["exact_ground_in_active_space_ha"]
    )
    n_eval = len(energies)
    if n_eval < 2:
        raise ValueError("energy_trace_ha must contain at least two evaluations")

    xs = np.arange(n_eval, dtype=float)
    ys = np.asarray(energies, dtype=float)
    # Keep the trace fully real (no smoothing): add cumulative minimum for storytelling.
    ys_best = np.minimum.accumulate(ys)
    final_e = float(ys[-1])
    err_mha = abs(final_e - ref) * 1000.0
    y_min = float(min(np.min(ys_best), ref))
    y_max = float(max(np.max(ys_best), ref))
    y_pad = max(8e-4, 0.20 * (y_max - y_min))

    fig, ax = plt.subplots(figsize=(12, 6.5))
    # Monotone "best so far" from real trace.
    ax.step(
        xs,
        ys_best,
        where="post",
        color=C["navy"],
        lw=2.8,
        label="Best-so-far energy (cumulative minimum)",
        zorder=4,
    )

    ax.axhline(ref, color=C["red"], ls="--", lw=2, label=f"CASCI reference  ({ref:.5f} Ha)")
    ax.axhspan(ref - 0.001, ref + 0.001, alpha=0.15, color=C["green"], label="Chemical accuracy  (±1 mHa)")
    ax.plot([xs[-1]], [final_e], marker="o", ms=8, color=C["green"], zorder=6)
    ax.text(
        0.02,
        0.98,
        f"Final: {final_e:.6f} Ha\n|Δ vs CASCI|: {err_mha:.3f} mHa",
        transform=ax.transAxes,
        fontsize=FS_INBOX,
        color="#1b4332",
        va="top",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.28", fc="#e8f5e9", ec=C["green"]),
        **_serif(),
    )

    ax.set_xlabel("L-BFGS-B evaluation index", fontsize=FS_SUB)
    ax.set_ylabel("Energy  (Hartree)", fontsize=FS_SUB)
    cfg_id = js.get("experiment_id", "")
    sub = f"[Recorded trace — {js.get('config_path', 'configs/example_h2.yaml')}"
    if cfg_id:
        sub += f", {cfg_id}"
    sub += "]"
    ax.set_title(
        "H$_2$ VQE / UCCSD  (sto-3g, JW mapping, bounded L-BFGS-B)\n" + sub,
        fontsize=FS_HEAD,
        fontweight="bold",
        color=C["navy"],
    )
    ax.legend(
        fontsize=FS_LEGEND,
        framealpha=0.93,
        loc='center left',
        bbox_to_anchor=(1.0, 0.5),
        borderpad=0.55,
        ncol=1,
    )
    ax.grid(True, alpha=0.25, ls="--")
    ax.set_xlim(0, float(n_eval - 1))
    ax.set_ylim(y_min - y_pad, y_max + y_pad)

    _subplots_finalize(fig, bottom=0.12, top=0.92, right=0.78)
    save(fig, "vqe_convergence_demo.png")


# ─── 11. Classical vs quantum energy comparison ───────────────────────────────

def fig_classical_quantum():
    """Classical-vs-quantum comparison from real exported run data (no hard-coded energies)."""
    data_path = Path(__file__).resolve().parent / "data" / "classical_quantum_comparison_h2_sto3g.json"
    if not data_path.is_file():
        raise FileNotFoundError(
            f"Missing {data_path}; run from repo root:\n"
            "  PYTHONPATH=src python docs/assets/export_classical_quantum_comparison_data.py"
        )
    js = json.loads(data_path.read_text(encoding="utf-8"))
    rows = list(js.get("rows") or [])
    if not rows:
        raise ValueError("classical_quantum_comparison JSON has no rows")

    methods = [str(r["method_label"]) for r in rows]
    energies = [float(r["energy_ha"]) for r in rows]
    errors_mha = [float(r["error_vs_fci_mha"]) for r in rows]
    color_by_key = {
        "hartree_fock": C["gray"],
        "mp2": "#7f8c8d",
        "ccsd": "#2c3e50",
        "vqe_platform": C["blue"],
        "fci": C["green"],
    }
    colors = [color_by_key.get(str(r.get("method_key")), C["gray"]) for r in rows]
    fci = energies[-1]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.2, 6.75))

    # ── Energy bar chart ──
    bars = ax1.barh(methods, energies, color=colors,
                    edgecolor='white', linewidth=1.5, height=0.55)
    ax1.axvline(fci, color=C['green'], ls='--', lw=2, label='FCI (exact)', alpha=0.8)
    bars[3].set_edgecolor(C['blue'])
    bars[3].set_linewidth(3)
    for bar, e in zip(bars, energies):
        ax1.text(e + 0.003, bar.get_y() + bar.get_height() / 2,
                 f'{e:.5f} Ha', va='center', fontsize=FS_INBOX,
                 fontweight='bold', color='#2c3e50')
    ax1.set_xlabel('Ground state energy  (Hartree)', fontsize=FS_SUB)
    ax1.set_title('H$_2$ Ground State Energy\n(sto-3g, 2e/2o active space)',
                  fontsize=FS_HEAD, fontweight='bold', color=C['navy'])
    e_min, e_max = min(energies), max(energies)
    pad = max(0.004, 0.12 * (e_max - e_min))
    ax1.set_xlim(e_min - pad, e_max + pad)
    ax1.grid(axis='x', alpha=0.25, ls='--')
    ax1.legend(fontsize=FS_LEGEND)

    # ── Error vs FCI ──
    bar_colors = [C['gray'], '#7f8c8d', '#2c3e50', C['blue'], C['green']]
    ax2.bar(methods, errors_mha, color=bar_colors,
            edgecolor='white', linewidth=1.5, width=0.55)
    ax2.axhline(1.0, color=C['red'], ls='--', lw=2,
                label='Chemical accuracy threshold  (1 mHa)')
    for i, e in enumerate(errors_mha):
        ax2.text(i, e + 0.15, f'{e:.2f}', ha='center', fontsize=FS_BODY,
                 fontweight='bold', color=bar_colors[i])
    ax2.set_ylabel('Error vs FCI  (mHa)', fontsize=FS_SUB)
    ax2.set_title('Deviation from Exact Solution',
                  fontsize=FS_HEAD, fontweight='bold', color=C['navy'])
    ax2.set_yscale('log')
    ax2.set_ylim(0.01, 400)
    ax2.legend(fontsize=FS_LEGEND)
    ax2.tick_params(axis='x', rotation=14)

    fig.text(
        0.5, 0.02,
        f"[Real runs; exported from {js.get('config_path', 'configs/example_h2_vqe_figure_near_casci.yaml')}]",
        ha='center', va='bottom', fontsize=FS_CAPTION,
        color=C['gray'], style='italic', **_serif(),
    )
    _subplots_finalize(fig, bottom=0.17, top=0.92, wspace=0.32, left=0.10, right=0.98)
    save(fig, 'classical_quantum_comparison.png')


# ─── 12. Mapping comparison ───────────────────────────────────────────────────

def fig_mapping_comparison():
    """Mapping comparison from real exported pipeline metrics (no schematic depths)."""
    data_path = Path(__file__).resolve().parent / "data" / "mapping_comparison_h2_sto3g.json"
    if not data_path.is_file():
        raise FileNotFoundError(
            f"Missing {data_path}; run from repo root:\n"
            "  PYTHONPATH=src python docs/assets/export_mapping_comparison_data.py"
        )
    js = json.loads(data_path.read_text(encoding="utf-8"))
    rows = list(js.get("rows") or [])
    if not rows:
        raise ValueError("mapping_comparison JSON has no rows")

    mappings = [str(r["mapping_label"]).replace(" (", "\n(") for r in rows]
    n_qubits = [int(r["n_qubits"]) for r in rows]
    twoq_counts = [int(r["compiled_sum_twoq"]) for r in rows]
    colors = [C['green'] if "SCBK" in m else C['blue'] for m in mappings]

    fig, axes = plt.subplots(1, 2, figsize=(13.8, 6.55))

    for ax, (data, ylabel, ytitle) in zip(axes, [
        (n_qubits, 'Qubit count', 'Qubits required\n(2e / 2o active space)'),
        (
            twoq_counts,
            'Two-qubit gates (sum over compiled protocol circuits)',
            'Compiled two-qubit gate load\n(real run, same pipeline config)',
        ),
    ]):
        bars = ax.bar(mappings, data, color=colors, alpha=0.85,
                      edgecolor='white', linewidth=2, width=0.54)
        bars[2].set_edgecolor(C['green'])
        bars[2].set_linewidth(3)
        for j, (bar, d) in enumerate(zip(bars, data)):
            lab_col = C['green'] if j == 2 else C['navy']
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + max(data) * 0.05, str(d),
                    ha='center', va='bottom', fontsize=FS_BODY,
                    fontweight='bold',
                    color=lab_col)
        ax.set_ylabel(ylabel, fontsize=FS_SUB)
        ax.set_title(ytitle, fontsize=FS_HEAD, fontweight='bold',
                     color=C['navy'], pad=14)
        ax.grid(axis='y', alpha=0.25, ls='--')
        ax.set_ylim(0, max(data) * 1.38)
        ax.set_facecolor('#fafafa')

    fig.suptitle('Fermion-to-Qubit Mapping Efficiency Comparison',
                 fontsize=FS_HEAD, fontweight='bold', color=C['navy'], y=0.98)
    plt.tight_layout(rect=[0.02, 0.04, 0.98, 0.90], w_pad=3.0)
    save(fig, 'mapping_comparison.png')


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('Generating all figures...')
    fig_why_quantum()
    fig_active_space()
    fig_active_space_convergence()
    fig_molecular_orbitals()
    fig_inquanto_workflow()
    fig_tangelo_workflow()
    fig_three_platform()
    fig_workflow_philosophy()
    fig_qchem_pipeline()
    fig_driver_interface()
    fig_vqe_convergence()
    fig_classical_quantum()
    fig_mapping_comparison()
    print('\nDone — all 13 figures saved.')
