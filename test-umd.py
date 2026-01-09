import ulamdyn as umd
import numpy as np
import pandas as pd

# Step 1: Define ring atoms (1-indexed)
ring_atoms = [1, 2, 3, 4, 5, 6]

# Step 2: Create RingParams object
ring = umd.RingParams(ring_atom_ind=ring_atoms)

# Step 3: Load trajectories
ring.read_all_trajs()

# Step 4: Manually calculate parameters and classify
all_pucker_params = []
for xyz in ring.ring_coords:
    cppar = ring.get_pucker_coords(xyz)
    all_pucker_params.append(cppar)

all_pucker_params = np.asarray(all_pucker_params, dtype=np.float64)

# Step 5: Convert to polar coordinates for 6-membered ring
polar_coords = ring._cp_to_polar(all_pucker_params)
df = pd.DataFrame(polar_coords)

# Step 6: Add classification
func_vec = np.vectorize(ring.get_conf_6memb)
df["class"] = func_vec(df["theta"].values, df["phi"].values)

# Step 7: Add TRAJ and Time info manually
if ring.traj_time is not None:
    df.insert(0, "TRAJ", ring.traj_time[:, 0])
    df.insert(1, "Time", ring.traj_time[:, 1])
    df["TRAJ"] = df["TRAJ"].astype("int32")

# Step 8: Save to CSV
df.to_csv("all_ring_params.csv", index=False)
print("✅ Saved to all_ring_params.csv")
print(df.head())
print("\nConformation distribution:")
print(df["class"].value_counts())
