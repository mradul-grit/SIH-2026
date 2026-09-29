from typing import List, Dict, Any, Tuple
import numpy as np
import torch

class TemporalSequenceAnalyzer:
    """
    Multi-Temporal Sequence Analyzer (T1 -> T2 -> T3 -> ... -> Tn).
    Performs pairwise forward change detection across arbitrary time intervals.
    """

    def __init__(self, model: torch.nn.Module, device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.model = model
        self.device = device
        self.model.to(self.device)
        self.model.eval()

    def analyze_sequence(
        self,
        images: List[np.ndarray],
        timestamps: List[str],
        threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        images: List of normalized (H, W, 3) arrays sorted by timestamp.
        timestamps: ISO date strings or year strings.
        Returns pairwise change masks and metrics.
        """
        assert len(images) == len(timestamps), "Mismatch between image count and timestamps"
        if len(images) < 2:
            return []

        pairwise_results = []
        with torch.no_grad():
            for i in range(len(images) - 1):
                t_prev = torch.from_numpy(images[i].transpose(2, 0, 1)).unsqueeze(0).float().to(self.device)
                t_curr = torch.from_numpy(images[i+1].transpose(2, 0, 1)).unsqueeze(0).float().to(self.device)

                out = self.model(t_prev, t_curr)
                logits = out["change_logits"].squeeze().cpu().numpy()
                probs = 1.0 / (1.0 + np.exp(-logits))
                mask = (probs > threshold).astype(np.uint8)

                change_pixels = int(np.sum(mask > 0))
                change_percent = round(100.0 * (change_pixels / mask.size), 3)

                pairwise_results.append({
                    "from_timestamp": timestamps[i],
                    "to_timestamp": timestamps[i+1],
                    "step_index": i + 1,
                    "change_pixels": change_pixels,
                    "change_percentage": change_percent,
                    "change_mask": mask,
                    "probability_map": probs
                })

        return pairwise_results
