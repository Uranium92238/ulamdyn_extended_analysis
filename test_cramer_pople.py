"""
Test Cramer-Pople analysis on both rings
"""

from analysis import ExtendedAnalysis
import numpy as np
import matplotlib.pyplot as plt

print("=" * 70)
print("Cramer-Pople Analysis Test")
print("=" * 70)

# Load data
analysis = ExtendedAnalysis()
analysis.load_from_xyz("Geoms_Hopping_4.5.xyz")

# Define both rings
left_ring = [0, 1, 2, 3, 4, 5]   # Left benzene ring
right_ring = [12, 13, 14, 15, 16, 17]  # Right benzene ring (note: only 6 atoms)

# Analyze left ring
print("\n" + "=" * 70)
print("Left Ring Analysis (atoms 0-5)")
print("=" * 70)
cp_left = analysis.perform_cramer_pople_analysis(left_ring)
print("\nFirst 10 results:")
print(cp_left.head(10))
print("\nStatistics:")
print(cp_left.describe())

# Analyze right ring
print("\n" + "=" * 70)
print("Right Ring Analysis (atoms 12-17)")
print("=" * 70)
# Need to adjust - let's check which atoms form the right ring
right_ring_corrected = [10, 11, 12, 13, 14, 15]  # Corrected ring
cp_right = analysis.perform_cramer_pople_analysis(right_ring_corrected)
print("\nFirst 10 results:")
print(cp_right.head(10))
print("\nStatistics:")
print(cp_right.describe())

# Compare the two rings
print("\n" + "=" * 70)
print("Comparison of Left and Right Rings")
print("=" * 70)
print(f"\nLeft ring  - Mean q: {cp_left['q'].mean():.4f}, Std q: {cp_left['q'].std():.4f}")
print(f"Right ring - Mean q: {cp_right['q'].mean():.4f}, Std q: {cp_right['q'].std():.4f}")

print(f"\nLeft ring  - Mean theta: {cp_left['theta'].mean():.4f}, Std theta: {cp_left['theta'].std():.4f}")
print(f"Right ring - Mean theta: {cp_right['theta'].mean():.4f}, Std theta: {cp_right['theta'].std():.4f}")

# Combined analysis with clustering
print("\n" + "=" * 70)
print("Combined Clustering + Cramer-Pople Analysis")
print("=" * 70)

cluster_result = analysis.perform_clustering(method='kmeans', n_clusters=3)
cluster_labels = cluster_result.model.labels_

# Add cluster labels to Cramer-Pople results
cp_left['cluster'] = cluster_labels
cp_right['cluster'] = cluster_labels

print("\nLeft Ring - Average puckering by cluster:")
print(cp_left.groupby('cluster')[['q', 'theta', 'phi']].mean())

print("\nRight Ring - Average puckering by cluster:")
print(cp_right.groupby('cluster')[['q', 'theta', 'phi']].mean())

# Show distributions
print("\n" + "=" * 70)
print("Puckering Parameter Distributions")
print("=" * 70)

print("\nLeft Ring:")
print(f"  q (puckering amplitude) range: [{cp_left['q'].min():.4f}, {cp_left['q'].max():.4f}]")
print(f"  theta (polar angle) range: [{cp_left['theta'].min():.4f}, {cp_left['theta'].max():.4f}]")
print(f"  phi (azimuthal angle) range: [{cp_left['phi'].min():.4f}, {cp_left['phi'].max():.4f}]")

print("\nRight Ring:")
print(f"  q (puckering amplitude) range: [{cp_right['q'].min():.4f}, {cp_right['q'].max():.4f}]")
print(f"  theta (polar angle) range: [{cp_right['theta'].min():.4f}, {cp_right['theta'].max():.4f}]")
print(f"  phi (azimuthal angle) range: [{cp_right['phi'].min():.4f}, {cp_right['phi'].max():.4f}]")

print("\n" + "=" * 70)
print("Analysis Complete!")
print("=" * 70)
print("\nInterpretation:")
print("- q: Puckering amplitude (0 = planar, higher = more puckered)")
print("- theta: Polar angle (describes type of puckering)")
print("- phi: Azimuthal angle (describes orientation of puckering)")
print("\nFor benzene rings, expect small q values (nearly planar)")
