import numpy as np
from typing import Dict, List, Tuple, Any
from scipy import ndimage

class MorphologicalPostProcessor:
    """
    Cleans neural change maps using morphological filtering and connected components.
    Removes isolated pixel noise while preserving building geometry.
    """

    def __init__(self, min_area_pixels: int = 25):
        self.min_area = min_area_pixels

    def remove_small_components(self, binary_mask: np.ndarray, min_size: int = None) -> np.ndarray:
        """Removes connected components smaller than min_size pixels."""
        thresh = min_size if min_size is not None else self.min_area
        labeled, num_features = ndimage.label(binary_mask > 0)
        if num_features == 0:
            return binary_mask

        sizes = ndimage.sum(binary_mask > 0, labeled, range(num_features + 1))
        mask_sizes = sizes < thresh
        remove_pixel = mask_sizes[labeled]
        cleaned = binary_mask.copy()
        cleaned[remove_pixel] = 0
        return cleaned

    def fill_holes(self, binary_mask: np.ndarray) -> np.ndarray:
        """Fills internal holes inside detected building contours."""
        return ndimage.binary_fill_holes(binary_mask > 0).astype(binary_mask.dtype)

    def morphological_clean(
        self,
        binary_mask: np.ndarray,
        open_radius: int = 1,
        close_radius: int = 2
    ) -> np.ndarray:
        """Performs opening to discard noise and closing to join fragmented building edges."""
        struct_open = ndimage.generate_binary_structure(2, 1)
        struct_close = ndimage.generate_binary_structure(2, 2)

        # Opening: erosion followed by dilation
        opened = ndimage.binary_opening(binary_mask > 0, structure=struct_open, iterations=open_radius)
        # Closing: dilation followed by erosion
        closed = ndimage.binary_closing(opened, structure=struct_close, iterations=close_radius)
        return closed.astype(binary_mask.dtype)

    def process(self, raw_binary_mask: np.ndarray) -> Dict[str, Any]:
        """Runs full postprocessing pipeline."""
        m1 = self.morphological_clean(raw_binary_mask)
        m2 = self.remove_small_components(m1, self.min_area)
        m3 = self.fill_holes(m2)

        initial_count = int(np.sum(raw_binary_mask > 0))
        final_count = int(np.sum(m3 > 0))

        return {
            "initial_change_pixels": initial_count,
            "final_change_pixels": final_count,
            "cleaned_mask": m3
        }

    def benchmark_component_thresholds(
        self,
        raw_mask: np.ndarray,
        thresholds: List[int] = [5, 10, 25, 50, 100]
    ) -> Dict[int, int]:
        """Profiles the effect of different area filters."""
        results = {}
        for th in thresholds:
            cleaned = self.remove_small_components(raw_mask, min_size=th)
            results[th] = int(np.sum(cleaned > 0))
        return results
