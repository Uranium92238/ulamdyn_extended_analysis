# Extended Analysis with ulamdyn

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
- Ring puckering parameter calculation
- Support for multiple ring structures
- Returns pandas DataFrame with q, theta, phi parameters

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

The custom parser supports XYZ files with metadata in comment lines:

```
38
TRAJ = 1 | Time = 3.0 fs | DE5.4 = 0.0815 eV | 
C        0.65678931  -1.66620430   1.17573480 
C        1.36722008  -1.51210075   0.05283259 
...
38
TRAJ = 7 | Time = 4.5 fs | DE5.4 = 0.0674 eV | 
C        0.58984919  -1.68638730   1.25779563 
...
```

Format:
- Line 1: Number of atoms
- Line 2: Comment/metadata (can include TRAJ and Time info)
- Lines 3+: Element X Y Z coordinates

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

## Comparison: TRAJ vs XYZ Loading

| Feature | TRAJ Folders | XYZ Files |
|---------|-------------|-----------|
| Source | TRAJ*/RESULTS/geometries.xyz | Any XYZ file |
| Setup | Requires TRAJ folder structure | Single/multiple XYZ files |
| Flexibility | Limited to TRAJ format | Any XYZ source |
| Metadata | Automatic from folder structure | Parsed from comment lines |
| Use Case | Original workflow | Custom workflows, external data |

## Troubleshooting

### Issue: "ValueError: could not convert string to float"
**Solution**: Your XYZ file has a different format. Try setting `use_ulamdyn_parser=True` or vice versa:
```python
analysis.load_from_xyz("file.xyz", use_ulamdyn_parser=True)
```

### Issue: "No geometries loaded"
**Solution**: Check your XYZ file format. Ensure it follows the standard format with atom count, comment line, and coordinates.

### Issue: Ring atoms not found in Cramer-Pople analysis
**Solution**: Verify your ring atom indices are correct (0-indexed) and correspond to actual atoms in your molecule.

### Issue: Clustering fails
**Solution**: Ensure you've loaded data first and that the dataset has been created properly. Check `analysis.summary()` to verify data is loaded.

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

## See Also

- `analysis_usage_examples.py` - Complete working examples
- Original `analysis.py` - Source code with detailed comments
- ulamdyn documentation - For advanced features

---

**Last Updated**: January 2026
