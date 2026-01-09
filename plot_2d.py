#!/usr/bin/env python
"""
2D plot of Cramer-Pople ring puckering parameters

Creates a 2D scatter plot with:
- X-axis: phi (azimuthal angle, 0-360 degrees)
- Y-axis: theta (polar angle, 0-360 degrees)
- Color: q (puckering amplitude) as heatmap

Supports both .params.dat and .classified.dat file formats.

Usage:
    python plot_2d.py 6.params.dat
    python plot_2d.py 2.spawn.classified.dat
    python plot_2d.py 2.params.dat 3.params.dat 4.params.dat 5.params.dat 6.params.dat
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable


def read_params_file(filename):
    """
    Read Cramer-Pople parameters from .params.dat or .classified.dat file
    
    Parameters:
    -----------
    filename : str
        Path to .params.dat or .classified.dat file
    
    Returns:
    --------
    df : pandas.DataFrame
        DataFrame with columns: geometry_idx, q, theta, phi, and optionally conformation
    """
    # Read data, skipping comment lines
    df = pd.read_csv(filename, sep=r'\s+', comment='#')
    
    # Check if conformation column exists (for .classified.dat files)
    if 'conformation' in df.columns:
        # Keep conformation as string, convert others to numeric
        numeric_cols = ['geometry_idx', 'q', 'theta', 'phi']
        df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric, errors='coerce')
    else:
        # Ensure all columns are numeric for .params.dat files
        df = df.apply(pd.to_numeric, errors='coerce')
    
    return df


def plot_2d_puckering(param_file, output_file=None):
    """
    Create 2D scatter plot of theta vs phi colored by q
    
    Parameters:
    -----------
    param_file : str
        Path to .params.dat file
    output_file : str, optional
        Output PDF filename
    """
    # Read data
    df = read_params_file(param_file)
    label = param_file.replace('.params.dat', '').replace('.spawn.classified.dat', '').replace('.classified.dat', '')
    spawn_num = label.split('.')[0] if '.' in label else label
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    
    # Convert theta from radians to degrees (0-360)
    theta_deg = np.rad2deg(df['theta'].values)
    # Normalize theta to 0-360 range
    theta_deg = theta_deg % 360
    
    # Phi is already in degrees, ensure 0-360 range
    phi_deg = df['phi'].values % 360
    
    # Get q values
    q_vals = df['q'].values
    
    # Create scatter plot - color based on q value
    scatter = ax.scatter(phi_deg, theta_deg, c=q_vals, 
                       cmap='viridis', s=40, alpha=0.7,
                       edgecolors='black', linewidths=0.3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('q (Å)', fontsize=12, fontweight='bold')
    
    # Configure axes
    ax.set_xlabel('φ (degrees)', fontsize=14, fontweight='bold')
    ax.set_ylabel('θ (degrees)', fontsize=14, fontweight='bold')
    ax.set_title(f'Spawn {spawn_num} - Ring Puckering Map\n({len(df)} geometries)', 
                fontsize=14, fontweight='bold')
    
    # Set axis limits
    ax.set_xlim(0, 360)
    ax.set_ylim(0, 360)
    
    # Add grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add statistics text
    stats_text = (f'q: {q_vals.mean():.3f} ± {q_vals.std():.3f} Å\n'
                 f'Range: [{q_vals.min():.3f}, {q_vals.max():.3f}] Å')
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Determine output filename
    if output_file is None:
        output_file = f"{label}_2d.pdf"
    
    # Save as PDF
    plt.savefig(output_file, format='pdf', dpi=300, bbox_inches='tight')
    print(f"✅ Saved 2D plot to {output_file}")
    
    plt.close()


def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        print("Usage: python plot_2d.py <params_file1> [params_file2 ...]")
        print("Example: python plot_2d.py 6.params.dat")
        print("Example: python plot_2d.py 2.spawn.classified.dat")
        print("Example: python plot_2d.py 2.params.dat 3.params.dat 4.params.dat 5.params.dat 6.params.dat")
        sys.exit(1)
    
    param_files = sys.argv[1:]
    
    print("\n" + "=" * 70)
    print("2D Cramer-Pople Puckering Visualization")
    print("=" * 70)
    print(f"Files to plot: {param_files}")
    print()
    
    # Create individual plot for each file
    print("Creating 2D puckering plots...")
    for param_file in param_files:
        plot_2d_puckering(param_file)
    
    print("\n✅ All 2D plots created successfully!")


if __name__ == "__main__":
    main()
