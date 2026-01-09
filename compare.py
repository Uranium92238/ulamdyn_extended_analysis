"""
Minimal comparison: Ring analysis using TRAJ vs external XYZ file
"""
from analysis import ExtendedAnalysis
import numpy as np

# Ring atoms (left benzene ring)
ring_atoms = [0, 1, 2, 3, 4, 5]

# Method 1: Load from TRAJ folders
print("Loading from TRAJ folders...")
traj_analysis = ExtendedAnalysis()
traj_analysis.load_from_trajs()
traj_cp = traj_analysis.perform_cramer_pople_analysis(ring_atoms)

# Method 2: Load from external XYZ file
print("\nLoading from traj2.xyz...")
xyz_analysis = ExtendedAnalysis()
xyz_analysis.load_from_xyz("traj2.xyz")
xyz_cp = xyz_analysis.perform_cramer_pople_analysis(ring_atoms)

# Print results in identical format
print("\n" + "=" * 70)
print("RESULTS COMPARISON")
print("=" * 70)

print(f"\nTRAJ Method:")
print(f"  Geometries: {len(traj_cp)}")
print(f"  q (mean ± std): {traj_cp['q'].mean():.6f} ± {traj_cp['q'].std():.6f}")
print(f"  theta (mean ± std): {traj_cp['theta'].mean():.6f} ± {traj_cp['theta'].std():.6f}")
print(f"  phi (mean ± std): {traj_cp['phi'].mean():.6f} ± {traj_cp['phi'].std():.6f}")
print(f"  First 5 q values: {traj_cp['q'].head().values}")

print(f"\nExternal XYZ Method:")
print(f"  Geometries: {len(xyz_cp)}")
print(f"  q (mean ± std): {xyz_cp['q'].mean():.6f} ± {xyz_cp['q'].std():.6f}")
print(f"  theta (mean ± std): {xyz_cp['theta'].mean():.6f} ± {xyz_cp['theta'].std():.6f}")
print(f"  phi (mean ± std): {xyz_cp['phi'].mean():.6f} ± {xyz_cp['phi'].std():.6f}")
print(f"  First 5 q values: {xyz_cp['q'].head().values}")

# Check if results are identical
print("\n" + "=" * 70)
print("VERIFICATION")
print("=" * 70)
identical = np.allclose(traj_cp['q'].values, xyz_cp['q'].values, rtol=1e-9)
print(f"Results identical: {'✅ YES' if identical else '❌ NO'}")
if identical:
    print("Both methods produce the same ring puckering parameters!")
