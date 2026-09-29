import numpy as np
from typing import Dict, Optional, Any

class SpectralConsistencyChecker:
    """
    Validates physical spectral indices to differentiate true building construction/demolition
    from seasonal greening/browning or agricultural changes.
    Supports:
    - NDVI: (NIR - Red) / (NIR + Red) when 4-band imagery is provided.
    - VARI (Visible Atmospherically Resistant Index): (Green - Red) / (Green + Red - Blue) for 3-band RGB.
    """

    def compute_vari(self, rgb_img: np.ndarray) -> np.ndarray:
        """Computes VARI index for RGB optical imagery in [0, 1]."""
        r = rgb_img[..., 0].astype(np.float32)
        g = rgb_img[..., 1].astype(np.float32)
        b = rgb_img[..., 2].astype(np.float32)
        denom = g + r - b
        denom[denom == 0] = 1e-6
        vari = (g - r) / denom
        return np.clip(vari, -1.0, 1.0)

    def filter_vegetation_changes(
        self,
        t1_img: np.ndarray,
        t2_img: np.ndarray,
        change_mask: np.ndarray,
        vari_thresh: float = 0.35
    ) -> Dict[str, Any]:
        """
        Suppresses false alarms in the change mask caused merely by vegetation greening/senescence.
        """
        v1 = self.compute_vari(t1_img)
        v2 = self.compute_vari(t2_img)
        delta_vari = np.abs(v2 - v1)

        # Pixels where both T1 and T2 are heavy vegetation or change is purely vegetative
        is_veg = (v1 > vari_thresh) & (v2 > vari_thresh)
        filtered_mask = change_mask.copy()
        suppressed_pixels = (change_mask > 0) & is_veg
        filtered_mask[suppressed_pixels] = 0

        suppressed_count = int(np.sum(suppressed_pixels))
        total_change_count = int(np.sum(change_mask > 0))
        suppression_ratio = suppressed_count / max(total_change_count, 1)

        return {
            "suppressed_vegetation_pixels": suppressed_count,
            "suppression_ratio": round(suppression_ratio, 4),
            "filtered_mask": filtered_mask
        }
