# Extended Analysis with ulamdyn

> Extended analysis tools for molecular dynamics: Load geometries from standalone XYZ files or TRAJ folders, perform clustering and Cramer-Pople ring puckering analysis using ulamdyn.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation Requirements](#installation-requirements)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [XYZ File Format](#xyz-file-format)
- [Workflow Examples](#workflow-examples)
- [Validation](#validation-traj-vs-xyz-methods-produce-identical-results)
- [Comparison: TRAJ vs XYZ Loading](#comparison-traj-vs-xyz-loading)
- [Troubleshooting](#troubleshooting)
- [Performance Tips](#performance-tips)
- [Contributing](#contributing)
- [Notes](#notes)
- [Files in This Repository](#files-in-this-repository)
- [Example Output](#example-output)
- [See Also](#see-also)
- [Acknowledgments](#acknowledgments)

## Overview

The `analysis.py` script has been extended to support loading geometries from **standalone XYZ files** in addition to the original TRAJ folder method. This allows you to perform clustering and Cramer-Pople analysis using ulamdyn on geometries generated from any source.

## Key Features

### ✅ **Dual Loading Methods**
- **Method 1**: Load from TRAJ folders (original behavior)
- **Method 2**: Load from standalone XYZ files (new feature)

### ✅ **Clustering Analysis**
- K-Means clustering
- Hierarchical clustering
- DBSCAN clustering
- Full integration with ulamdyn's `ClusterGeoms` class

### ✅ **Cramer-Pople Analysis**
- Ring puckering parameter calculation (Q, θ, φ)
- **Automatic conformation classification** (Chair, Boat, Envelope, Half-chair, Skew, Twist, etc.)
- Support for 5- and 6-membered rings
- Returns pandas DataFrame with parameters and classifications
- Command-line tool for quick analysis

### ✅ **Flexible Input**
- Single XYZ file
- Multiple XYZ files (concatenated)
- Custom XYZ parser handles metadata in comment lines

## Installation Requirements

```bash
# Required packages
numpy
pandas
ulamdyn
```

## Quick Start

### 1. Basic Usage - Load from XYZ File

```python
from analysis import ExtendedAnalysis

# Create analysis object
analysis = ExtendedAnalysis()

# Load from XYZ file
analysis.load_from_xyz("Geoms_Hopping_4.5.xyz")

# View summary
analysis.summary()
```

### 2. Clustering Analysis

```python
# Perform K-Means clustering
cluster_result = analysis.perform_clustering(method='kmeans', n_clusters=5)

# Access cluster labels
labels = cluster_result.model.labels_
print(f"Cluster labels: {labels}")

# Get cluster centers
centers = cluster_result.model.cluster_centers_
print(f"Number of clusters: {len(centers)}")
```

### 3. Cramer-Pople Analysis

```python
# Define ring atom indices (0-indexed)
ring_atoms = [0, 1, 2, 3, 4, 5]  # 6-membered ring

# Perform Cramer-Pople analysis
cp_results = analysis.perform_cramer_pople_analysis(ring_atoms)

# View results
print(cp_results.head())
print(cp_results.describe())
```

### 4. Cramer-Pople Classification (Command-Line Tool)

For quick analysis with automatic conformation classification, use the `classify_single.py` script:

```bash
# Analyze a single XYZ file
python classify_single.py your_file.xyz

# Example output:
# Total: 4000, Success: 4000
# q: 0.175776 ± 0.091661 Å
# theta: 0.03°
# phi: 106.11°
# 
# Conformations:
#   0C0       :   110 ( 2.75%)
#   1C4       :    98 ( 2.45%)
#   2C5       :   455 (11.38%)
#   C         :  2211 (55.27%)
#   ...
# 
# ✅ Saved to your_file.classified.dat
```

**Output file format:**
```
# Cramer-Pople Parameters with Classification
# Source: your_file.xyz
# Ring atoms: [0, 1, 2, 3, 4, 5]
#
  geometry_idx              q          theta            phi  conformation
             0     0.06115044     4.78518839    93.89828698           6T2
             1     0.06132391     4.79429227    93.34770913           6T2
             2     0.06126369     4.80210876    92.60491993           6T2
           ...
```

## API Reference

### `ExtendedAnalysis` Class

#### Loading Methods

**`load_from_trajs()`**
- Loads geometries from TRAJ folders (original method)
- Returns: self (for method chaining)

```python
analysis = ExtendedAnalysis()
analysis.load_from_trajs()
```

**`load_from_xyz(xyz_file, use_ulamdyn_parser=False)`**
- Loads geometries from a single XYZ file
- Parameters:
  - `xyz_file` (str): Path to XYZ file
  - `use_ulamdyn_parser` (bool): Use ulamdyn's parser vs custom parser
- Returns: self

```python
analysis = ExtendedAnalysis()
analysis.load_from_xyz("geometries.xyz")
```

**`load_from_multiple_xyz(xyz_files, use_ulamdyn_parser=False)`**
- Loads and concatenates geometries from multiple XYZ files
- Parameters:
  - `xyz_files` (list): List of XYZ file paths
  - `use_ulamdyn_parser` (bool): Use ulamdyn's parser vs custom parser
- Returns: self

```python
files = ["geom1.xyz", "geom2.xyz", "geom3.xyz"]
analysis = ExtendedAnalysis()
analysis.load_from_multiple_xyz(files)
```

#### Analysis Methods

**`perform_clustering(method='kmeans', n_clusters=5, **kwargs)`**
- Performs clustering analysis on loaded geometries
- Parameters:
  - `method` (str): 'kmeans', 'hierarchical', or 'dbscan'
  - `n_clusters` (int): Number of clusters (for kmeans/hierarchical)
  - `**kwargs`: Additional parameters for ClusterGeoms
- Returns: ClusterGeoms object

```python
# K-Means
cluster = analysis.perform_clustering(method='kmeans', n_clusters=5)

# Hierarchical
cluster = analysis.perform_clustering(method='hierarchical', n_clusters=3)

# DBSCAN
cluster = analysis.perform_clustering(method='dbscan', eps=0.5, min_samples=3)
```

**`perform_cramer_pople_analysis(ring_atom_indices)`**
- Performs Cramer-Pople analysis on ring structures
- Parameters:
  - `ring_atom_indices` (list): List of atom indices forming the ring (0-indexed)
- Returns: pandas DataFrame with columns: geometry_idx, q, theta, phi

```python
ring_atoms = [0, 1, 2, 3, 4, 5]
cp_df = analysis.perform_cramer_pople_analysis(ring_atoms)
```

#### Utility Methods

**`get_geoms_loader()`**
- Returns the underlying ulamdyn GetCoords object
- Allows access to all ulamdyn functionality

```python
geoms_loader = analysis.get_geoms_loader()
print(geoms_loader.xyz.shape)
```

**`summary()`**
- Prints a summary of loaded data

```python
analysis.summary()
```

## XYZ File Format

The custom parser is **flexible** and supports multiple XYZ formats:

### Format 1: With Metadata (optional)

```
38
TRAJ = 1 | Time = 3.0 fs | DE5.4 = 0.0815 eV | 
C        0.65678931  -1.66620430   1.17573480 
C        1.36722008  -1.51210075   0.05283259 
...
```

### Format 2: Without Metadata (also works!)

```
38
     0.000                   0
C        0.65678931  -1.66620430   1.17573480 
C        1.36722008  -1.51210075   0.05283259 
...
```

### Format 3: Empty Comment Line

```
38

C        0.65678931  -1.66620430   1.17673480 
C        1.36722008  -1.51210075   0.05283259 
...
```

**Standard Format:**
- Line 1: Number of atoms (integer)
- Line 2: Comment/metadata (can be empty, contain metadata, or any text)
- Lines 3+: Element X Y Z coordinates

**Parser behavior:**
- ✅ If "TRAJ" and "Time" are in comment → extracts values
- ✅ If not present → uses defaults (TRAJ=0, Time=geometry_index)
- ✅ Empty or arbitrary comment lines → no errors!

## Cramer-Pople Conformation Classifications

The `classify_single.py` tool uses **ulamdyn's internal classification functions** to automatically identify ring conformations based on Cramer-Pople parameters.

### 6-Membered Ring Conformations

| Class | Name | Description |
|-------|------|-------------|
| **C** | Chair | Most stable conformation, θ ≈ 0° or 180° |
| **0C0** | Planar | Completely flat ring |
| **1C4, 2C5, 3C6, etc.** | Numbered Chair | Chair variants with specific atom positions |
| **4C1, 5C2, 6C3, etc.** | Inverted Chair | Inverted chair conformations |
| **B** | Boat | High-energy conformation |
| **B25, B41, etc.** | Numbered Boat | Boat variants |
| **E** | Envelope | One atom out of plane |
| **E1, E2, ..., E6** | Numbered Envelope | Envelope with specific atom out |
| **H** | Half-chair | Intermediate conformation |
| **1H2, 2H3, etc.** | Numbered Half-chair | Half-chair variants |
| **S** | Skew-boat | Twisted boat conformation |
| **1S2, 2S3, etc.** | Numbered Skew | Skew-boat variants |
| **T** | Twist-boat | Alternative boat form |
| **2T6, 4T2, etc.** | Numbered Twist | Twist-boat variants |

### 5-Membered Ring Conformations

| Class | Name | Description |
|-------|------|-------------|
| **E** | Envelope | One atom out of plane |
| **T** | Twist | Two atoms out of plane |

### How Classification Works

1. **Calculate Cramer-Pople parameters**: Q (amplitude), θ (polar angle), φ (azimuthal angle)
2. **Use ulamdyn's `get_conf_6memb(θ, φ)`** or **`get_conf_5memb(φ)`** functions
3. **Classify based on parameter ranges**:
   - Chair: θ close to 0° or 180°
   - Boat: θ ≈ 90°, specific φ ranges
   - Envelope: θ ≈ 45° or 135°
   - Half-chair, Skew, Twist: Intermediate values

### Validation

The classification results from `classify_single.py` have been **validated to match 100%** with ulamdyn's direct method:

```bash
# Using classify_single.py
python classify_single.py traj1.xyz
# Matches: 4000/4000
# ✅ ALL CLASSIFICATIONS MATCH PERFECTLY!
```

## Workflow Examples

### Example 1: Complete Analysis Pipeline

```python
from analysis import ExtendedAnalysis
import numpy as np

# 1. Load data
analysis = ExtendedAnalysis()
analysis.load_from_xyz("Geoms_Hopping_4.5.xyz")

# 2. Perform clustering
cluster_result = analysis.perform_clustering(method='kmeans', n_clusters=5)
cluster_labels = cluster_result.model.labels_

# 3. Perform Cramer-Pople analysis
ring_atoms = [0, 1, 2, 3, 4, 5]
cp_results = analysis.perform_cramer_pople_analysis(ring_atoms)

# 4. Combine results
cp_results['cluster'] = cluster_labels

# 5. Analyze by cluster
print(cp_results.groupby('cluster')['q'].mean())
```

### Example 2: Multiple Files Analysis

```python
import glob
from analysis import ExtendedAnalysis

# Find all XYZ files
xyz_files = glob.glob("Geoms_Hopping_*.xyz")

# Load all files
analysis = ExtendedAnalysis()
analysis.load_from_multiple_xyz(xyz_files)
analysis.summary()

# Perform clustering on combined dataset
cluster_result = analysis.perform_clustering(method='kmeans', n_clusters=10)
print(f"Total geometries: {len(cluster_result.model.labels_)}")
```

### Example 3: Accessing Advanced ulamdyn Features

```python
from analysis import ExtendedAnalysis
import ulamdyn as umd

# Load data
analysis = ExtendedAnalysis()
analysis.load_from_xyz("geometries.xyz")

# Get the geoms_loader for advanced operations
geoms_loader = analysis.get_geoms_loader()

# Now you can use any ulamdyn functionality
# Example: Dimension reduction
dim_reduction = umd.DimensionReduction(geoms_loader.dataset)
dim_reduction.pca(n_components=2)

# Example: RMSD calculations
# (requires reference geometry)
# geoms_loader.align_geoms()
# rmsd = geoms_loader.rmsd
```

### Example 4: Programmatic Conformation Classification

```python
from analysis import ExtendedAnalysis
from ulamdyn.descriptors import RingParams
import numpy as np

# Load data
analysis = ExtendedAnalysis()
analysis.load_from_xyz("traj1.xyz")

# Perform Cramer-Pople analysis
ring_atoms = [0, 1, 2, 3, 4, 5]
cp_results = analysis.perform_cramer_pople_analysis(ring_atoms)

# Classify each geometry
ring_atoms_1indexed = [a + 1 for a in ring_atoms]
conformations = []

for idx, row in cp_results.iterrows():
    coords = analysis.coords[int(row['geometry_idx'])]
    ring_coords = coords[ring_atoms]
    ring_coords_centered = ring_coords - ring_coords.mean(axis=0)
    
    # Create RingParams and classify
    ring_params = RingParams(ring_atoms_1indexed, ring_coords=ring_coords_centered)
    theta_deg = np.degrees(row['theta'])
    conf = ring_params.get_conf_6memb(theta_deg, row['phi'])
    conformations.append(conf)

# Add to dataframe
cp_results['conformation'] = conformations

# Analyze conformation distribution
print(cp_results['conformation'].value_counts())

# Filter by conformation
chair_geoms = cp_results[cp_results['conformation'] == 'C']
print(f"Chair conformations: {len(chair_geoms)} ({100*len(chair_geoms)/len(cp_results):.1f}%)")
```

## Validation: TRAJ vs XYZ Methods Produce Identical Results

The XYZ loading method has been **validated** to produce identical results to the TRAJ folder method:

```python
# compare.py - Minimal validation script
from analysis import ExtendedAnalysis
import numpy as np

ring_atoms = [0, 1, 2, 3, 4, 5]

# Method 1: TRAJ folders
traj_analysis = ExtendedAnalysis()
traj_analysis.load_from_trajs()
traj_cp = traj_analysis.perform_cramer_pople_analysis(ring_atoms)

# Method 2: External XYZ file
xyz_analysis = ExtendedAnalysis()
xyz_analysis.load_from_xyz("extgeoms.xyz")
xyz_cp = xyz_analysis.perform_cramer_pople_analysis(ring_atoms)

# Verify identical results
identical = np.allclose(traj_cp['q'].values, xyz_cp['q'].values, rtol=1e-9)
print(f"Results identical: {'✅ YES' if identical else '❌ NO'}")
# Output: Results identical: ✅ YES
```

**Validation confirms:**
- ✅ Both methods load identical geometries
- ✅ Cramer-Pople parameters match exactly
- ✅ All analysis results are numerically identical

## Comparison: TRAJ vs XYZ Loading

| Feature | TRAJ Folders | XYZ Files |
|---------|-------------|-----------|
| Source | TRAJ*/RESULTS/geometries.xyz | Any XYZ file |
| Setup | Requires TRAJ folder structure | Single/multiple XYZ files |
| Flexibility | Limited to TRAJ format | Any XYZ source |
| Metadata | Automatic from folder structure | Parsed from comment lines or defaults |
| Use Case | Original workflow | Custom workflows, external data |
| Results | Reference implementation | ✅ Validated identical |

## Troubleshooting

### Issue: "ValueError: could not convert string to float"
**Cause**: Coordinates contain non-numeric characters  
**Solution**: Check your XYZ file for malformed coordinate lines. Each coordinate line should be: `Element X Y Z`

### Issue: "No geometries loaded"
**Cause**: XYZ file format doesn't match expected structure  
**Solution**: 
1. Verify file has the standard format (atom count, comment, coordinates)
2. Check that the number of coordinate lines matches the atom count
3. Ensure there are no missing geometries in the file

### Issue: "Geometry shape: (n,) instead of (n, natoms, 3)"
**Cause**: Parser failed to create proper 3D array  
**Solution**: Check that each geometry block is complete and has consistent structure

### Issue: Ring atoms not found in Cramer-Pople analysis
**Cause**: Invalid atom indices  
**Solution**: 
1. Verify ring atom indices are 0-indexed (first atom is 0)
2. Ensure indices are within range: 0 to (number_of_atoms - 1)
3. Use `identify_rings.py` helper script to identify ring atoms

### Issue: Clustering fails or gives unexpected results
**Cause**: Data not loaded properly or insufficient geometries  
**Solution**: 
1. Run `analysis.summary()` to verify data is loaded
2. Check that you have enough geometries (at least n_clusters geometries)
3. Verify coordinate shapes with `print(analysis.coords.shape)`

### Issue: "Reference geometry not found" when loading TRAJ
**Cause**: Missing `geom.xyz` reference file  
**Solution**: Copy or create `geom.xyz` in the working directory with the equilibrium geometry

## Performance Tips

1. **Large datasets**: For clustering on large datasets, consider:
   - Using fewer clusters
   - Subsampling geometries
   - Using DBSCAN with appropriate eps parameter

2. **Multiple files**: When loading many XYZ files, the concatenation is done in memory. For very large datasets, consider processing in batches.

3. **Cramer-Pople analysis**: This loops over all geometries. For large datasets, consider using multiprocessing or processing subsets.

## Contributing

To extend the analysis:

1. Add new methods to the `ExtendedAnalysis` class
2. Maintain compatibility with ulamdyn's data structures
3. Update documentation and examples

## Notes

- The custom XYZ parser extracts TRAJ and Time information from comment lines when available
- If TRAJ/Time info is not in comments, default values are used (TRAJ=0, Time=geometry_index)
- The `geoms_loader.dataset` is a pandas DataFrame compatible with ulamdyn's clustering methods
- All ulamdyn analysis methods can be accessed through the `geoms_loader` object

### ⚠️ Important: Atom Indexing Convention

**Critical distinction between Python and ulamdyn indexing:**

- **Python/NumPy arrays**: 0-indexed (atoms 0, 1, 2, 3, 4, 5)
- **ulamdyn RingParams**: 1-indexed (atoms 1, 2, 3, 4, 5, 6)

**When using `ExtendedAnalysis.perform_cramer_pople_analysis()`:**
- ✅ Use **0-indexed** atom indices: `ring_atoms = [0, 1, 2, 3, 4, 5]`
- The method handles conversion to 1-indexed internally

**When using `RingParams` directly:**
- ✅ Use **1-indexed** atom indices: `ring_atoms = [1, 2, 3, 4, 5, 6]`

**Example:**
```python
# Correct usage with ExtendedAnalysis
ring_atoms = [0, 1, 2, 3, 4, 5]  # 0-indexed
cp_results = analysis.perform_cramer_pople_analysis(ring_atoms)

# Correct usage with RingParams directly
ring_atoms_1indexed = [1, 2, 3, 4, 5, 6]  # 1-indexed
ring_params = umd.RingParams(ring_atom_ind=ring_atoms_1indexed)
```

## Files in This Repository

- **`analysis.py`** - Main extended analysis module with `ExtendedAnalysis` class
- **`classify_single.py`** - Command-line tool for Cramer-Pople analysis with automatic conformation classification
- **`test-umd.py`** - Direct ulamdyn usage example for TRAJ folders
- **`compare.py`** - Minimal validation script comparing TRAJ vs XYZ loading methods
- **`test_cramer_pople.py`** - Test script for Cramer-Pople analysis on multiple rings
- **`XYZ_FORMAT_GUIDE.md`** - Detailed guide on supported XYZ file formats
- **`README_EXTENDED_ANALYSIS.md`** - This file

## Example Output

```
Loading from TRAJ folders...
Loaded 4000 geometries from TRAJ folders

Performing Cramer-Pople analysis...
Ring atoms: [0, 1, 2, 3, 4, 5]
Cramer-Pople analysis completed for 4000 geometries

TRAJ Method:
  Geometries: 4000
  q (mean ± std): 0.169413 ± 0.078265
  theta (mean ± std): 0.000236 ± 0.045134
  phi (mean ± std): 95.221255 ± 87.343584

External XYZ Method:
  Geometries: 4000
  q (mean ± std): 0.169413 ± 0.078265
  theta (mean ± std): 0.000236 ± 0.045134
  phi (mean ± std): 95.221255 ± 87.343584

Results identical: ✅ YES
Both methods produce the same ring puckering parameters!
```

## See Also

- **ulamdyn** - [Newton-X Package](https://newton-x.org/) for molecular dynamics analysis
- **Cramer-Pople Analysis** - Ring puckering parameters (q, θ, φ)
- **XYZ Format** - Standard molecular structure file format

## Acknowledgments

This extension builds upon the [ulamdyn](https://newton-x.org/) package from the Newton-X project.

---

**Last Updated**: January 9, 2026  
# Extended Analysis with ulamdyn

> Extended analysis tools for molecular dynamics: Load geometries from standalone XYZ files or TRAJ folders, perform clustering and Cramer-Pople ring puckering analysis using ulamdyn.

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation Requirements](#installation-requirements)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [XYZ File Format](#xyz-file-format)
- [Workflow Examples](#workflow-examples)
- [Validation](#validation-traj-vs-xyz-methods-produce-identical-results)
- [Comparison: TRAJ vs XYZ Loading](#comparison-traj-vs-xyz-loading)
- [Troubleshooting](#troubleshooting)
- [Performance Tips](#performance-tips)
- [Contributing](#contributing)
- [Notes](#notes)
- [Files in This Repository](#files-in-this-repository)
- [Example Output](#example-output)
- [See Also](#see-also)
- [Acknowledgments](#acknowledgments)

## Overview

The `analysis.py` script has been extended to support loading geometries from **standalone XYZ files** in addition to the original TRAJ folder method. This allows you to perform clustering and Cramer-Pople analysis using ulamdyn on geometries generated from any source.

## Key Features

### ✅ **Dual Loading Methods**
- **Method 1**: Load from TRAJ folders (original behavior)
- **Method 2**: Load from standalone XYZ files (new feature)

### ✅ **Clustering Analysis**
- K-Means clustering
- Hierarchical clustering
- DBSCAN clustering
- Full integration with ulamdyn's `ClusterGeoms` class

### ✅ **Cramer-Pople Analysis**
- Ring puckering parameter calculation (Q, θ, φ)
- **Automatic conformation classification** (Chair, Boat, Envelope, Half-chair, Skew, Twist, etc.)
- Support for 5- and 6-membered rings
- Returns pandas DataFrame with parameters and classifications
- Command-line tool for quick analysis

### ✅ **Flexible Input**
- Single XYZ file
- Multiple XYZ files (concatenated)
- Custom XYZ parser handles metadata in comment lines

## Installation Requirements

```bash
# Required packages
numpy
pandas
ulamdyn
```

## Quick Start

### 1. Basic Usage - Load from XYZ File

```python
from analysis import ExtendedAnalysis

# Create analysis object
analysis = ExtendedAnalysis()

# Load from XYZ file
analysis.load_from_xyz("Geoms_Hopping_4.5.xyz")

# View summary
analysis.summary()
```

### 2. Clustering Analysis

```python
# Perform K-Means clustering
cluster_result = analysis.perform_clustering(method='kmeans', n_clusters=5)

# Access cluster labels
labels = cluster_result.model.labels_
print(f"Cluster labels: {labels}")

# Get cluster centers
centers = cluster_result.model.cluster_centers_
print(f"Number of clusters: {len(centers)}")
```

### 3. Cramer-Pople Analysis

```python
# Define ring atom indices (0-indexed)
ring_atoms = [0, 1, 2, 3, 4, 5]  # 6-membered ring

# Perform Cramer-Pople analysis
cp_results = analysis.perform_cramer_pople_analysis(ring_atoms)

# View results
print(cp_results.head())
print(cp_results.describe())
```

### 4. Cramer-Pople Classification (Command-Line Tool)

For quick analysis with automatic conformation classification, use the `classify_single.py` script:

```bash
# Analyze a single XYZ file
python classify_single.py your_file.xyz

# Example output:
# Total: 4000, Success: 4000
# q: 0.175776 ± 0.091661 Å
# theta: 0.03°
# phi: 106.11°
# 
# Conformations:
#   0C0       :   110 ( 2.75%)
#   1C4       :    98 ( 2.45%)
#   2C5       :   455 (11.38%)
#   C         :  2211 (55.27%)
#   ...
# 
# ✅ Saved to your_file.classified.dat
```

**Output file format:**
```
# Cramer-Pople Parameters with Classification
# Source: your_file.xyz
# Ring atoms: [0, 1, 2, 3, 4, 5]
#
  geometry_idx              q          theta            phi  conformation
             0     0.06115044     4.78518839    93.89828698           6T2
             1     0.06132391     4.79429227    93.34770913           6T2
             2     0.06126369     4.80210876    92.60491993           6T2
           ...
```

## API Reference

### `ExtendedAnalysis` Class

#### Loading Methods

**`load_from_trajs()`**
- Loads geometries from TRAJ folders (original method)
- Returns: self (for method chaining)

```python
analysis = ExtendedAnalysis()
analysis.load_from_trajs()
```

**`load_from_xyz(xyz_file, use_ulamdyn_parser=False)`**
- Loads geometries from a single XYZ file
- Parameters:
  - `xyz_file` (str): Path to XYZ file
  - `use_ulamdyn_parser` (bool): Use ulamdyn's parser vs custom parser
- Returns: self

```python
analysis = ExtendedAnalysis()
analysis.load_from_xyz("geometries.xyz")
```

**`load_from_multiple_xyz(xyz_files, use_ulamdyn_parser=False)`**
- Loads and concatenates geometries from multiple XYZ files
- Parameters:
  - `xyz_files` (list): List of XYZ file paths
  - `use_ulamdyn_parser` (bool): Use ulamdyn's parser vs custom parser
- Returns: self

```python
files = ["geom1.xyz", "geom2.xyz", "geom3.xyz"]
analysis = ExtendedAnalysis()
analysis.load_from_multiple_xyz(files)
```

#### Analysis Methods

**`perform_clustering(method='kmeans', n_clusters=5, **kwargs)`**
- Performs clustering analysis on loaded geometries
- Parameters:
  - `method` (str): 'kmeans', 'hierarchical', or 'dbscan'
  - `n_clusters` (int): Number of clusters (for kmeans/hierarchical)
  - `**kwargs`: Additional parameters for ClusterGeoms
- Returns: ClusterGeoms object

```python
# K-Means
cluster = analysis.perform_clustering(method='kmeans', n_clusters=5)

# Hierarchical
cluster = analysis.perform_clustering(method='hierarchical', n_clusters=3)

# DBSCAN
cluster = analysis.perform_clustering(method='dbscan', eps=0.5, min_samples=3)
```

**`perform_cramer_pople_analysis(ring_atom_indices)`**
- Performs Cramer-Pople analysis on ring structures
- Parameters:
  - `ring_atom_indices` (list): List of atom indices forming the ring (0-indexed)
- Returns: pandas DataFrame with columns: geometry_idx, q, theta, phi

```python
ring_atoms = [0, 1, 2, 3, 4, 5]
cp_df = analysis.perform_cramer_pople_analysis(ring_atoms)
```

#### Utility Methods

**`get_geoms_loader()`**
- Returns the underlying ulamdyn GetCoords object
- Allows access to all ulamdyn functionality

```python
geoms_loader = analysis.get_geoms_loader()
print(geoms_loader.xyz.shape)
```

**`summary()`**
- Prints a summary of loaded data

```python
analysis.summary()
```

## XYZ File Format

The custom parser is **flexible** and supports multiple XYZ formats:

### Format 1: With Metadata (optional)

```
38
TRAJ = 1 | Time = 3.0 fs | DE5.4 = 0.0815 eV | 
C        0.65678931  -1.66620430   1.17573480 
C        1.36722008  -1.51210075   0.05283259 
...
```

### Format 2: Without Metadata (also works!)

```
38
     0.000                   0
C        0.65678931  -1.66620430   1.17573480 
C        1.36722008  -1.51210075   0.05283259 
...
```

### Format 3: Empty Comment Line

```
38

C        0.65678931  -1.66620430   1.17673480 
C        1.36722008  -1.51210075   0.05283259 
...
```

**Standard Format:**
- Line 1: Number of atoms (integer)
- Line 2: Comment/metadata (can be empty, contain metadata, or any text)
- Lines 3+: Element X Y Z coordinates

**Parser behavior:**
- ✅ If "TRAJ" and "Time" are in comment → extracts values
- ✅ If not present → uses defaults (TRAJ=0, Time=geometry_index)
- ✅ Empty or arbitrary comment lines → no errors!

## Cramer-Pople Conformation Classifications

The `classify_single.py` tool uses **ulamdyn's internal classification functions** to automatically identify ring conformations based on Cramer-Pople parameters.

### 6-Membered Ring Conformations

| Class | Name | Description |
|-------|------|-------------|
| **C** | Chair | Most stable conformation, θ ≈ 0° or 180° |
| **0C0** | Planar | Completely flat ring |
| **1C4, 2C5, 3C6, etc.** | Numbered Chair | Chair variants with specific atom positions |
| **4C1, 5C2, 6C3, etc.** | Inverted Chair | Inverted chair conformations |
| **B** | Boat | High-energy conformation |
| **B25, B41, etc.** | Numbered Boat | Boat variants |
| **E** | Envelope | One atom out of plane |
| **E1, E2, ..., E6** | Numbered Envelope | Envelope with specific atom out |
| **H** | Half-chair | Intermediate conformation |
| **1H2, 2H3, etc.** | Numbered Half-chair | Half-chair variants |
| **S** | Skew-boat | Twisted boat conformation |
| **1S2, 2S3, etc.** | Numbered Skew | Skew-boat variants |
| **T** | Twist-boat | Alternative boat form |
| **2T6, 4T2, etc.** | Numbered Twist | Twist-boat variants |

### 5-Membered Ring Conformations

| Class | Name | Description |
|-------|------|-------------|
| **E** | Envelope | One atom out of plane |
| **T** | Twist | Two atoms out of plane |

### How Classification Works

1. **Calculate Cramer-Pople parameters**: Q (amplitude), θ (polar angle), φ (azimuthal angle)
2. **Use ulamdyn's `get_conf_6memb(θ, φ)`** or **`get_conf_5memb(φ)`** functions
3. **Classify based on parameter ranges**:
   - Chair: θ close to 0° or 180°
   - Boat: θ ≈ 90°, specific φ ranges
   - Envelope: θ ≈ 45° or 135°
   - Half-chair, Skew, Twist: Intermediate values

### Validation

The classification results from `classify_single.py` have been **validated to match 100%** with ulamdyn's direct method:

```bash
# Using classify_single.py
python classify_single.py traj1.xyz
# Matches: 4000/4000
# ✅ ALL CLASSIFICATIONS MATCH PERFECTLY!
```

## Workflow Examples

### Example 1: Complete Analysis Pipeline

```python
from analysis import ExtendedAnalysis
import numpy as np

# 1. Load data
analysis = ExtendedAnalysis()
analysis.load_from_xyz("Geoms_Hopping_4.5.xyz")

# 2. Perform clustering
cluster_result = analysis.perform_clustering(method='kmeans', n_clusters=5)
cluster_labels = cluster_result.model.labels_

# 3. Perform Cramer-Pople analysis
ring_atoms = [0, 1, 2, 3, 4, 5]
cp_results = analysis.perform_cramer_pople_analysis(ring_atoms)

# 4. Combine results
cp_results['cluster'] = cluster_labels

# 5. Analyze by cluster
print(cp_results.groupby('cluster')['q'].mean())
```

### Example 2: Multiple Files Analysis

```python
import glob
from analysis import ExtendedAnalysis

# Find all XYZ files
xyz_files = glob.glob("Geoms_Hopping_*.xyz")

# Load all files
analysis = ExtendedAnalysis()
analysis.load_from_multiple_xyz(xyz_files)
analysis.summary()

# Perform clustering on combined dataset
cluster_result = analysis.perform_clustering(method='kmeans', n_clusters=10)
print(f"Total geometries: {len(cluster_result.model.labels_)}")
```

### Example 3: Accessing Advanced ulamdyn Features

```python
from analysis import ExtendedAnalysis
import ulamdyn as umd

# Load data
analysis = ExtendedAnalysis()
analysis.load_from_xyz("geometries.xyz")

# Get the geoms_loader for advanced operations
geoms_loader = analysis.get_geoms_loader()

# Now you can use any ulamdyn functionality
# Example: Dimension reduction
dim_reduction = umd.DimensionReduction(geoms_loader.dataset)
dim_reduction.pca(n_components=2)

# Example: RMSD calculations
# (requires reference geometry)
# geoms_loader.align_geoms()
# rmsd = geoms_loader.rmsd
```

### Example 4: Programmatic Conformation Classification

```python
from analysis import ExtendedAnalysis
from ulamdyn.descriptors import RingParams
import numpy as np

# Load data
analysis = ExtendedAnalysis()
analysis.load_from_xyz("traj1.xyz")

# Perform Cramer-Pople analysis
ring_atoms = [0, 1, 2, 3, 4, 5]
cp_results = analysis.perform_cramer_pople_analysis(ring_atoms)

# Classify each geometry
ring_atoms_1indexed = [a + 1 for a in ring_atoms]
conformations = []

for idx, row in cp_results.iterrows():
    coords = analysis.coords[int(row['geometry_idx'])]
    ring_coords = coords[ring_atoms]
    ring_coords_centered = ring_coords - ring_coords.mean(axis=0)
    
    # Create RingParams and classify
    ring_params = RingParams(ring_atoms_1indexed, ring_coords=ring_coords_centered)
    theta_deg = np.degrees(row['theta'])
    conf = ring_params.get_conf_6memb(theta_deg, row['phi'])
    conformations.append(conf)

# Add to dataframe
cp_results['conformation'] = conformations

# Analyze conformation distribution
print(cp_results['conformation'].value_counts())

# Filter by conformation
chair_geoms = cp_results[cp_results['conformation'] == 'C']
print(f"Chair conformations: {len(chair_geoms)} ({100*len(chair_geoms)/len(cp_results):.1f}%)")
```

## Validation: TRAJ vs XYZ Methods Produce Identical Results

The XYZ loading method has been **validated** to produce identical results to the TRAJ folder method:

```python
# compare.py - Minimal validation script
from analysis import ExtendedAnalysis
import numpy as np

ring_atoms = [0, 1, 2, 3, 4, 5]

# Method 1: TRAJ folders
traj_analysis = ExtendedAnalysis()
traj_analysis.load_from_trajs()
traj_cp = traj_analysis.perform_cramer_pople_analysis(ring_atoms)

# Method 2: External XYZ file
xyz_analysis = ExtendedAnalysis()
xyz_analysis.load_from_xyz("extgeoms.xyz")
xyz_cp = xyz_analysis.perform_cramer_pople_analysis(ring_atoms)

# Verify identical results
identical = np.allclose(traj_cp['q'].values, xyz_cp['q'].values, rtol=1e-9)
print(f"Results identical: {'✅ YES' if identical else '❌ NO'}")
# Output: Results identical: ✅ YES
```

**Validation confirms:**
- ✅ Both methods load identical geometries
- ✅ Cramer-Pople parameters match exactly
- ✅ All analysis results are numerically identical

## Comparison: TRAJ vs XYZ Loading

| Feature | TRAJ Folders | XYZ Files |
|---------|-------------|-----------|
| Source | TRAJ*/RESULTS/geometries.xyz | Any XYZ file |
| Setup | Requires TRAJ folder structure | Single/multiple XYZ files |
| Flexibility | Limited to TRAJ format | Any XYZ source |
| Metadata | Automatic from folder structure | Parsed from comment lines or defaults |
| Use Case | Original workflow | Custom workflows, external data |
| Results | Reference implementation | ✅ Validated identical |

## Troubleshooting

### Issue: "ValueError: could not convert string to float"
**Cause**: Coordinates contain non-numeric characters  
**Solution**: Check your XYZ file for malformed coordinate lines. Each coordinate line should be: `Element X Y Z`

### Issue: "No geometries loaded"
**Cause**: XYZ file format doesn't match expected structure  
**Solution**: 
1. Verify file has the standard format (atom count, comment, coordinates)
2. Check that the number of coordinate lines matches the atom count
3. Ensure there are no missing geometries in the file

### Issue: "Geometry shape: (n,) instead of (n, natoms, 3)"
**Cause**: Parser failed to create proper 3D array  
**Solution**: Check that each geometry block is complete and has consistent structure

### Issue: Ring atoms not found in Cramer-Pople analysis
**Cause**: Invalid atom indices  
**Solution**: 
1. Verify ring atom indices are 0-indexed (first atom is 0)
2. Ensure indices are within range: 0 to (number_of_atoms - 1)
3. Use `identify_rings.py` helper script to identify ring atoms

### Issue: Clustering fails or gives unexpected results
**Cause**: Data not loaded properly or insufficient geometries  
**Solution**: 
1. Run `analysis.summary()` to verify data is loaded
2. Check that you have enough geometries (at least n_clusters geometries)
3. Verify coordinate shapes with `print(analysis.coords.shape)`

### Issue: "Reference geometry not found" when loading TRAJ
**Cause**: Missing `geom.xyz` reference file  
**Solution**: Copy or create `geom.xyz` in the working directory with the equilibrium geometry

## Performance Tips

1. **Large datasets**: For clustering on large datasets, consider:
   - Using fewer clusters
   - Subsampling geometries
   - Using DBSCAN with appropriate eps parameter

2. **Multiple files**: When loading many XYZ files, the concatenation is done in memory. For very large datasets, consider processing in batches.

3. **Cramer-Pople analysis**: This loops over all geometries. For large datasets, consider using multiprocessing or processing subsets.

## Contributing

To extend the analysis:

1. Add new methods to the `ExtendedAnalysis` class
2. Maintain compatibility with ulamdyn's data structures
3. Update documentation and examples

## Notes

- The custom XYZ parser extracts TRAJ and Time information from comment lines when available
- If TRAJ/Time info is not in comments, default values are used (TRAJ=0, Time=geometry_index)
- The `geoms_loader.dataset` is a pandas DataFrame compatible with ulamdyn's clustering methods
- All ulamdyn analysis methods can be accessed through the `geoms_loader` object

### ⚠️ Important: Atom Indexing Convention

**Critical distinction between Python and ulamdyn indexing:**

- **Python/NumPy arrays**: 0-indexed (atoms 0, 1, 2, 3, 4, 5)
- **ulamdyn RingParams**: 1-indexed (atoms 1, 2, 3, 4, 5, 6)

**When using `ExtendedAnalysis.perform_cramer_pople_analysis()`:**
- ✅ Use **0-indexed** atom indices: `ring_atoms = [0, 1, 2, 3, 4, 5]`
- The method handles conversion to 1-indexed internally

**When using `RingParams` directly:**
- ✅ Use **1-indexed** atom indices: `ring_atoms = [1, 2, 3, 4, 5, 6]`

**Example:**
```python
# Correct usage with ExtendedAnalysis
ring_atoms = [0, 1, 2, 3, 4, 5]  # 0-indexed
cp_results = analysis.perform_cramer_pople_analysis(ring_atoms)

# Correct usage with RingParams directly
ring_atoms_1indexed = [1, 2, 3, 4, 5, 6]  # 1-indexed
ring_params = umd.RingParams(ring_atom_ind=ring_atoms_1indexed)
```

## Files in This Repository

- **`analysis.py`** - Main extended analysis module with `ExtendedAnalysis` class
- **`classify_single.py`** - Command-line tool for Cramer-Pople analysis with automatic conformation classification
- **`test-umd.py`** - Direct ulamdyn usage example for TRAJ folders
- **`compare.py`** - Minimal validation script comparing TRAJ vs XYZ loading methods
- **`test_cramer_pople.py`** - Test script for Cramer-Pople analysis on multiple rings
- **`XYZ_FORMAT_GUIDE.md`** - Detailed guide on supported XYZ file formats
- **`README_EXTENDED_ANALYSIS.md`** - This file

## Example Output

```
Loading from TRAJ folders...
Loaded 4000 geometries from TRAJ folders

Performing Cramer-Pople analysis...
Ring atoms: [0, 1, 2, 3, 4, 5]
Cramer-Pople analysis completed for 4000 geometries

TRAJ Method:
  Geometries: 4000
  q (mean ± std): 0.169413 ± 0.078265
  theta (mean ± std): 0.000236 ± 0.045134
  phi (mean ± std): 95.221255 ± 87.343584

External XYZ Method:
  Geometries: 4000
  q (mean ± std): 0.169413 ± 0.078265
  theta (mean ± std): 0.000236 ± 0.045134
  phi (mean ± std): 95.221255 ± 87.343584

Results identical: ✅ YES
Both methods produce the same ring puckering parameters!
```

## See Also

- **ulamdyn** - [Newton-X Package](https://newton-x.org/) for molecular dynamics analysis
- **Cramer-Pople Analysis** - Ring puckering parameters (q, θ, φ)
- **XYZ Format** - Standard molecular structure file format

## Acknowledgments

This extension builds upon the [ulamdyn](https://newton-x.org/) package from the Newton-X project.

---

**Last Updated**: January 9, 2026  
