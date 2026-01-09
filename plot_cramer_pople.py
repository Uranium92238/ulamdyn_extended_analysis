#!/usr/bin/env python
"""
Plot Cramer-Pople ring puckering parameters on a 3D sphere

The Cramer-Pople parameters (q, theta, phi) are spherical coordinates:
- q: radial distance (puckering amplitude)
- theta: polar angle
- phi: azimuthal angle

This script visualizes the puckering trajectory on a sphere.
Supports both .params.dat and .classified.dat file formats.

Usage:
    python plot_cramer_pople.py 6.params.dat
    python plot_cramer_pople.py 2.spawn.classified.dat
    python plot_cramer_pople.py 2.params.dat 3.params.dat 4.params.dat
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd


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


def spherical_to_cartesian(q, theta, phi):
    """
    Convert spherical coordinates to Cartesian coordinates
    
    Parameters:
    -----------
    q : array-like
        Radial distance (puckering amplitude)
    theta : array-like
        Polar angle in radians
    phi : array-like
        Azimuthal angle in degrees
    
    Returns:
    --------
    x, y, z : arrays
        Cartesian coordinates
    """
    phi_rad = np.deg2rad(phi)
    x = q * np.sin(theta) * np.cos(phi_rad)
    y = q * np.sin(theta) * np.sin(phi_rad)
    z = q * np.cos(theta)
    return x, y, z


def plot_sphere_wireframe(ax, max_q, alpha=0.1, color='gray'):
    """
    Plot a wireframe sphere as reference
    
    Parameters:
    -----------
    ax : matplotlib 3D axis
        Axis to plot on
    max_q : float
        Maximum radius for the sphere
    alpha : float
        Transparency
    color : str
        Color of wireframe
    """
    u = np.linspace(0, 2 * np.pi, 50)
    v = np.linspace(0, np.pi, 50)
    x = max_q * np.outer(np.cos(u), np.sin(v))
    y = max_q * np.outer(np.sin(u), np.sin(v))
    z = max_q * np.outer(np.ones(np.size(u)), np.cos(v))
    ax.plot_wireframe(x, y, z, color=color, alpha=alpha, linewidth=0.5)


def plot_cramer_pople_3d(param_files, output_file=None):
    """
    Create 3D sphere plot of Cramer-Pople parameters
    
    Parameters:
    -----------
    param_files : list
        List of .params.dat files to plot
    output_file : str, optional
        If provided, save figure to this file
    """
    fig = plt.figure(figsize=(10, 10))
    
    # Main 3D plot
    ax1 = fig.add_subplot(111, projection='3d')
    
    # Define specific colors for each spawn number
    color_map = {
        '2': 'red',
        '3': 'green',
        '4': 'blue',
        '5': 'orange',
        '6': 'purple'
    }
    
    all_q = []
    
    for idx, param_file in enumerate(param_files):
        # Read data
        df = read_params_file(param_file)
        label = param_file.replace('.params.dat', '').replace('.spawn.classified.dat', '')
        
        # Get color based on spawn number
        spawn_num = label.split('.')[0] if '.' in label else label
        color = color_map.get(spawn_num, plt.cm.tab10(idx))
        
        # Convert to Cartesian
        x, y, z = spherical_to_cartesian(df['q'].values, df['theta'].values, df['phi'].values)
        
        all_q.extend(df['q'].values)
        
        # 3D scatter plot
        ax1.scatter(x, y, z, c=color, label=f"Spawn {spawn_num}", alpha=0.6, s=20)
    
    # Plot reference sphere
    max_q = max(all_q) * 1.1
    plot_sphere_wireframe(ax1, max_q)
    
    # Configure 3D plot
    ax1.set_xlabel('X (Å)', fontsize=12)
    ax1.set_ylabel('Y (Å)', fontsize=12)
    ax1.set_zlabel('Z (Å)', fontsize=12)
    ax1.set_title('Cramer-Pople Puckering Sphere\n(q, θ, φ) in Cartesian coordinates', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper left', fontsize=10)
    ax1.set_box_aspect([1,1,1])
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Saved plot to {output_file}")
    
    plt.show()


def main():
    """Main function"""
    
    if len(sys.argv) < 2:
        print("Usage: python plot_cramer_pople.py <params_file1> [params_file2 ...]")
        print("Example: python plot_cramer_pople.py 6.params.dat")
        print("Example: python plot_cramer_pople.py 2.spawn.classified.dat")
        print("Example: python plot_cramer_pople.py 2.params.dat 3.params.dat 4.params.dat 5.params.dat 6.params.dat")
        sys.exit(1)
    
    param_files = sys.argv[1:]
    
    print("\n" + "=" * 70)
    print("Cramer-Pople Ring Puckering Visualization")
    print("=" * 70)
    print(f"Files to plot: {param_files}")
    print()
    
    # Create output filename
    if len(param_files) == 1:
        base_name = param_files[0].replace('.params.dat', '').replace('.spawn.classified.dat', '')
        sphere_output = f"{base_name}_sphere.png"
    else:
        sphere_output = "all_sphere.png"
    
    # Plot 3D sphere only
    print("Creating 3D sphere plot...")
    plot_cramer_pople_3d(param_files, output_file=sphere_output)
    
    print("\n✅ Sphere plot created successfully!")


if __name__ == "__main__":
    main()
