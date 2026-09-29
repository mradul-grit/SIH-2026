import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import torch
from torch.utils.data import DataLoader, Subset

sys.path.insert(0, r"f:\natraj26227")

from project_code.datasets.dataset_registry import get_dataset
from project_code.datasets.patch_extractor import LazyPatchDataset
from project_code.models.siamese_resnet18 import SiameseResNet18UNet
from project_code.evaluation.metrics import compute_metrics_from_counts

def load_test_subsets(num_samples_per_dataset: int = 40):
    """Load balanced test subsets across all 5 benchmark datasets."""
    datasets = {}
    specs = [
        ("LEVIR-CD", "test", 512),
        ("LEVIR-CD+", "test", 512),
        ("WHU-CD", "test", 512),
        ("S2Looking", "test", 512),
        ("SYSU-CD", "test", 256)
    ]
    for name, split, stride in specs:
        try:
            base_ds = get_dataset(name, split=split)
            patch_ds = LazyPatchDataset(base_ds, patch_size=256, stride=stride, mode="test")
            n = len(patch_ds)
            step = max(1, n // num_samples_per_dataset)
            indices = list(range(0, n, step))[:num_samples_per_dataset]
            subset = Subset(patch_ds, indices)
            datasets[name] = subset
            print(f"Loaded test set for {name}: {len(subset)} patches (sampled from {n}).")
        except Exception as e:
            print(f"Warning loading {name}: {e}")
    return datasets

def custom_collate(batch):
    t1_list = [torch.from_numpy(b["image_t1"]) if isinstance(b["image_t1"], np.ndarray) else b["image_t1"] for b in batch]
    t2_list = [torch.from_numpy(b["image_t2"]) if isinstance(b["image_t2"], np.ndarray) else b["image_t2"] for b in batch]
    mask_list = [torch.from_numpy(b["change_mask"]) if isinstance(b["change_mask"], np.ndarray) else b["change_mask"] for b in batch]
    return {
        "image_t1": torch.stack(t1_list, dim=0),
        "image_t2": torch.stack(t2_list, dim=0),
        "change_mask": torch.stack(mask_list, dim=0),
    }

@torch.no_grad()
def evaluate_model(model, dataloader, device):
    model.eval()
    running_tp = 0
    running_fp = 0
    running_fn = 0
    running_tn = 0
    latencies = []

    for batch in dataloader:
        t1 = batch["image_t1"].to(device)
        t2 = batch["image_t2"].to(device)
        mask = batch["change_mask"].to(device)

        if device.type == "cuda":
            torch.cuda.synchronize()
        t_start = time.perf_counter()

        with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
            out = model(t1, t2)
            logits = out["change_logits"]

        if device.type == "cuda":
            torch.cuda.synchronize()
        latencies.append((time.perf_counter() - t_start) * 1000 / t1.size(0))

        probs = torch.sigmoid(logits).squeeze(1).cpu().numpy()
        targets = (mask.cpu().numpy() > 0.5).astype(bool)
        preds = (probs > 0.5).astype(bool)

        p_flat = preds.reshape(-1)
        t_flat = targets.reshape(-1)

        running_tp += int(np.logical_and(p_flat, t_flat).sum())
        running_fp += int(np.logical_and(p_flat, ~t_flat).sum())
        running_fn += int(np.logical_and(~p_flat, t_flat).sum())
        running_tn += int(np.logical_and(~p_flat, ~t_flat).sum())

    metrics = compute_metrics_from_counts(running_tp, running_fp, running_fn, running_tn)
    metrics["avg_latency_ms"] = round(float(np.mean(latencies)), 2)
    return metrics

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"=== Running Quantitative Model Benchmark on {device} ===")
    print("Device Name:", torch.cuda.get_device_name(0) if device.type == "cuda" else "CPU")

    # 1. Load test sets
    test_subsets = load_test_subsets(num_samples_per_dataset=40)

    # 2. Paths
    baseline_pt = r"f:\natraj26227\experiments\levir_baseline\model.pt"
    unified_pt = r"f:\natraj26227\experiments\unified_5datasets_cbam\model.pt"

    models_to_test = [
        ("LEVIR-CD Baseline Model", baseline_pt),
        ("Unified 5-Dataset Model (24.82 GB)", unified_pt)
    ]

    all_results = {}

    for model_name, ckpt_path in models_to_test:
        print(f"\nEvaluating: {model_name}...")
        model = SiameseResNet18UNet(pretrained=False, attention_type="cbam", num_semantic_classes=0)
        state_dict = torch.load(ckpt_path, map_location=device)
        model.load_state_dict(state_dict)
        model.to(device)

        model_results = {"per_dataset": {}}
        overall_tp, overall_fp, overall_fn, overall_tn = 0, 0, 0, 0
        overall_latencies = []

        for ds_name, subset in test_subsets.items():
            loader = DataLoader(subset, batch_size=2, shuffle=False, collate_fn=custom_collate)
            m = evaluate_model(model, loader, device)
            model_results["per_dataset"][ds_name] = m
            overall_tp += m["tp"]
            overall_fp += m["fp"]
            overall_fn += m["fn"]
            overall_tn += m["tn"]
            overall_latencies.append(m["avg_latency_ms"])
            print(f"  {ds_name:12s} -> F1: {m['f1']:.4f} | IoU: {m['iou']:.4f} | FPR: {m['fpr']:.4f} | Latency: {m['avg_latency_ms']}ms")

        overall_metrics = compute_metrics_from_counts(overall_tp, overall_fp, overall_fn, overall_tn)
        overall_metrics["avg_latency_ms"] = round(float(np.mean(overall_latencies)), 2)
        model_results["overall"] = overall_metrics
        all_results[model_name] = model_results
        print(f"  OVERALL AGGREGATE -> F1: {overall_metrics['f1']:.4f} | IoU: {overall_metrics['iou']:.4f} | FPR: {overall_metrics['fpr']:.4f}")

    # Save benchmark JSON
    out_json = r"f:\natraj26227\experiments\model_comparison_benchmark.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
    print("\nBenchmark saved to:", out_json)

    # Print summary table
    print("\n" + "="*85)
    print(f"{'Dataset / Metric':28s} | {'LEVIR-CD Baseline':24s} | {'Unified 5-Dataset (24.82 GB)':24s}")
    print("="*85)

    datasets_list = list(test_subsets.keys())
    for ds in datasets_list:
        base_f1 = all_results["LEVIR-CD Baseline Model"]["per_dataset"][ds]["f1"]
        uni_f1 = all_results["Unified 5-Dataset Model (24.82 GB)"]["per_dataset"][ds]["f1"]
        base_fpr = all_results["LEVIR-CD Baseline Model"]["per_dataset"][ds]["fpr"]
        uni_fpr = all_results["Unified 5-Dataset Model (24.82 GB)"]["per_dataset"][ds]["fpr"]
        print(f"{ds:28s} | F1: {base_f1:.4f} (FPR: {base_fpr:.4f})  | F1: {uni_f1:.4f} (FPR: {uni_fpr:.4f})")

    print("-" * 85)
    b_all = all_results["LEVIR-CD Baseline Model"]["overall"]
    u_all = all_results["Unified 5-Dataset Model (24.82 GB)"]["overall"]
    print(f"{'OVERALL ALL-DATASET F1':28s} | {b_all['f1']:.4f}                   | {u_all['f1']:.4f}")
    print(f"{'OVERALL ALL-DATASET IoU':28s} | {b_all['iou']:.4f}                   | {u_all['iou']:.4f}")
    print(f"{'OVERALL FALSE ALARM RATE':28s} | {b_all['fpr']:.4f}                   | {u_all['fpr']:.4f}")
    print(f"{'AVERAGE GPU LATENCY (ms)':28s} | {b_all['avg_latency_ms']:.1f}ms                 | {u_all['avg_latency_ms']:.1f}ms")
    print("="*85)

if __name__ == "__main__":
    main()
