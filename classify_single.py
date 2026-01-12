#!/usr/bin/env python3
"""Quick script to classify a single XYZ file"""

import sys
from analysis import ExtendedAnalysis
from ulamdyn.descriptors import RingParams
import numpy as np

if len(sys.argv) < 2:
    print("Usage: python3 classify_single.py <xyz_file>")
    sys.exit(1)

xyz_file = sys.argv[1]
output_file = xyz_file.replace('.xyz', '.classified.dat')
ring_atoms = [0, 1, 2, 3, 4, 5]  # 0-indexed for analysis

print('=' * 70)
print(f'Analyzing and Classifying {xyz_file}')
print('=' * 70)

# Load and analyze
analysis = ExtendedAnalysis()
analysis.load_from_xyz(xyz_file)
print(f'Loaded {len(analysis.coords)} geometries')

cp_results = analysis.perform_cramer_pople_analysis(ring_atoms)
print(f'✅ Cramer-Pople analysis complete')

# Classify
print('Classifying conformations...')
ring_atoms_1indexed = [a + 1 for a in ring_atoms]  # Convert to 1-indexed for ulamdyn
conformations = []

for idx, row in cp_results.iterrows():
    try:
        coords = analysis.coords[int(row['geometry_idx'])]
        ring_coords = coords[ring_atoms]  # Extract using 0-indexed
        ring_coords_centered = ring_coords - ring_coords.mean(axis=0)
        ring_params = RingParams(ring_atoms_1indexed, ring_coords=ring_coords_centered)
        theta_deg = np.degrees(row['theta'])
        conformations.append(ring_params.get_conf_6memb(theta_deg, row['phi']))
    except:
        conformations.append('ERROR')

cp_results['conformation'] = conformations
valid = cp_results[cp_results['conformation'] != 'ERROR']

# Print stats
print(f'\nTotal: {len(cp_results)}, Success: {len(valid)}')
print(f'q: {valid["q"].mean():.6f} ± {valid["q"].std():.6f} Å')
print(f'theta: {np.rad2deg(valid["theta"].mean()):.2f}°')
print(f'phi: {valid["phi"].mean():.2f}°')
print('\nConformations:')
for conf, count in valid['conformation'].value_counts().sort_index().items():
    print(f'  {conf:10s}: {count:5d} ({100*count/len(valid):5.2f}%)')

# Save
with open(output_file, 'w') as f:
    f.write(f'# Cramer-Pople Parameters with Classification\n')
    f.write(f'# Source: {xyz_file}\n')
    f.write(f'# Ring atoms: {ring_atoms}\n')
    f.write(f'#\n')
    f.write(f'  geometry_idx              q          theta            phi  conformation\n')
    for _, row in cp_results.iterrows():
        f.write(f'{int(row["geometry_idx"]):14d}  {row["q"]:13.8f}  {row["theta"]:13.8f}  {row["phi"]:13.8f}  {row["conformation"]:>12s}\n')
    
    # Add summary statistics
    f.write(f'\n# Summary Statistics\n')
    f.write(f'# Total geometries: {len(cp_results)}\n')
    f.write(f'# Successfully classified: {len(valid)}\n')
    f.write(f'#\n')
    f.write(f'# Conformation Counts and Percentages:\n')
    for conf, count in valid['conformation'].value_counts().items():
        percentage = 100 * count / len(valid)
        f.write(f'#   {conf:10s}: {count:5d} ({percentage:5.2f}%)\n')

print(f'\n✅ Saved to {output_file}')
