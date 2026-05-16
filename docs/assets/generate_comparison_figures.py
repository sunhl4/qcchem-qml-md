#!/usr/bin/env python3
"""
Generate visual comparison figures for three platforms: commercial stack, Tangelo, qchem-stack.
Style: Infographic-style comparison charts.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, FancyArrowPatch
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as path_effects

plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.linewidth'] = 1.5

def save_figure(fig, name, dpi=300):
    fig.savefig(f'/Users/shl/nvidia/qcchem-qml-md/docs/assets/{name}', 
                dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Saved: {name}")
    plt.close()

def plot_three_platform_comparison():
    """
    Three-platform radar comparison: commercial vs Tangelo vs qchem-stack.
    """
    fig, axes = plt.subplots(1, 3, figsize=(16, 6))
    fig.patch.set_facecolor('white')
    
    # Categories for comparison
    categories = ['Algorithm\nBreadth', 'Workflow\nDiscipline', 'Auditability\n(Repro)', 
                  'Hardware\nFreedom', 'MD/ML\nIntegration', 'Cloud\nMaturity']
    n_cats = len(categories)
    
    # Data (subjective scores 1-5)
    vendor_a_scores = [4, 5, 3, 2, 2, 5]
    tangelo_scores = [5, 2, 2, 4, 3, 2]
    qchem_scores = [3, 4, 5, 4, 4, 3]
    
    colors = ['#e74c3c', '#3498db', '#27ae60']  # Red, Blue, Green
    platforms = ['Commercial stack\n(reference)', 'Tangelo\n(Open Source)', 'qchem-stack\n(Our Platform)']
    all_scores = [vendor_a_scores, tangelo_scores, qchem_scores]
    
    for idx, (ax, scores, platform, color) in enumerate(zip(axes, all_scores, platforms, colors)):
        # Create bar chart instead of radar for clarity
        y_pos = np.arange(n_cats)
        bars = ax.barh(y_pos, scores, color=color, alpha=0.7, edgecolor='black', linewidth=2)
        
        # Add score labels
        for bar, score in zip(bars, scores):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                   f'{score}', ha='left', va='center', fontsize=11, fontweight='bold')
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(categories, fontsize=10)
        ax.set_xlim(0, 6)
        ax.set_title(platform, fontsize=13, fontweight='bold', color=color, pad=15)
        ax.set_xlabel('Score (1-5)', fontsize=10)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        
        # Add box around each subplot
        for spine in ax.spines.values():
            spine.set_linewidth(2)
            spine.set_color(color)
    
    fig.suptitle('Quantum Chemistry Platforms: Capability Comparison', 
                fontsize=16, fontweight='bold', y=0.98, color='#2c3e50')
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    save_figure(fig, 'three_platform_radar.png')

def plot_commercial_stack_workflow():
    """
    Visualize a typical three-pillar commercial quantum-chemistry workflow (illustrative).
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('white')
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, 'Commercial stack: illustrative three-pillar workflow', 
           fontsize=16, ha='center', fontweight='bold', color='#e74c3c')
    
    # Three pillars
    pillars = [
        (2, 6.5, 'Chemical\nSpecification', '#ffebee', '#e74c3c',
         ['FermionSpace', 'Active Space', 'PySCF driver', 'Geometry']),
        (7, 6.5, 'Program\nConstruction', '#fff3e0', '#f39c12',
         ['Algorithm*', 'Computable', 'Protocol', 'TKET Passes']),
        (12, 6.5, 'Execution &\nAnalysis', '#e8f5e9', '#27ae60',
         ['Managed cloud', 'HW backends', 'Metering', 'Resource Table']),
    ]
    
    for x, y, title, facecolor, edgecolor, items in pillars:
        # Main box
        box = FancyBboxPatch((x-1.8, y-2), 3.6, 3.5, boxstyle="round,pad=0.1",
                            facecolor=facecolor, edgecolor=edgecolor, linewidth=3)
        ax.add_patch(box)
        
        # Title
        ax.text(x, y+1, title, fontsize=12, ha='center', fontweight='bold', color='#2c3e50')
        
        # Items
        for i, item in enumerate(items):
            ax.text(x, y+0.3-i*0.5, f"• {item}", fontsize=9, ha='center', color='#495057')
    
    # Arrows between pillars
    arrow_style = dict(arrowstyle='->', color='#95a5a6', lw=3, 
                      connectionstyle="arc3,rad=0")
    ax.annotate('', xy=(5.2, 6.5), xytext=(3.8, 6.5), arrowprops=arrow_style)
    ax.annotate('', xy=(10.2, 6.5), xytext=(8.8, 6.5), arrowprops=arrow_style)
    
    plt.tight_layout()
    save_figure(fig, 'commercial_stack_workflow.png')

def plot_tangelo_workflow_detailed():
    """
    Detailed Tangelo workflow showing its notebook-friendly approach.
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    fig.patch.set_facecolor('white')
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(6, 9.5, 'Tangelo: Research Toolbox Workflow', 
           fontsize=16, ha='center', fontweight='bold', color='#3498db')
    
    # Workflow steps
    steps = [
        (6, 8, 'SecondQuantizedMolecule', '#dbe4ff', 
         'xyz geometry\ncharge, spin, basis\nPySCF/Psi4 backend'),
        (6, 6.2, 'Solver Options (dict)', '#d3f9d8',
         'ansatz: UCCSD/HEA\nmapping: JW/BK\nbackend: qulacs/qiskit'),
        (6, 4.4, 'Solver.build()', '#fff3bf',
         'mean-field (HF)\nfermionic Hamiltonian\nansatz circuit\nsimulator'),
        (6, 2.6, 'Solver.simulate()', '#ffc9c9',
         'optimization loop\nenergy convergence\noptimal parameters'),
        (6, 0.8, 'Analysis', '#ffd8a8',
         'get_resources()\nget_rdm()\ncircuit export'),
    ]
    
    for i, (x, y, title, color, desc) in enumerate(steps):
        # Box
        box = FancyBboxPatch((x-2, y-0.6), 4, 1.2, boxstyle="round,pad=0.08",
                            facecolor=color, edgecolor='#2c3e50', linewidth=2)
        ax.add_patch(box)
        
        # Title
        ax.text(x, y+0.2, title, fontsize=11, ha='center', 
               fontweight='bold', color='#2c3e50')
        ax.text(x, y-0.25, desc, fontsize=8, ha='center', 
               color='#495057', style='italic')
        
        # Arrow to next step
        if i < len(steps) - 1:
            ax.annotate('', xy=(x, y-0.7), xytext=(x, y+0.7),
                       arrowprops=dict(arrowstyle='->', color='#3498db', lw=2))
    
    # Side notes
    note_box = FancyBboxPatch((9.5, 3), 2.2, 4, boxstyle="round,pad=0.1",
                            facecolor='#e3f2fd', edgecolor='#3498db', linewidth=2)
    ax.add_patch(note_box)
    ax.text(10.6, 6.5, 'Research-Friendly', fontsize=10, ha='center', 
           fontweight='bold', color='#1565c0')
    ax.text(10.6, 5.5, '✓ Easy to hack', fontsize=9, ha='center', color='#2c3e50')
    ax.text(10.6, 5, '✓ Flexible dict config', fontsize=9, ha='center', color='#2c3e50')
    ax.text(10.6, 4.5, '✓ Rich algorithms', fontsize=9, ha='center', color='#2c3e50')
    ax.text(10.6, 3.8, '⚠ Black-box internals', fontsize=9, ha='center', color='#e74c3c')
    ax.text(10.6, 3.3, '⚠ Weak reproducibility', fontsize=9, ha='center', color='#e74c3c')
    
    plt.tight_layout()
    save_figure(fig, 'tangelo_workflow_detailed.png')

def plot_workflow_philosophy_comparison():
    """
    Delegates to generate_all_figures.fig_workflow_philosophy so the PNG always
    matches the report (14 pt typography, horizontal steps, tight row spacing).
    """
    import sys
    from pathlib import Path

    _here = Path(__file__).resolve().parent
    if str(_here) not in sys.path:
        sys.path.insert(0, str(_here))
    from generate_all_figures import fig_workflow_philosophy

    fig_workflow_philosophy()

if __name__ == '__main__':
    print("Generating comparison figures...")
    plot_three_platform_comparison()
    plot_commercial_stack_workflow()
    plot_tangelo_workflow_detailed()
    plot_workflow_philosophy_comparison()
    print("\nAll comparison figures generated!")
