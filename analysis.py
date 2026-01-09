import numpy as np
import pandas as pd
import ulamdyn as umd
import os


class ExtendedAnalysis:
    """
    Extended analysis class that supports loading geometries from both
    TRAJ folders (original method) and standalone XYZ files.
    """
    
    def __init__(self):
        self.geoms_loader = umd.GetCoords()
        self.coords = None
        self.labels = None
        self.source_type = None
    
    def load_from_trajs(self):
        """Load geometries from TRAJ folders (original method)"""
        print("Loading from TRAJ folders...")
        self.geoms_loader.read_all_trajs()
        self.geoms_loader.build_dataframe()
        self.source_type = "traj"
        print(f"Loaded {len(self.geoms_loader.xyz)} geometries from TRAJ folders")
        return self
    
    def _parse_xyz_custom(self, xyz_file):
        """
        Custom XYZ parser that handles files with metadata in comment lines.
        This works with files that have format:
        - Line 1: number of atoms
        - Line 2: metadata (e.g., "TRAJ = 1 | Time = 3.0 fs | ...")
        - Lines 3+: element x y z
        
        Also parses Time and TRAJ information from comment lines.
        """
        geometries = []
        labels = []
        times = []
        trajs = []
        
        with open(xyz_file, 'r') as f:
            lines = f.readlines()
        
        i = 0
        geom_idx = 0
        while i < len(lines):
            try:
                # Read number of atoms
                n_atoms = int(lines[i].strip())
                i += 1
                
                # Read comment/metadata line (if it exists)
                # Handle cases where comment line might be missing or empty
                if i < len(lines):
                    comment = lines[i].strip() if lines[i].strip() else f"Geometry {geom_idx}"
                else:
                    comment = f"Geometry {geom_idx}"
                
                labels.append(comment)
                
                # Parse Time and TRAJ from comment if available
                # Format: "TRAJ = 1 | Time = 3.0 fs | ..."
                # Defaults: use geometry index for time, 0 for trajectory
                time_val = geom_idx
                traj_val = 0
                
                # Only try to parse if comment contains these keywords
                if comment and "Time" in comment:
                    try:
                        # Extract time value
                        time_part = comment.split("Time")[1].split("|")[0]
                        time_str = ''.join([c for c in time_part if c.isdigit() or c == '.' or c == '-'])
                        time_val = float(time_str) if time_str else geom_idx
                    except:
                        time_val = geom_idx
                
                if comment and "TRAJ" in comment:
                    try:
                        # Extract trajectory number
                        traj_part = comment.split("TRAJ")[1].split("|")[0]
                        traj_str = ''.join([c for c in traj_part if c.isdigit()])
                        traj_val = int(traj_str) if traj_str else 0
                    except:
                        traj_val = 0
                
                times.append(time_val)
                trajs.append(traj_val)
                i += 1
                
                # Read atomic coordinates
                coords = []
                for j in range(n_atoms):
                    if i >= len(lines):
                        break
                    parts = lines[i].strip().split()
                    if len(parts) >= 4:  # element x y z
                        x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                        coords.append([x, y, z])
                    i += 1
                
                if len(coords) == n_atoms:
                    geometries.append(coords)
                    geom_idx += 1
                else:
                    # Remove incomplete geometry metadata
                    labels.pop()
                    times.pop()
                    trajs.pop()
                    
            except (ValueError, IndexError) as e:
                # Skip malformed entries
                i += 1
                continue
        
        if not geometries:
            raise ValueError(f"No valid geometries found in {xyz_file}")
        
        return (np.array(geometries), np.array(labels), 
                np.array(times), np.array(trajs))
    
    def load_from_xyz(self, xyz_file, use_ulamdyn_parser=False):
        """
        Load geometries from a standalone XYZ file.
        
        Parameters:
        -----------
        xyz_file : str
            Path to the XYZ file containing multiple geometries
        use_ulamdyn_parser : bool
            If True, use ulamdyn's built-in parser (for TRAJ-style XYZ files).
            If False (default), use custom parser for files with metadata in comments.
        """
        print(f"Loading from XYZ file: {xyz_file}")
        
        if not os.path.exists(xyz_file):
            raise FileNotFoundError(f"XYZ file not found: {xyz_file}")
        
        try:
            if use_ulamdyn_parser:
                # Use ulamdyn's from_xyz method
                coords, labels = self.geoms_loader.from_xyz(xyz_file)
                # Create dummy Time and TRAJ
                times = np.arange(len(coords))
                trajs = np.zeros(len(coords), dtype=int)
            else:
                # Use custom parser
                coords, labels, times, trajs = self._parse_xyz_custom(xyz_file)
            
            # Manually set the loaded data to the geoms_loader object
            self.geoms_loader.xyz = coords
            self.geoms_loader.labels = labels
            # traj_time should be 2D array with shape (n_geoms, 2) -> [TRAJ, Time]
            self.geoms_loader.traj_time = np.column_stack([trajs, times])
            self.geoms_loader.trajectories = trajs
            self.coords = coords
            self.labels = labels
            self.source_type = "xyz"
            
            # Create a dataset compatible with ClusterGeoms
            # Reshape xyz to 2D: (n_geoms, n_atoms * 3)
            n_geoms = len(coords)
            flattened_coords = coords.reshape(n_geoms, -1)
            
            # Create DataFrame with TRAJ and Time columns
            df = pd.DataFrame(flattened_coords)
            df.insert(0, "Time", times)
            df.insert(0, "TRAJ", trajs)
            self.geoms_loader.dataset = df
            
            print(f"Loaded {len(coords)} geometries from XYZ file")
            print(f"Geometry shape: {coords.shape}")
            
        except Exception as e:
            print(f"Error loading XYZ file: {e}")
            print("Trying alternative parser...")
            # Try the other parser if one fails
            try:
                if use_ulamdyn_parser:
                    coords, labels, times, trajs = self._parse_xyz_custom(xyz_file)
                else:
                    coords, labels = self.geoms_loader.from_xyz(xyz_file)
                    times = np.arange(len(coords))
                    trajs = np.zeros(len(coords), dtype=int)
                
                self.geoms_loader.xyz = coords
                self.geoms_loader.labels = labels
                # traj_time should be 2D array with shape (n_geoms, 2) -> [TRAJ, Time]
                self.geoms_loader.traj_time = np.column_stack([trajs, times])
                self.geoms_loader.trajectories = trajs
                self.coords = coords
                self.labels = labels
                self.source_type = "xyz"
                
                # Create a dataset compatible with ClusterGeoms
                n_geoms = len(coords)
                flattened_coords = coords.reshape(n_geoms, -1)
                df = pd.DataFrame(flattened_coords)
                df.insert(0, "Time", times)
                df.insert(0, "TRAJ", trajs)
                self.geoms_loader.dataset = df
                
                print(f"Loaded {len(coords)} geometries from XYZ file")
                print(f"Geometry shape: {coords.shape}")
            except Exception as e2:
                raise RuntimeError(f"Failed to load XYZ file with both parsers: {e}, {e2}")
        
        return self
    
    def load_from_multiple_xyz(self, xyz_files, use_ulamdyn_parser=False):
        """
        Load and concatenate geometries from multiple XYZ files.
        
        Parameters:
        -----------
        xyz_files : list of str
            List of paths to XYZ files
        use_ulamdyn_parser : bool
            If True, use ulamdyn's built-in parser. If False, use custom parser.
        """
        all_coords = []
        all_labels = []
        all_times = []
        all_trajs = []
        
        print(f"Loading from {len(xyz_files)} XYZ files...")
        
        for xyz_file in xyz_files:
            if not os.path.exists(xyz_file):
                print(f"Warning: File not found, skipping: {xyz_file}")
                continue
            
            try:
                if use_ulamdyn_parser:
                    coords, labels = self.geoms_loader.from_xyz(xyz_file)
                    times = np.arange(len(coords))
                    trajs = np.zeros(len(coords), dtype=int)
                else:
                    coords, labels, times, trajs = self._parse_xyz_custom(xyz_file)
                
                all_coords.append(coords)
                all_labels.append(labels)
                all_times.append(times)
                all_trajs.append(trajs)
                print(f"  Loaded {len(coords)} geometries from {os.path.basename(xyz_file)}")
            except Exception as e:
                print(f"Warning: Error loading {xyz_file}: {e}")
                continue
        
        if not all_coords:
            raise ValueError("No geometries loaded from any file")
        
        # Concatenate all geometries
        self.coords = np.concatenate(all_coords, axis=0)
        self.labels = np.concatenate(all_labels, axis=0)
        all_trajs_concat = np.concatenate(all_trajs, axis=0)
        all_times_concat = np.concatenate(all_times, axis=0)
        self.geoms_loader.xyz = self.coords
        self.geoms_loader.labels = self.labels
        # traj_time should be 2D array with shape (n_geoms, 2) -> [TRAJ, Time]
        self.geoms_loader.traj_time = np.column_stack([all_trajs_concat, all_times_concat])
        self.geoms_loader.trajectories = all_trajs_concat
        self.source_type = "xyz_multiple"
        
        # Create a dataset compatible with ClusterGeoms
        n_geoms = len(self.coords)
        flattened_coords = self.coords.reshape(n_geoms, -1)
        df = pd.DataFrame(flattened_coords)
        df.insert(0, "Time", all_times_concat)
        df.insert(0, "TRAJ", all_trajs_concat)
        self.geoms_loader.dataset = df
        
        print(f"Total: {len(self.coords)} geometries loaded")
        print(f"Geometry shape: {self.coords.shape}")
        
        return self
    
    def perform_clustering(self, method='kmeans', n_clusters=5, **kwargs):
        """
        Perform clustering analysis on the loaded geometries.
        
        Parameters:
        -----------
        method : str
            Clustering method ('kmeans', 'dbscan', 'hierarchical', etc.)
        n_clusters : int
            Number of clusters (for methods that require it)
        **kwargs : additional arguments to pass to ClusterGeoms
        
        Returns:
        --------
        ClusterGeoms object
        """
        if self.geoms_loader.xyz is None:
            raise ValueError("No geometries loaded. Call load_from_trajs() or load_from_xyz() first.")
        
        print(f"\nPerforming clustering analysis using {method}...")
        print(f"Data shape: {self.geoms_loader.xyz.shape}")
        
        # Use the dataset (DataFrame) for clustering
        if self.geoms_loader.dataset is not None:
            data_for_clustering = self.geoms_loader.dataset
        else:
            # Fallback: reshape xyz data to 2D for clustering
            n_geoms = len(self.geoms_loader.xyz)
            data_for_clustering = self.geoms_loader.xyz.reshape(n_geoms, -1)
        
        # Create ClusterGeoms object with the loaded data
        cluster_obj = umd.ClusterGeoms(data=data_for_clustering, **kwargs)
        
        # Perform clustering based on method
        if method == 'kmeans':
            cluster_obj.kmeans(n_clusters=n_clusters)
        elif method == 'dbscan':
            cluster_obj.dbscan(**kwargs)
        elif method == 'hierarchical':
            cluster_obj.hierarchical(n_clusters=n_clusters)
        else:
            raise ValueError(f"Unknown clustering method: {method}")
        
        # Get cluster labels from the model
        cluster_labels = cluster_obj.model.labels_
        print(f"Clustering completed. Found {len(np.unique(cluster_labels))} clusters")
        
        return cluster_obj
    
    def perform_cramer_pople_analysis(self, ring_atom_indices):
        """
        Perform Cramer-Pople analysis on ring structures.
        
        Parameters:
        -----------
        ring_atom_indices : list
            List of atom indices that form the ring (0-indexed)
        
        Returns:
        --------
        RingParams object with puckering parameters
        """
        if self.geoms_loader.xyz is None:
            raise ValueError("No geometries loaded. Call load_from_trajs() or load_from_xyz() first.")
        
        print(f"\nPerforming Cramer-Pople analysis...")
        print(f"Ring atoms: {ring_atom_indices}")
        
        n_geoms = len(self.geoms_loader.xyz)
        results = []
        
        for i, geom in enumerate(self.geoms_loader.xyz):
            # Extract ring coordinates for this geometry (0-indexed)
            ring_coords = geom[ring_atom_indices]
            
            # Create RingParams object and calculate puckering parameters
            # RingParams expects 1-indexed atoms!
            ring_atom_indices_1indexed = [idx + 1 for idx in ring_atom_indices]
            ring_params = umd.RingParams(
                ring_atom_ind=ring_atom_indices_1indexed,
                ring_coords=ring_coords
            )
            
            # Get puckering coordinates
            # For 6-membered rings: returns [q2, q3, phi2, phi3]
            # Need to convert to polar coords: Q, theta, phi
            try:
                pucker = ring_params.get_pucker_coords(ring_coords)
                # Convert to polar coordinates using ulamdyn's method
                polar = ring_params._cp_to_polar(pucker.reshape(1, -1))
                q_val = polar['Q'][0]
                theta_val = polar['theta'][0] * np.pi / 180  # Convert to radians
                phi_val = polar['phi'][0]
            except Exception as e:
                q_val, theta_val, phi_val = None, None, None
            
            results.append({
                'geometry_idx': i,
                'q': q_val,
                'theta': theta_val,
                'phi': phi_val,
            })
            
            if (i + 1) % 100 == 0:
                print(f"  Processed {i + 1}/{n_geoms} geometries")
        
        print(f"Cramer-Pople analysis completed for {n_geoms} geometries")
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(results)
        
        return df
    
    def get_geoms_loader(self):
        """Return the geoms_loader object for further analysis"""
        return self.geoms_loader
    
    def summary(self):
        """Print a summary of loaded data"""
        print("\n" + "="*50)
        print("Analysis Summary")
        print("="*50)
        print(f"Source type: {self.source_type}")
        if self.geoms_loader.xyz is not None:
            print(f"Number of geometries: {len(self.geoms_loader.xyz)}")
            print(f"Geometry shape: {self.geoms_loader.xyz.shape}")
            print(f"Number of atoms: {self.geoms_loader.xyz.shape[1]}")
        else:
            print("No geometries loaded")
        print("="*50)


# Example usage for backward compatibility
if __name__ == "__main__":
    # Original method (from TRAJ folders)
    print("=" * 60)
    print("Method 1: Loading from TRAJ folders (original)")
    print("=" * 60)
    
    if os.path.exists("TRAJ"):
        analysis1 = ExtendedAnalysis()
        analysis1.load_from_trajs()
        analysis1.summary()
    else:
        print("No TRAJ folders found, skipping this method")
    
    # New method (from XYZ files)
    print("\n" + "=" * 60)
    print("Method 2: Loading from standalone XYZ file")
    print("=" * 60)
    
    xyz_file = "Geoms_Hopping_4.5.xyz"
    if os.path.exists(xyz_file):
        analysis2 = ExtendedAnalysis()
        analysis2.load_from_xyz(xyz_file)
        analysis2.summary()
        
        # Example: Perform clustering
        print("\n" + "=" * 60)
        print("Performing clustering analysis")
        print("=" * 60)
        cluster_result = analysis2.perform_clustering(method='kmeans', n_clusters=5)
        print(f"Cluster labels: {cluster_result.model.labels_[:20]}...")  # Show first 20
        
        # Example: Cramer-Pople analysis (you need to specify ring atoms)
        # Uncomment and modify the ring_atoms list for your molecule
        # print("\n" + "=" * 60)
        # print("Performing Cramer-Pople analysis")
        # print("=" * 60)
        # ring_atoms = [0, 1, 2, 3, 4, 5]  # Example: 6-membered ring
        # cp_results = analysis2.perform_cramer_pople_analysis(ring_atoms)
        # print(cp_results.head())
    else:
        print(f"XYZ file {xyz_file} not found")