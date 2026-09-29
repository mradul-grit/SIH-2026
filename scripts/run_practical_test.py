import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import torch
from torch.utils.data import DataLoader, Subset

# sys.path.insert(0, r"f:\natraj26227")
sys.path.insert(0, r"g:\natraj26227")

from project_code.datasets.dataset_registry import get_dataset
from project_code.datasets.patch_extractor import LazyPatchDataset
from project_code.models.siamese_resnet18 import SiameseResNet18UNet
from project_code.evaluation.metrics import compute_metrics_from_counts
from PIL import Image

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
def evaluate_dataset_at_threshold(model, dataloader, device, threshold: float = 0.40):
    model.eval()
    running_tp = 0
    running_fp = 0
    running_fn = 0
    running_tn = 0
    latencies = []

    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

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
        preds = (probs > threshold).astype(bool)

        p_flat = preds.reshape(-1)
        t_flat = targets.reshape(-1)

        running_tp += int(np.logical_and(p_flat, t_flat).sum())
        running_fp += int(np.logical_and(p_flat, ~t_flat).sum())
        running_fn += int(np.logical_and(~p_flat, t_flat).sum())
        running_tn += int(np.logical_and(~p_flat, ~t_flat).sum())

    metrics = compute_metrics_from_counts(running_tp, running_fp, running_fn, running_tn)
    metrics["avg_latency_ms"] = round(float(np.mean(latencies)), 2)
    metrics["fps"] = round(1000.0 / metrics["avg_latency_ms"], 1) if metrics["avg_latency_ms"] > 0 else 0
    if device.type == "cuda":
        metrics["peak_vram_mb"] = round(torch.cuda.max_memory_allocated(device) / (1024 * 1024), 2)
    else:
        metrics["peak_vram_mb"] = 0.0
    return metrics

def run_tiled_scene(model, device, p1, p2, pl, threshold=0.40):
    img1 = Image.open(p1).convert("RGB")
    img2 = Image.open(p2).convert("RGB")
    gt = (np.array(Image.open(pl).convert("L")) > 0).astype(bool)
    w, h = img1.size

    arr1 = np.array(img1).astype(np.float32) / 255.0
    arr2 = np.array(img2).astype(np.float32) / 255.0

    patch_size = 256
    stride = 224
    prob_map = np.zeros((h, w), dtype=np.float32)
    count_map = np.zeros((h, w), dtype=np.float32)

    y_coords = list(range(0, h - patch_size + 1, stride))
    if not y_coords or y_coords[-1] + patch_size < h:
        y_coords.append(h - patch_size)
    x_coords = list(range(0, w - patch_size + 1, stride))
    if not x_coords or x_coords[-1] + patch_size < w:
        x_coords.append(w - patch_size)

    t_start = time.perf_counter()
    batches_t1 = []
    batches_t2 = []
    coords = []
    for y in y_coords:
        for x in x_coords:
            batches_t1.append(arr1[y:y+patch_size, x:x+patch_size].transpose(2, 0, 1))
            batches_t2.append(arr2[y:y+patch_size, x:x+patch_size].transpose(2, 0, 1))
            coords.append((y, x))
            if len(batches_t1) == 2:
                b1_t = torch.from_numpy(np.stack(batches_t1)).float().to(device)
                b2_t = torch.from_numpy(np.stack(batches_t2)).float().to(device)
                with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
                    with torch.no_grad():
                        out = model(b1_t, b2_t)
                        b_probs = torch.sigmoid(out["change_logits"]).squeeze(1).cpu().numpy()
                for idx, (by, bx) in enumerate(coords):
                    prob_map[by:by+patch_size, bx:bx+patch_size] += b_probs[idx]
                    count_map[by:by+patch_size, bx:bx+patch_size] += 1.0
                batches_t1.clear()
                batches_t2.clear()
                coords.clear()

    if batches_t1:
        b1_t = torch.from_numpy(np.stack(batches_t1)).float().to(device)
        b2_t = torch.from_numpy(np.stack(batches_t2)).float().to(device)
        with torch.amp.autocast("cuda", enabled=(device.type == "cuda")):
            with torch.no_grad():
                out = model(b1_t, b2_t)
                b_probs = torch.sigmoid(out["change_logits"]).squeeze(1).cpu().numpy()
        for idx, (by, bx) in enumerate(coords):
            prob_map[by:by+patch_size, bx:bx+patch_size] += b_probs[idx]
            count_map[by:by+patch_size, bx:bx+patch_size] += 1.0

    count_map[count_map == 0] = 1.0
    avg_probs = prob_map / count_map
    pred = avg_probs > threshold
    if device.type == "cuda":
        torch.cuda.synchronize()
    latency_ms = (time.perf_counter() - t_start) * 1000.0

    p_flat = pred.reshape(-1)
    t_flat = gt.reshape(-1)
    tp = int(np.logical_and(p_flat, t_flat).sum())
    fp = int(np.logical_and(p_flat, ~t_flat).sum())
    fn = int(np.logical_and(~p_flat, t_flat).sum())
    tn = int(np.logical_and(~p_flat, ~t_flat).sum())

    m = compute_metrics_from_counts(tp, fp, fn, tn)
    m["latency_ms"] = round(latency_ms, 2)
    m["resolution"] = f"{w}x{h}"
    m["gt_change_pixels"] = int(t_flat.sum())
    m["pred_change_pixels"] = int(p_flat.sum())
    return m

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("=" * 70)
    print("      SIH-227 PRACTICAL MODEL ACCURACY & HARDWARE BENCHMARK")
    print("=" * 70)
    print(f"Device: {device}")
    if device.type == "cuda":
        print(f"GPU Name: {torch.cuda.get_device_name(0)}")
        print(f"Total VRAM: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.2f} GB")
        print(f"CUDA Version: {torch.version.cuda}")
    print(f"Torch Version: {torch.__version__}")

    # ckpt_path = r"f:\natraj26227\experiments\unified_5datasets_cbam\model.pt"
    ckpt_path = r"g:\natraj26227\experiments\unified_5datasets_cbam\model.pt"
    if not os.path.exists(ckpt_path):
        print(f"Error: checkpoint {ckpt_path} not found!")
        return

    print(f"\nLoading weights from: {ckpt_path}")
    model = SiameseResNet18UNet(pretrained=False, attention_type="cbam", num_semantic_classes=0)
    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    model.to(device)
    model.eval()

    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    model_size_mb = os.path.getsize(ckpt_path) / (1024 * 1024)
    print(f"Total Parameters: {total_params:,} ({total_params/1e6:.2f}M)")
    print(f"Trainable Parameters: {trainable_params:,}")
    print(f"Model File Size: {model_size_mb:.2f} MB")

    # Load 100 samples from each test dataset
    print("\n--- Loading Real Held-Out Test Splits ---")
    datasets_to_test = [
        ("LEVIR-CD", "test", 512, 100),
        ("LEVIR-CD+", "test", 512, 100),
        ("WHU-CD", "test", 256, 100),
        ("S2Looking", "test", 512, 100),
        ("SYSU-CD", "test", 256, 100)
    ]

    loaders = {}
    for name, split, stride, n_samples in datasets_to_test:
        try:
            base_ds = get_dataset(name, split=split)
            patch_ds = LazyPatchDataset(base_ds, patch_size=256, stride=stride, mode="test")
            total_avail = len(patch_ds)
            step = max(1, total_avail // n_samples)
            indices = list(range(0, total_avail, step))[:n_samples]
            subset = Subset(patch_ds, indices)
            loader = DataLoader(subset, batch_size=4, shuffle=False, collate_fn=custom_collate)
            loaders[name] = (loader, len(subset), total_avail)
            print(f"  [OK] {name} ({split}): Loaded {len(subset)} real test patches (sampled from {total_avail} total)")
        except Exception as e:
            print(f"  [ERR] Failed to load {name}: {e}")

    # 1. Test across datasets at optimal threshold 0.40
    print("\n" + "=" * 70)
    print("1. TEST ACCURACY & METRICS BY DATASET (Threshold = 0.40)")
    print("=" * 70)

    dataset_results = {}
    all_tp = 0
    all_fp = 0
    all_fn = 0
    all_tn = 0
    all_latencies = []

    print(f"{'Dataset':<14} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<8} | {'F1-Score':<8} | {'IoU':<8} | {'FPR':<7} | {'Latency':<9} | {'VRAM'}")
    print("-" * 95)

    for name, (loader, n_sub, n_tot) in loaders.items():
        res = evaluate_dataset_at_threshold(model, loader, device, threshold=0.40)
        dataset_results[name] = res
        all_tp += res["tp"]
        all_fp += res["fp"]
        all_fn += res["fn"]
        all_tn += res["tn"]
        all_latencies.append(res["avg_latency_ms"])

        print(f"{name:<14} | {res['accuracy']*100:>6.2f}%  | {res['precision']*100:>7.2f}%  | {res['recall']*100:>6.2f}% | {res['f1']:>8.4f} | {res['iou']:>8.4f} | {res['fpr']*100:>5.2f}% | {res['avg_latency_ms']:>6.1f} ms | {res['peak_vram_mb']:>5.0f} MB")

    overall_metrics = compute_metrics_from_counts(all_tp, all_fp, all_fn, all_tn)
    overall_metrics["avg_latency_ms"] = round(float(np.mean(all_latencies)), 2)
    overall_metrics["fps"] = round(1000.0 / overall_metrics["avg_latency_ms"], 1)
    if device.type == "cuda":
        overall_metrics["peak_vram_mb"] = round(torch.cuda.max_memory_allocated(device) / (1024 * 1024), 2)

    print("-" * 95)
    print(f"{'OVERALL':<14} | {overall_metrics['accuracy']*100:>6.2f}%  | {overall_metrics['precision']*100:>7.2f}%  | {overall_metrics['recall']*100:>6.2f}% | {overall_metrics['f1']:>8.4f} | {overall_metrics['iou']:>8.4f} | {overall_metrics['fpr']*100:>5.2f}% | {overall_metrics['avg_latency_ms']:>6.1f} ms | {overall_metrics['peak_vram_mb']:>5.0f} MB")

    # 2. Threshold Sensitivity Analysis
    print("\n" + "=" * 70)
    print("2. THRESHOLD SENSITIVITY SWEEP (Across All Test Datasets)")
    print("=" * 70)
    print(f"{'Threshold':<10} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<8} | {'F1-Score':<8} | {'IoU':<8} | {'FPR (False Alarm)':<18} | {'FNR (Miss Rate)'}")
    print("-" * 95)

    threshold_sweep = []
    # Test on LEVIR-CD test set across thresholds
    levir_loader = loaders["LEVIR-CD"][0]
    for th in [0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60]:
        th_res = evaluate_dataset_at_threshold(model, levir_loader, device, threshold=th)
        threshold_sweep.append({"threshold": th, **th_res})
        print(f"{th:<10.2f} | {th_res['accuracy']*100:>6.2f}%  | {th_res['precision']*100:>7.2f}%  | {th_res['recall']*100:>6.2f}% | {th_res['f1']:>8.4f} | {th_res['iou']:>8.4f} | {th_res['fpr']*100:>14.2f}%    | {th_res['fnr']*100:>12.2f}%")

    # 3. Native Full-Scene (1024x1024) Tiled Benchmark
    print("\n" + "=" * 70)
    print("3. FULL 1024x1024 SCENE NATIVE TILED BENCHMARK (Real Whole Images)")
    print("=" * 70)
    full_scenes = [
        # ("LEVIR-CD test_10.png (Suburban)", "f:/natraj26227/datasets/LEVIR CD/test/A/test_10.png", "f:/natraj26227/datasets/LEVIR CD/test/B/test_10.png", "f:/natraj26227/datasets/LEVIR CD/test/label/test_10.png"),
        # ("LEVIR-CD test_100.png (Industrial)", "f:/natraj26227/datasets/LEVIR CD/test/A/test_100.png", "f:/natraj26227/datasets/LEVIR CD/test/B/test_100.png", "f:/natraj26227/datasets/LEVIR CD/test/label/test_100.png"),
        # ("LEVIR-CD test_14.png (Dense Housing)", "f:/natraj26227/datasets/LEVIR CD/test/A/test_14.png", "f:/natraj26227/datasets/LEVIR CD/test/B/test_14.png", "f:/natraj26227/datasets/LEVIR CD/test/label/test_14.png"),
        # ("LEVIR-CD test_1.png (No-Change Control)", "f:/natraj26227/datasets/LEVIR CD/test/A/test_1.png", "f:/natraj26227/datasets/LEVIR CD/test/B/test_1.png", "f:/natraj26227/datasets/LEVIR CD/test/label/test_1.png"),
        ("LEVIR-CD test_10.png (Suburban)", "g:/natraj26227/datasets/LEVIR CD/test/A/test_10.png", "g:/natraj26227/datasets/LEVIR CD/test/B/test_10.png", "g:/natraj26227/datasets/LEVIR CD/test/label/test_10.png"),
        ("LEVIR-CD test_100.png (Industrial)", "g:/natraj26227/datasets/LEVIR CD/test/A/test_100.png", "g:/natraj26227/datasets/LEVIR CD/test/B/test_100.png", "g:/natraj26227/datasets/LEVIR CD/test/label/test_100.png"),
        ("LEVIR-CD test_14.png (Dense Housing)", "g:/natraj26227/datasets/LEVIR CD/test/A/test_14.png", "g:/natraj26227/datasets/LEVIR CD/test/B/test_14.png", "g:/natraj26227/datasets/LEVIR CD/test/label/test_14.png"),
        ("LEVIR-CD test_1.png (No-Change Control)", "g:/natraj26227/datasets/LEVIR CD/test/A/test_1.png", "g:/natraj26227/datasets/LEVIR CD/test/B/test_1.png", "g:/natraj26227/datasets/LEVIR CD/test/label/test_1.png"),
    ]

    scene_results = []
    print(f"{'Scene Name':<38} | {'Resolution':<9} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<8} | {'F1-Score':<8} | {'IoU':<8} | {'Latency'}")
    print("-" * 115)
    for title, p1, p2, pl in full_scenes:
        if os.path.exists(p1) and os.path.exists(p2) and os.path.exists(pl):
            sm = run_tiled_scene(model, device, p1, p2, pl, threshold=0.40)
            sm["scene_title"] = title
            scene_results.append(sm)
            print(f"{title:<38} | {sm['resolution']:<9} | {sm['accuracy']*100:>6.2f}%  | {sm['precision']*100:>7.2f}%  | {sm['recall']*100:>6.2f}% | {sm['f1']:>8.4f} | {sm['iou']:>8.4f} | {sm['latency_ms']:>6.1f} ms")

    # Save complete empirical audit report
    # out_file = r"f:\natraj26227\experiments\practical_test_results.json"
    out_file = r"g:\natraj26227\experiments\practical_test_results.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    report = {
        "timestamp": time.time(),
        "hardware": {
            "device": str(device),
            "gpu_name": torch.cuda.get_device_name(0) if device.type == "cuda" else "CPU",
            "total_vram_gb": round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2) if device.type == "cuda" else 0,
            "peak_vram_mb": overall_metrics["peak_vram_mb"],
            "torch_version": torch.__version__,
            "cuda_version": torch.version.cuda if device.type == "cuda" else None
        },
        "model_specs": {
            "weights_path": ckpt_path,
            "total_parameters": total_params,
            "trainable_parameters": trainable_params,
            "model_size_mb": round(model_size_mb, 2),
            "architecture": "SiameseResNet18UNet + CBAM Dual Attention"
        },
        "overall_patch_benchmark": overall_metrics,
        "per_dataset_benchmark": dataset_results,
        "threshold_sweep_levir": threshold_sweep,
        "full_scene_tiled_benchmark": scene_results
    }
    with open(out_file, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\n[OK] Full practical benchmark saved to: {out_file}")

if __name__ == "__main__":
    main()
