from typing import Dict, Union
import numpy as np
import torch

def compute_metrics(
    preds: Union[np.ndarray, torch.Tensor],
    targets: Union[np.ndarray, torch.Tensor],
    threshold: float = 0.5,
    eps: float = 1e-7
) -> Dict[str, float]:
    """
    Compute full suite of binary change detection metrics:
    - Precision, Recall, F1, IoU, Dice, FPR (False Positive Rate), FNR (False Negative Rate), Accuracy
    """
    if isinstance(preds, torch.Tensor):
        if preds.ndim == 4 and preds.shape[1] == 1:
            preds = preds.squeeze(1)
        preds = torch.sigmoid(preds) if preds.min() < 0 or preds.max() > 1 else preds
        preds = (preds > threshold).cpu().numpy().astype(bool)
    else:
        preds = (preds > threshold).astype(bool)

    if isinstance(targets, torch.Tensor):
        if targets.ndim == 4 and targets.shape[1] == 1:
            targets = targets.squeeze(1)
        targets = (targets > 0).cpu().numpy().astype(bool)
    else:
        targets = (targets > 0).astype(bool)

    # Flatten
    p_flat = preds.reshape(-1)
    t_flat = targets.reshape(-1)

    tp = np.logical_and(p_flat, t_flat).sum()
    fp = np.logical_and(p_flat, ~t_flat).sum()
    fn = np.logical_and(~p_flat, t_flat).sum()
    tn = np.logical_and(~p_flat, ~t_flat).sum()

    precision = float(tp / (tp + fp + eps))
    recall = float(tp / (tp + fn + eps))
    f1 = float(2 * precision * recall / (precision + recall + eps))
    iou = float(tp / (tp + fp + fn + eps))
    dice = float(2 * tp / (2 * tp + fp + fn + eps))
    fpr = float(fp / (fp + tn + eps))
    fnr = float(fn / (fn + tp + eps))
    accuracy = float((tp + tn) / (tp + tn + fp + fn + eps))

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "iou": round(iou, 4),
        "dice": round(dice, 4),
        "fpr": round(fpr, 4),
        "fnr": round(fnr, 4),
        "accuracy": round(accuracy, 4),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn)
    }

def compute_metrics_from_counts(tp: int, fp: int, fn: int, tn: int, eps: float = 1e-7) -> Dict[str, float]:
    """Compute binary change metrics from pre-accumulated TP, FP, FN, TN counts."""
    precision = float(tp / (tp + fp + eps))
    recall = float(tp / (tp + fn + eps))
    f1 = float(2 * precision * recall / (precision + recall + eps))
    iou = float(tp / (tp + fp + fn + eps))
    dice = float(2 * tp / (2 * tp + fp + fn + eps))
    fpr = float(fp / (fp + tn + eps))
    fnr = float(fn / (fn + tp + eps))
    accuracy = float((tp + tn) / (tp + tn + fp + fn + eps))

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "iou": round(iou, 4),
        "dice": round(dice, 4),
        "fpr": round(fpr, 4),
        "fnr": round(fnr, 4),
        "accuracy": round(accuracy, 4),
        "tp": int(tp),
        "fp": int(fp),
        "fn": int(fn),
        "tn": int(tn)
    }

