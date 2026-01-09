# XYZ File Format Support

The `ExtendedAnalysis` class supports multiple XYZ file formats through its custom parser.

## Supported Formats

### 1. **Standard XYZ with Metadata** (like your Geoms_Hopping files)

```
38
TRAJ = 1 | Time = 3.0 fs | DE5.4 = 0.0815 eV | 
C        0.65678931  -1.66620430   1.17573480 
C        1.36722008  -1.51210075   0.05283259 
...
```

**Parsing behavior:**
- ✅ Extracts TRAJ number from comment
- ✅ Extracts Time value from comment
- ✅ Stores full comment as label

---

### 2. **Standard XYZ without Metadata** (your case)

```
38

C        0.65678931  -1.66620430   1.17573480 
C        1.36722008  -1.51210075   0.05283259 
...
```

**Parsing behavior:**
- ✅ Empty comment line → Creates label "Geometry 0", "Geometry 1", etc.
- ✅ Uses geometry index as Time (0, 1, 2, ...)
- ✅ Uses 0 as TRAJ number
- ✅ No errors!

---

### 3. **Standard XYZ with Simple Comments**

```
38
First geometry
C        0.65678931  -1.66620430   1.17573480 
C        1.36722008  -1.51210075   0.05283259 
...
38
Second geometry
C        0.58984919  -1.68638730   1.25779563 
...
```

**Parsing behavior:**
- ✅ Uses comment as label
- ✅ Uses geometry index as Time
- ✅ Uses 0 as TRAJ number

---

## Default Values

When metadata is not present in comment lines:

| Field | Default Value | Description |
|-------|--------------|-------------|
| **Time** | Geometry index (0, 1, 2, ...) | Sequential numbering |
| **TRAJ** | 0 | All geometries assigned to trajectory 0 |
| **Label** | `"Geometry {idx}"` or actual comment | Used for identification |

## Examples

### Example 1: Load XYZ without metadata

```python
from analysis import ExtendedAnalysis

# Your XYZ file has no metadata - no problem!
analysis = ExtendedAnalysis()
analysis.load_from_xyz("my_geometries.xyz")

# Time will be: [0, 1, 2, 3, ...]
# TRAJ will be: [0, 0, 0, 0, ...]
print(f"Times: {analysis.geoms_loader.traj_time[:, 1]}")
print(f"Trajectories: {analysis.geoms_loader.traj_time[:, 0]}")
```

### Example 2: Manually set time values

If you want to assign specific time values to your geometries:

```python
from analysis import ExtendedAnalysis
import numpy as np

# Load data
analysis = ExtendedAnalysis()
analysis.load_from_xyz("my_geometries.xyz")

# Override time values (e.g., if you know the actual times)
# Let's say each geometry is 0.5 fs apart
n_geoms = len(analysis.coords)
actual_times = np.arange(n_geoms) * 0.5  # 0, 0.5, 1.0, 1.5, ...

# Update the geoms_loader
analysis.geoms_loader.traj_time[:, 1] = actual_times

# Now rebuild the dataset with correct times
analysis.geoms_loader.dataset['Time'] = actual_times

print(f"Updated times: {actual_times}")
```

### Example 3: Assign trajectory numbers

If your XYZ file combines multiple trajectories:

```python
from analysis import ExtendedAnalysis
import numpy as np

# Load data
analysis = ExtendedAnalysis()
analysis.load_from_xyz("combined_trajectories.xyz")

# Assign trajectory numbers (e.g., 20 geometries per trajectory)
n_geoms = len(analysis.coords)
geoms_per_traj = 20
traj_numbers = np.repeat(range(n_geoms // geoms_per_traj + 1), geoms_per_traj)[:n_geoms]

# Update the geoms_loader
analysis.geoms_loader.traj_time[:, 0] = traj_numbers
analysis.geoms_loader.trajectories = traj_numbers
analysis.geoms_loader.dataset['TRAJ'] = traj_numbers

print(f"Trajectory assignments: {traj_numbers}")
```

## Coordinate Format

The parser expects standard XYZ coordinate format:

```
Element  X  Y  Z
```

- **Element**: Atom symbol (C, H, N, O, etc.)
- **X, Y, Z**: Cartesian coordinates (typically in Ångströms)

Whitespace can be spaces or tabs, and any amount is fine.

## Error Handling

The parser is robust and handles:

✅ **Missing comment lines** → Creates default labels  
✅ **Empty comment lines** → Creates default labels  
✅ **Comments without metadata** → Uses comment as label, defaults for Time/TRAJ  
✅ **Incomplete geometries** → Skips and continues  
✅ **Malformed lines** → Skips and continues  

## Tips for Your Workflow

### If you generate XYZ files yourself:

1. **Simple approach**: Just include empty comment lines
   ```
   38
   
   C  0.0  0.0  0.0
   ...
   ```

2. **With identifiers**: Add simple comments
   ```
   38
   Configuration 1
   C  0.0  0.0  0.0
   ...
   ```

3. **With full metadata** (recommended if you have time info):
   ```
   38
   Time = 0.5 fs
   C  0.0  0.0  0.0
   ...
   ```

4. **With both** (ideal for trajectory data):
   ```
   38
   TRAJ = 1 | Time = 0.5 fs
   C  0.0  0.0  0.0
   ...
   ```

## Validation

To check what was parsed from your XYZ file:

```python
from analysis import ExtendedAnalysis

analysis = ExtendedAnalysis()
analysis.load_from_xyz("your_file.xyz")

# Check what was loaded
print(f"Number of geometries: {len(analysis.coords)}")
print(f"First 5 labels: {analysis.labels[:5]}")
print(f"Time values: {analysis.geoms_loader.traj_time[:, 1]}")
print(f"TRAJ values: {analysis.geoms_loader.traj_time[:, 0]}")
analysis.summary()
```

## Common Issues

### Issue: "No valid geometries found"
**Cause**: File format is incorrect  
**Solution**: Check that each geometry block has:
1. Line with number of atoms (integer)
2. Comment line (can be empty)
3. Exactly that many coordinate lines

### Issue: Wrong number of geometries loaded
**Cause**: Some geometry blocks might be incomplete  
**Solution**: Check that each block has the correct number of coordinate lines

### Issue: Clustering fails
**Cause**: Usually not related to XYZ format  
**Solution**: Ensure you have enough geometries (at least as many as n_clusters)

---

## Summary

The parser is **flexible and forgiving**:

- ✅ Works with or without metadata
- ✅ Uses sensible defaults when metadata is missing
- ✅ Doesn't require specific comment format
- ✅ Handles various XYZ dialects

**You don't need to modify your XYZ files** - the parser will work with whatever format you have!
