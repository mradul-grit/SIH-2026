import numpy as np
from typing import Dict, Tuple, Any

class RegistrationValidator:
    """
    Validates bi-temporal image pair alignment using 2D phase correlation.
    Warns if translational shift between T1 and T2 exceeds acceptable tolerance.
    """

    def __init__(self, max_allowed_shift: float = 3.0):
        self.max_allowed_shift = max_allowed_shift

    def compute_alignment(self, t1_img: np.ndarray, t2_img: np.ndarray) -> Dict[str, Any]:
        """
        Calculates shift (dx, dy) and registration quality score [0.0, 1.0].
        t1_img, t2_img: (H, W, C) or (H, W) in [0, 1] or [0, 255].
        """
        # Convert to grayscale
        if t1_img.ndim == 3 and t1_img.shape[2] == 3:
            g1 = 0.2989 * t1_img[:, :, 0] + 0.5870 * t1_img[:, :, 1] + 0.1140 * t1_img[:, :, 2]
            g2 = 0.2989 * t2_img[:, :, 0] + 0.5870 * t2_img[:, :, 1] + 0.1140 * t2_img[:, :, 2]
        else:
            g1, g2 = t1_img.squeeze(), t2_img.squeeze()

        # 2D Fast Fourier Transform
        f1 = np.fft.fft2(g1)
        f2 = np.fft.fft2(g2)
        eps = 1e-10
        # Cross-power spectrum
        cross_power = (f1 * np.conj(f2)) / (np.abs(f1 * np.conj(f2)) + eps)
        r = np.fft.ifft2(cross_power)
        r = np.real(r)

        # Peak location
        y_peak, x_peak = np.unravel_index(np.argmax(r), r.shape)
        h, w = r.shape
        dy = y_peak if y_peak < h // 2 else y_peak - h
        dx = x_peak if x_peak < w // 2 else x_peak - w

        shift_dist = float(np.sqrt(dx**2 + dy**2))
        peak_val = float(np.max(r))

        is_aligned = shift_dist <= self.max_allowed_shift
        confidence = float(np.clip(peak_val * 5.0, 0.0, 1.0))

        return {
            "shift_dx": float(dx),
            "shift_dy": float(dy),
            "shift_distance": round(shift_dist, 2),
            "peak_correlation": round(peak_val, 4),
            "is_aligned": is_aligned,
            "registration_confidence": round(confidence, 3),
            "status": "VALID_ALIGNMENT" if is_aligned else "MISALIGNMENT_DETECTED"
        }
