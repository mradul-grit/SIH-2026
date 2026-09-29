from typing import List, Dict, Any, Optional
import numpy as np

class DiscoveryClusterer:
    """
    Unsupervised Semantic Discovery using RemoteCLIP Embeddings + UMAP + HDBSCAN.
    Groups satellite tiles into thematic clusters (e.g., dense urban, industrial, rural, water bodies)
    without manual labels.
    """

    def __init__(self, n_components: int = 2, min_cluster_size: int = 5):
        self.n_components = n_components
        self.min_cluster_size = min_cluster_size

    def reduce_dimensions(self, embeddings: np.ndarray) -> np.ndarray:
        """Projects high-dimensional vectors to 2D using pure NumPy SVD PCA (100% DLL-safe)."""
        try:
            import umap
            reducer = umap.UMAP(n_components=self.n_components, random_state=42, n_neighbors=15)
            return reducer.fit_transform(embeddings)
        except Exception:
            # Pure NumPy SVD PCA - zero external DLL dependencies
            X = embeddings.astype(np.float64)
            X_centered = X - np.mean(X, axis=0)
            U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
            return np.dot(X_centered, Vt[:self.n_components].T)

    def _dbscan_pure_numpy(self, dist_matrix: np.ndarray, eps: float = 0.4, min_samples: int = 3) -> np.ndarray:
        """Pure NumPy DBSCAN implementation with zero external C-extension or DLL dependencies."""
        n = dist_matrix.shape[0]
        labels = np.full(n, -1, dtype=int)
        cluster_id = 0
        visited = np.zeros(n, dtype=bool)

        for i in range(n):
            if visited[i]:
                continue
            visited[i] = True
            neighbors = np.where(dist_matrix[i] <= eps)[0]
            if len(neighbors) < min_samples:
                labels[i] = -1
            else:
                labels[i] = cluster_id
                seed_set = list(neighbors[neighbors != i])
                s_idx = 0
                while s_idx < len(seed_set):
                    curr = seed_set[s_idx]
                    s_idx += 1
                    if not visited[curr]:
                        visited[curr] = True
                        curr_neighbors = np.where(dist_matrix[curr] <= eps)[0]
                        if len(curr_neighbors) >= min_samples:
                            for cn in curr_neighbors:
                                if cn not in seed_set:
                                    seed_set.append(cn)
                    if labels[curr] == -1:
                        labels[curr] = cluster_id
                cluster_id += 1
        return labels

    def compute_hybrid_distance_matrix(
        self,
        embeddings: np.ndarray,
        coordinates: np.ndarray,
        alpha: float = 0.7
    ) -> np.ndarray:
        """
        Computes pairwise hybrid distance matrix:
        D_ij = alpha * D_cosine(e_i, e_j) + (1 - alpha) * D_haversine(coord_i, coord_j)
        """
        n = len(embeddings)
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-7
        normed = embeddings / norms
        cosine_sim = np.clip(np.dot(normed, normed.T), -1.0, 1.0)
        d_cosine = np.clip((1.0 - cosine_sim) / 2.0, 0.0, 1.0)

        lat = np.radians(coordinates[:, 0])
        lon = np.radians(coordinates[:, 1])
        dlat = lat[:, np.newaxis] - lat[np.newaxis, :]
        dlon = lon[:, np.newaxis] - lon[np.newaxis, :]
        a = np.sin(dlat / 2.0)**2 + np.cos(lat[:, np.newaxis]) * np.cos(lat[np.newaxis, :]) * np.sin(dlon / 2.0)**2
        c = 2.0 * np.arcsin(np.clip(np.sqrt(a), 0.0, 1.0))
        d_geo_km = c * 6371.0
        max_geo = float(np.max(d_geo_km)) if np.max(d_geo_km) > 0 else 1.0
        d_geo_norm = np.clip(d_geo_km / max_geo, 0.0, 1.0)

        d_hybrid = (alpha * d_cosine + (1.0 - alpha) * d_geo_norm).astype(np.float64)
        np.fill_diagonal(d_hybrid, 0.0)
        return d_hybrid

    def cluster(self, embeddings: np.ndarray, coordinates: Optional[np.ndarray] = None) -> np.ndarray:
        """Finds density-based clusters using HDBSCAN with hybrid Cosine+Haversine metric."""
        if coordinates is not None and len(coordinates) == len(embeddings):
            dist_matrix = self.compute_hybrid_distance_matrix(embeddings, coordinates)
        else:
            # Euclidean distance matrix from embeddings
            diff = embeddings[:, np.newaxis, :] - embeddings[np.newaxis, :, :]
            dist_matrix = np.linalg.norm(diff, axis=-1)
            d_max = np.max(dist_matrix) if np.max(dist_matrix) > 0 else 1.0
            dist_matrix /= d_max

        try:
            import hdbscan
            clusterer = hdbscan.HDBSCAN(min_cluster_size=self.min_cluster_size, metric="precomputed")
            return clusterer.fit_predict(dist_matrix)
        except Exception:
            return self._dbscan_pure_numpy(dist_matrix, eps=0.4, min_samples=self.min_cluster_size)

    def analyze_dataset(
        self,
        embeddings: np.ndarray,
        tile_metadata: List[Dict[str, Any]],
        use_hybrid_metric: bool = True
    ) -> Dict[str, Any]:
        """
        Runs projection and clustering on satellite tile embeddings.
        Returns 2D coordinates, cluster IDs, and cluster summaries.
        """
        assert len(embeddings) == len(tile_metadata)
        if len(embeddings) == 0:
            return {"points": [], "clusters": {}}

        coords_geo = np.array([
            [meta.get("latitude", 0.0), meta.get("longitude", 0.0)]
            for meta in tile_metadata
        ], dtype=np.float32)

        coords_2d = self.reduce_dimensions(embeddings)
        cluster_labels = self.cluster(embeddings, coordinates=coords_geo if use_hybrid_metric else None)

        points = []
        clusters_summary = {}

        for i in range(len(embeddings)):
            c_id = int(cluster_labels[i])
            pt = {
                "tile_id": tile_metadata[i].get("tile_id", f"tile_{i}"),
                "x": round(float(coords_2d[i, 0]), 4),
                "y": round(float(coords_2d[i, 1]), 4),
                "cluster_id": c_id,
                "dataset": tile_metadata[i].get("dataset_name", "N/A"),
                "image_path": tile_metadata[i].get("image_path", ""),
                "timestamp": tile_metadata[i].get("timestamp", "2020-01-01"),
                "latitude": tile_metadata[i].get("latitude", 0.0),
                "longitude": tile_metadata[i].get("longitude", 0.0)
            }
            points.append(pt)

            if c_id not in clusters_summary:
                clusters_summary[c_id] = {
                    "cluster_id": c_id,
                    "label": f"Cluster {c_id}" if c_id != -1 else "Noise / Outliers",
                    "count": 0,
                    "representative_tiles": []
                }
            clusters_summary[c_id]["count"] += 1
            if len(clusters_summary[c_id]["representative_tiles"]) < 3:
                clusters_summary[c_id]["representative_tiles"].append(pt["tile_id"])

        return {
            "total_points": len(points),
            "total_clusters": len([c for c in clusters_summary.keys() if c != -1]),
            "noise_points": clusters_summary.get(-1, {}).get("count", 0),
            "points": points,
            "clusters": clusters_summary
        }
