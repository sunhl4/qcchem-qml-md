#!/usr/bin/env python3
"""
Generate publication-quality scientific figures for quantum chemistry presentation.
Style: Clean, professional, suitable for TOC (Table of Contents) graphics in journals.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Ellipse, Polygon, Arc
from matplotlib.collections import PatchCollection
import matplotlib.patheffects as path_effects

# Set publication style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
plt.rcParams['axes.linewidth'] = 1.5
plt.rcParams['xtick.major.width'] = 1.5
plt.rcParams['ytick.major.width'] = 1.5

def save_figure(fig, name, dpi=300):
    """Save with tight layout."""
    fig.savefig(f'/Users/shl/nvidia/qcchem-qml-md/docs/assets/{name}', 
                dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
    print(f"Saved: {name}")

def plot_why_quantum_chemistry():
    """
    Figure 1: Why quantum computing for chemistry?
    Left: Classical computer overwhelmed by exponential scaling
    Right: Quantum processor seamlessly handling the molecule
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.patch.set_facecolor('white')
    
    # ===== LEFT PANEL: Classical Struggle =====
    ax = axes[0]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Classical Computing:\nExponential Scaling', 
                 fontsize=14, fontweight='bold', pad=20, color='#2c3e50')
    
    # Draw molecule (simplified benzene-like ring)
    center_x, center_y = 5, 5
    n_atoms = 6
    radius = 2
    atom_positions = []
    for i in range(n_atoms):
        angle = 2 * np.pi * i / n_atoms
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        atom_positions.append((x, y))
        # Draw atom
        circle = Circle((x, y), 0.3, facecolor='#95a5a6', edgecolor='#7f8c8d', linewidth=2)
        ax.add_patch(circle)
        # Add chaos lines (representing exponential complexity)
        for j in range(3):
            offset_angle = np.random.uniform(0, 2*np.pi)
            length = np.random.uniform(0.5, 1.5)
            ax.plot([x, x + length*np.cos(offset_angle)], 
                   [y, y + length*np.sin(offset_angle)], 
                   'k-', alpha=0.3, linewidth=1)
    
    # Add bonds
    for i in range(n_atoms):
        x1, y1 = atom_positions[i]
        x2, y2 = atom_positions[(i+1) % n_atoms]
        ax.plot([x1, x2], [y1, y2], 'k-', linewidth=3, alpha=0.5)
    
    # Draw "crushing" classical computer chip at bottom
    chip = FancyBboxPatch((3, 0.5), 4, 1.5, boxstyle="round,pad=0.1", 
                         facecolor='#ecf0f1', edgecolor='#7f8c8d', linewidth=3)
    ax.add_patch(chip)
    # Chip pins
    for i in range(5):
        x_pin = 3.5 + i * 0.7
        ax.plot([x_pin, x_pin], [0.5, 0.3], 'k-', linewidth=2)
        ax.plot([x_pin, x_pin], [2.0, 2.2], 'k-', linewidth=2)
    
    # Add explosion/breaking effect
    ax.annotate('', xy=(5, 2.2), xytext=(5, 3.5),
               arrowprops=dict(arrowstyle='->', color='#e74c3c', lw=3))
    
    # Add "2^N" text
    text = ax.text(5, 8.5, r'$2^N$ scaling', fontsize=16, ha='center', fontweight='bold',
                  color='#c0392b')
    text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    
    # ===== RIGHT PANEL: Quantum Solution =====
    ax = axes[1]
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Quantum Computing:\nNatural Fit', 
                 fontsize=14, fontweight='bold', pad=20, color='#2c3e50')
    
    # Draw same molecule but with quantum wavefunction visualization
    center_x, center_y = 5, 5.5
    radius = 2
    atom_positions = []
    
    # Draw quantum orbital clouds (glowing effect)
    for i in range(n_atoms):
        angle = 2 * np.pi * i / n_atoms
        x = center_x + radius * np.cos(angle)
        y = center_y + radius * np.sin(angle)
        atom_positions.append((x, y))
        
        # Draw orbital lobes (red/blue for phase)
        # Outer lobe
        ellipse_outer = Ellipse((x + 0.5*np.cos(angle), y + 0.5*np.sin(angle)), 
                               1.2, 0.6, angle=np.degrees(angle),
                               facecolor='#e74c3c', alpha=0.3, edgecolor='#c0392b', linewidth=2)
        ax.add_patch(ellipse_outer)
        # Inner lobe
        ellipse_inner = Ellipse((x - 0.3*np.cos(angle), y - 0.3*np.sin(angle)), 
                               0.8, 0.4, angle=np.degrees(angle),
                               facecolor='#3498db', alpha=0.3, edgecolor='#2980b9', linewidth=2)
        ax.add_patch(ellipse_inner)
        
        # Draw atom nucleus
        circle = Circle((x, y), 0.25, facecolor='#2c3e50', edgecolor='black', linewidth=2)
        ax.add_patch(circle)
    
    # Add bonds
    for i in range(n_atoms):
        x1, y1 = atom_positions[i]
        x2, y2 = atom_positions[(i+1) % n_atoms]
        ax.plot([x1, x2], [y1, y2], '#2c3e50', linewidth=4, alpha=0.8)
    
    # Draw quantum processor at bottom
    # Qubit grid
    for i in range(3):
        for j in range(3):
            qx, qy = 3.5 + i*1.2, 0.8 + j*0.6
            # Qubit circle
            qubit = Circle((qx, qy), 0.2, facecolor='#3498db', 
                         edgecolor='#2980b9', linewidth=2)
            ax.add_patch(qubit)
            # Connection lines between qubits
            if i < 2:
                ax.plot([qx+0.2, qx+1.0], [qy, qy], '#3498db', linewidth=1.5, alpha=0.6)
            if j < 2:
                ax.plot([qx, qx], [qy+0.2, qy+0.4], '#3498db', linewidth=1.5, alpha=0.6)
    
    # Add smooth connection arrow
    ax.annotate('', xy=(5, 3.8), xytext=(5, 2.5),
               arrowprops=dict(arrowstyle='->', color='#27ae60', lw=4,
                             connectionstyle="arc3,rad=0"))
    
    # Add "Polynomial" text
    text = ax.text(5, 8.5, 'Polynomial scaling', fontsize=16, ha='center', fontweight='bold',
                  color='#27ae60')
    text.set_path_effects([path_effects.withStroke(linewidth=3, foreground='white')])
    
    plt.tight_layout()
    save_figure(fig, 'why_quantum_chemistry.png')
    plt.close()

def plot_active_space_embedding():
    """
    Figure 2: Active Space and Embedding concept.
    Large protein environment (grey/transparent) + highlighted active site (colored orbitals).
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    fig.patch.set_facecolor('white')
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Title
    ax.text(6, 7.5, 'Quantum Embedding Strategy: Focus on the Active Space', 
           fontsize=16, ha='center', fontweight='bold', color='#2c3e50')
    
    # Draw large molecular environment (wireframe/simplified)
    # Create a large irregular "protein" shape
    env_x = [1, 2.5, 4, 5, 6.5, 8, 9.5, 11, 10, 8.5, 7, 5.5, 4, 2.5, 1.5, 1]
    env_y = [2, 1, 1.5, 2.5, 1.8, 2.2, 1.5, 2.5, 4, 5, 5.5, 5, 4.5, 4, 3, 2]
    
    # Draw environment as transparent filled shape
    env_poly = Polygon(list(zip(env_x, env_y)), facecolor='#ecf0f1', 
                      edgecolor='#bdc3c7', linewidth=3, alpha=0.6, linestyle='--')
    ax.add_patch(env_poly)
    
    # Add some random atoms in environment (grey)
    np.random.seed(42)
    for _ in range(30):
        x = np.random.uniform(1.5, 10.5)
        y = np.random.uniform(2, 5)
        # Check if inside rough polygon
        circle = Circle((x, y), 0.15, facecolor='#95a5a6', 
                       edgecolor='#7f8c8d', linewidth=1, alpha=0.5)
        ax.add_patch(circle)
    
    # Draw the ACTIVE SITE (center, highlighted)
    center_x, center_y = 6, 3.5
    
    # Draw orbital clouds around active site
    # Multiple concentric orbital representations
    for r, alpha in [(1.8, 0.15), (1.4, 0.25), (1.0, 0.35)]:
        circle = Circle((center_x, center_y), r, facecolor='#e74c3c', 
                       edgecolor='none', alpha=alpha)
        ax.add_patch(circle)
    
    # Draw orbital lobes (pi orbitals)
    for angle in [0, 60, 120, 180, 240, 300]:
        rad = np.radians(angle)
        # Red lobe
        ex = center_x + 1.2 * np.cos(rad)
        ey = center_y + 1.2 * np.sin(rad)
        ellipse = Ellipse((ex, ey), 0.8, 0.4, angle=angle,
                         facecolor='#e74c3c', alpha=0.4, edgecolor='#c0392b', linewidth=2)
        ax.add_patch(ellipse)
        # Blue lobe (opposite phase)
        ex2 = center_x + 0.6 * np.cos(rad + np.pi)
        ey2 = center_y + 0.6 * np.sin(rad + np.pi)
        ellipse2 = Ellipse((ex2, ey2), 0.5, 0.25, angle=angle+180,
                          facecolor='#3498db', alpha=0.4, edgecolor='#2980b9', linewidth=2)
        ax.add_patch(ellipse2)
    
    # Central active atoms
    active_atoms = [(0, 0), (0.8, 0.5), (-0.5, 0.8), (0.3, -0.7)]
    for dx, dy in active_atoms:
        circle = Circle((center_x + dx, center_y + dy), 0.25, 
                       facecolor='#2c3e50', edgecolor='black', linewidth=2.5)
        ax.add_patch(circle)
    
    # Labels
    ax.text(2, 6.5, 'Classical Region\n(Large Environment)', fontsize=11, 
           ha='center', color='#7f8c8d', style='italic')
    ax.text(10, 6.5, 'Classical Region\n(Large Environment)', fontsize=11, 
           ha='center', color='#7f8c8d', style='italic')
    
    # Active space label with box
    bbox_props = dict(boxstyle="round,pad=0.5", facecolor='#fff9e6', 
                     edgecolor='#f39c12', linewidth=2)
    ax.text(center_x, 1.5, 'QUANTUM ACTIVE SPACE\n(High-precision treatment)', 
           fontsize=12, ha='center', fontweight='bold', color='#d35400', bbox=bbox_props)
    
    # Arrows pointing to active space
    ax.annotate('', xy=(center_x-1, 2.5), xytext=(center_x-2, 1.8),
               arrowprops=dict(arrowstyle='->', color='#e67e22', lw=2))
    ax.annotate('', xy=(center_x+1, 2.5), xytext=(center_x+2, 1.8),
               arrowprops=dict(arrowstyle='->', color='#e67e22', lw=2))
    
    plt.tight_layout()
    save_figure(fig, 'active_space_embedding_sci.png')
    plt.close()

def plot_molecular_orbitals():
    """
    Figure 3: Molecular orbitals - pi and sigma orbitals visualization.
    Clean scientific rendering showing orbital phase (red/blue).
    """
    fig = plt.figure(figsize=(14, 5))
    fig.patch.set_facecolor('white')
    
    # Create 3 subplots for different orbital types
    orbitals = [
        ('σ (sigma) Bonding', 'linear'),
        ('π (pi) Bonding', 'pi'),
        ('δ (delta) Bonding', 'delta')
    ]
    
    for idx, (title, otype) in enumerate(orbitals, 1):
        ax = fig.add_subplot(1, 3, idx)
        ax.set_xlim(-2, 2)
        ax.set_ylim(-1.5, 1.5)
        ax.set_aspect('equal')
        ax.axis('off')
        ax.set_title(title, fontsize=13, fontweight='bold', pad=15, color='#2c3e50')
        
        # Draw two nuclei
        n1, n2 = (-1.2, 0), (1.2, 0)
        for nx, ny in [n1, n2]:
            circle = Circle((nx, ny), 0.2, facecolor='#34495e', 
                           edgecolor='black', linewidth=2)
            ax.add_patch(circle)
        
        if otype == 'linear':
            # Sigma orbital - cylindrical along bond axis
            # Draw bond
            ax.plot([-1.2, 1.2], [0, 0], '#2c3e50', linewidth=4, zorder=1)
            # Orbital cloud - elongated along axis
            ellipse = Ellipse((0, 0), 2.2, 0.6, facecolor='#e74c3c', 
                             alpha=0.3, edgecolor='#c0392b', linewidth=2)
            ax.add_patch(ellipse)
            
        elif otype == 'pi':
            # Pi orbital - above and below the bond
            ax.plot([-1.2, 1.2], [0, 0], '#2c3e50', linewidth=4, zorder=1)
            # Top lobe (red)
            ellipse_top = Ellipse((0, 0.6), 1.8, 0.7, facecolor='#e74c3c',
                                 alpha=0.35, edgecolor='#c0392b', linewidth=2)
            ax.add_patch(ellipse_top)
            # Bottom lobe (blue - opposite phase)
            ellipse_bottom = Ellipse((0, -0.6), 1.8, 0.7, facecolor='#3498db',
                                    alpha=0.35, edgecolor='#2980b9', linewidth=2)
            ax.add_patch(ellipse_bottom)
            
        elif otype == 'delta':
            # Delta orbital - two lobes on each side
            ax.plot([-1.2, 1.2], [0, 0], '#2c3e50', linewidth=4, zorder=1)
            # Four lobes in cloverleaf pattern
            for angle in [45, 135, 225, 315]:
                rad = np.radians(angle)
                ex = 0.6 * np.cos(rad)
                ey = 0.6 * np.sin(rad)
                color = '#e74c3c' if angle < 180 else '#3498db'
                edge = '#c0392b' if angle < 180 else '#2980b9'
                ellipse = Ellipse((ex, ey), 0.7, 0.4, angle=angle,
                                 facecolor=color, alpha=0.35, edgecolor=edge, linewidth=2)
                ax.add_patch(ellipse)
    
    # Add overall title
    fig.suptitle('Molecular Orbital Types: The Target of Quantum Simulations', 
                fontsize=15, fontweight='bold', y=0.98, color='#2c3e50')
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    save_figure(fig, 'molecular_orbitals_sci.png')
    plt.close()

def plot_comparison_flow():
    """
    Canonical asset matches the group-report pipeline figure (generate_all_figures).
    """
    import sys
    from pathlib import Path

    _here = Path(__file__).resolve().parent
    if str(_here) not in sys.path:
        sys.path.insert(0, str(_here))
    from generate_all_figures import fig_qchem_pipeline

    fig_qchem_pipeline()

if __name__ == '__main__':
    print("Generating publication-quality scientific figures...")
    plot_why_quantum_chemistry()
    plot_active_space_embedding()
    plot_molecular_orbitals()
    plot_comparison_flow()
    print("\nAll figures generated successfully!")
