import time
from typing import List, Dict, Any, Union, Optional, Tuple
import numpy as np
from .remoteclip_encoder import RemoteCLIPEncoder
from .qdrant_indexer import QdrantLocalIndexer
from .quantizer_4bit import ScalarQuantizer4Bit

class SemanticSearchEngine:
    """
    Unified Semantic Search Engine for Satellite Imagery with Active Learning and SQ4 Rescoring.
    
    Features:
    - Zero-shot natural language queries ("new construction near road") & Image-to-Image search.
    - 4-Bit Scalar Quantizer (SQ4) with two-stage SSD rescoring.
    - Active-learning relevance feedback (Rocchio rank adaptation from analyst confirms/rejects).
    - Hybrid filtering (Date, Sensor platform, Bounding Box spatial extents).
    """

    def __init__(
        self,
        encoder: RemoteCLIPEncoder = None,
        indexer: QdrantLocalIndexer = None,
        quantizer: ScalarQuantizer4Bit = None
    ):
        self.encoder = encoder or RemoteCLIPEncoder()
        self.indexer = indexer or QdrantLocalIndexer()
        self.quantizer = quantizer or ScalarQuantizer4Bit()
        
        # Active-learning session state
        self.confirmed_vectors: List[np.ndarray] = []
        self.rejected_vectors: List[np.ndarray] = []

    def record_feedback(self, vector: np.ndarray, action: str):
        """
        Incorporates analyst confirmation or rejection into active-learning session state.
        Action: 'CONFIRM' or 'REJECT'
        """
        v_norm = vector.astype(np.float32)
        norm = np.linalg.norm(v_norm)
        if norm > 1e-7:
            v_norm /= norm

        if action.upper() == "CONFIRM":
            self.confirmed_vectors.append(v_norm)
            if len(self.confirmed_vectors) > 20:
                self.confirmed_vectors.pop(0)
        elif action.upper() == "REJECT":
            self.rejected_vectors.append(v_norm)
            if len(self.rejected_vectors) > 20:
                self.rejected_vectors.pop(0)

    def _apply_rocchio_shift(self, query_vec: np.ndarray, alpha: float = 1.0, beta: float = 0.5, gamma: float = 0.25) -> np.ndarray:
        """
        Rocchio Relevance Feedback algorithm:
        q_new = alpha * q_base + (beta / |D_pos|) * sum(D_pos) - (gamma / |D_neg|) * sum(D_neg)
        """
        adapted = alpha * query_vec.copy().astype(np.float32)
        if self.confirmed_vectors:
            pos_mean = np.mean(self.confirmed_vectors, axis=0)
            adapted += beta * pos_mean
        if self.rejected_vectors:
            neg_mean = np.mean(self.rejected_vectors, axis=0)
            adapted -= gamma * neg_mean

        norm = np.linalg.norm(adapted)
        if norm > 1e-7:
            adapted /= norm
        return adapted

    def search_by_text(
        self,
        text_query: str,
        limit: int = 10,
        apply_active_learning: bool = True,
        use_sq4_rescore: bool = True
    ) -> Dict[str, Any]:
        """Performs semantic text-to-image search with optional active learning and SQ4 rescoring."""
        t0 = time.perf_counter()
        raw_query_vec = self.encoder.encode_text(text_query)

        if apply_active_learning and (self.confirmed_vectors or self.rejected_vectors):
            query_vec = self._apply_rocchio_shift(raw_query_vec)
            rank_adapted = True
        else:
            query_vec = raw_query_vec
            rank_adapted = False

        if use_sq4_rescore and self.quantizer.packed_vectors is not None and len(self.quantizer.point_ids) > 0:
            hits = self.quantizer.search_asymmetric(query_vec, top_candidates=limit*4, final_top_k=limit)
        else:
            hits = self.indexer.search(query_vec, limit=limit)

        latency_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "query": text_query,
            "latency_ms": round(latency_ms, 2),
            "total_results": len(hits),
            "rank_adapted_by_feedback": rank_adapted,
            "results": hits
        }

    def search_by_image(
        self,
        image_input: Union[str, np.ndarray],
        limit: int = 10,
        use_sq4_rescore: bool = True
    ) -> Dict[str, Any]:
        """Performs image-to-image similarity search."""
        t0 = time.perf_counter()
        img_vec = self.encoder.encode_image(image_input)

        if use_sq4_rescore and self.quantizer.packed_vectors is not None and len(self.quantizer.point_ids) > 0:
            hits = self.quantizer.search_asymmetric(img_vec, top_candidates=limit*4, final_top_k=limit)
        else:
            hits = self.indexer.search(img_vec, limit=limit)

        latency_ms = (time.perf_counter() - t0) * 1000.0

        return {
            "latency_ms": round(latency_ms, 2),
            "total_results": len(hits),
            "results": hits
        }

    def search_hybrid(
        self,
        text_query: str,
        sensor_filter: Optional[str] = None,
        date_range: Optional[Tuple[str, str]] = None,
        bbox_filter: Optional[Tuple[float, float, float, float]] = None,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Hybrid retrieval combining vector similarity with metadata filters:
        - Sensor: optical, Sentinel-2, Landsat, etc.
        - Date: (start_date, end_date)
        - BBox: (min_lat, max_lat, min_lon, max_lon)
        """
        t0 = time.perf_counter()
        query_vec = self.encoder.encode_text(text_query)

        def filter_fn(meta: Dict[str, Any]) -> bool:
            if sensor_filter and meta.get("sensor", "").lower() != sensor_filter.lower():
                return False
            if date_range:
                d = meta.get("timestamp", "")
                if d and (d < date_range[0] or d > date_range[1]):
                    return False
            if bbox_filter:
                lat = meta.get("latitude", 0.0)
                lon = meta.get("longitude", 0.0)
                min_lat, max_lat, min_lon, max_lon = bbox_filter
                if not (min_lat <= lat <= max_lat and min_lon <= lon <= max_lon):
                    return False
            return True

        if self.quantizer.packed_vectors is not None and len(self.quantizer.point_ids) > 0:
            hits = self.quantizer.search_asymmetric(query_vec, top_candidates=limit*5, final_top_k=limit, filter_fn=filter_fn)
        else:
            hits = self.indexer.search(query_vec, limit=limit*3)
            hits = [h for h in hits if filter_fn(h.get("payload", {}))][:limit]

        latency_ms = (time.perf_counter() - t0) * 1000.0
        return {
            "query": text_query,
            "filter_applied": {
                "sensor": sensor_filter,
                "date_range": date_range,
                "bbox": bbox_filter
            },
            "latency_ms": round(latency_ms, 2),
            "total_results": len(hits),
            "results": hits
        }
