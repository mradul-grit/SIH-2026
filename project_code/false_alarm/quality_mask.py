import numpy as np
from typing import Dict, Tuple, Any

class QualityMaskFilter:
    """
    Detects cloud contamination, dense shadows, and extreme radiometric discrepancy.
    Suppresses false positives triggered by clouds or moving cast shadows.
    """

    def __init__(self, cloud_bright_thresh: float = 0.85, shadow_dark_thresh: float = 0.10):
        self.cloud_thresh = cloud_bright_thresh
        self.shadow_thresh = shadow_dark_thresh

    def assess_pair_quality(
        self,
        t1_img: np.ndarray,
        t2_img: np.ndarray
    ) -> Dict[str, Any]:
        """
        Input: normalized [0, 1] RGB images (H, W, 3).
        Returns cloud/shadow mask and radiometric suitability flag.
        """
        # Luminance
        l1 = 0.299 * t1_img[..., 0] + 0.587 * t1_img[..., 1] + 0.114 * t1_img[..., 2]
        l2 = 0.299 * t2_img[..., 0] + 0.587 * t2_img[..., 1] + 0.114 * t2_img[..., 2]

        # Cloud detection (high brightness, low color saturation)
        c1 = (l1 > self.cloud_thresh) & (np.std(t1_img, axis=-1) < 0.08)
        c2 = (l2 > self.cloud_thresh) & (np.std(t2_img, axis=-1) < 0.08)
        cloud_mask = c1 | c2

        # Shadow detection
        s1 = l1 < self.shadow_thresh
        s2 = l2 < self.shadow_thresh
        shadow_mask = s1 | s2

        cloud_ratio = float(np.mean(cloud_mask))
        shadow_ratio = float(np.mean(shadow_mask))

        # Overall quality score
        quality_score = max(0.0, 1.0 - (cloud_ratio * 2.0 + shadow_ratio * 0.5))

        return {
            "cloud_fraction": round(cloud_ratio, 4),
            "shadow_fraction": round(shadow_ratio, 4),
            "quality_score": round(quality_score, 3),
            "cloud_mask": cloud_mask.astype(np.uint8),
            "shadow_mask": shadow_mask.astype(np.uint8),
            "is_usable": quality_score >= 0.60
        }
