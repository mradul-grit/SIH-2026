import json
from pathlib import Path
from typing import List, Dict, Tuple
import numpy as np
import torch
from .metrics import compute_metrics

class ThresholdOptimizer:
    """
    Optimizes change detection threshold on validation data.
    Sweeps [0.10, 0.90] to maximize F1 while enforcing FPR <= 0.15.
    """

    def __init__(self, thresholds: List[float] = None):
        if thresholds is None:
            self.thresholds = [round(x, 2) for x in np.arange(0.10, 0.95, 0.05)]
        else:
            self.thresholds = thresholds

    def optimize(
        self,
        probabilities: np.ndarray,
        ground_truth: np.ndarray,
        max_allowed_fpr: float = 0.15
    ) -> Dict[str, float]:
        best_score = -1.0
        best_thresh = 0.5
        best_metrics = {}
        all_results = []

        for th in self.thresholds:
            metrics = compute_metrics(probabilities, ground_truth, threshold=th)
            all_results.append({"threshold": th, **metrics})

            # Check FPR constraint first
            if metrics["fpr"] <= max_allowed_fpr:
                # Primary objective: maximize F1 + IoU
                objective = metrics["f1"] * 0.7 + metrics["iou"] * 0.3
                if objective > best_score:
                    best_score = objective
                    best_thresh = th
                    best_metrics = metrics

        # Fallback if no threshold met FPR constraint
        if not best_metrics:
            best_thresh = min(all_results, key=lambda x: x["fpr"])["threshold"]
            best_metrics = [r for r in all_results if r["threshold"] == best_thresh][0]

        result = {
            "optimal_threshold": best_thresh,
            "metrics": best_metrics,
            "target_fpr_constraint": max_allowed_fpr,
            "sweep_results": all_results
        }
        return result

    def save_optimal_threshold(self, result: dict, output_path: Optional[str] = None):
        from project_code.config import MODELS_DIR
        p = Path(output_path) if output_path else (MODELS_DIR / "best_threshold.json")
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)
        print(f"Optimal threshold {result['optimal_threshold']} saved to {p}")
