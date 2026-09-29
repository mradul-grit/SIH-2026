import os
import sys
import json
import random
import numpy as np
import torch
from torch.utils.data import DataLoader

# sys.path.insert(0, r"f:\natraj26227")
sys.path.insert(0, r"g:\natraj26227")

from project_code.datasets.unified_change_dataset import UnifiedChangeDataset
from project_code.models.siamese_resnet18 import SiameseResNet18UNet
from project_code.training.trainer import ChangeDetectionTrainer

def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def main():
    set_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"=== SIH-227 Phase 10: Unified 5-Dataset Multi-Task Training on {device} ===")

    print("Indexing all 5 datasets for training (24.82 GB)...")
    train_ds = UnifiedChangeDataset(
        dataset_names=["LEVIR-CD", "LEVIR-CD+", "WHU-CD", "S2Looking", "SYSU-CD"],
        split="train",
        patch_size=256,
        stride=256,
        balanced_sampling=True
    )
    print(f"Total training patches available across all 5 datasets: {len(train_ds):,}")

    print("Indexing validation datasets...")
    val_ds = UnifiedChangeDataset(
        dataset_names=["LEVIR-CD", "LEVIR-CD+", "WHU-CD", "S2Looking", "SYSU-CD"],
        split="val",
        patch_size=256,
        stride=512,
        balanced_sampling=False
    )
    print(f"Total validation patches available: {len(val_ds):,}")

    # Use a diverse, high-speed validation subset of 1,000 patches for quick evaluation between epochs
    from torch.utils.data import Subset
    val_indices = list(range(0, len(val_ds), max(1, len(val_ds) // 1000)))[:1000]
    val_subset = Subset(val_ds, val_indices)
    print(f"Validation subset for epoch evaluation: {len(val_subset)} patches.")

    def unified_collate_fn(batch):
        t1_list = [torch.from_numpy(b["image_t1"]) if isinstance(b["image_t1"], np.ndarray) else b["image_t1"] for b in batch]
        t2_list = [torch.from_numpy(b["image_t2"]) if isinstance(b["image_t2"], np.ndarray) else b["image_t2"] for b in batch]
        mask_list = [torch.from_numpy(b["change_mask"]) if isinstance(b["change_mask"], np.ndarray) else b["change_mask"] for b in batch]

        collated = {
            "image_t1": torch.stack(t1_list, dim=0),
            "image_t2": torch.stack(t2_list, dim=0),
            "change_mask": torch.stack(mask_list, dim=0),
            "metadata": [b.get("metadata", {}) for b in batch]
        }
        if all("semantic_mask" in b and b["semantic_mask"] is not None for b in batch):
            sem_list = [torch.from_numpy(b["semantic_mask"]) if isinstance(b["semantic_mask"], np.ndarray) else b["semantic_mask"] for b in batch]
            collated["semantic_mask"] = torch.stack(sem_list, dim=0)

        return collated

    train_loader = DataLoader(
        train_ds,
        batch_size=2,
        shuffle=True,
        num_workers=0,
        collate_fn=unified_collate_fn,
        pin_memory=(device.type == "cuda")
    )
    val_loader = DataLoader(
        val_subset,
        batch_size=2,
        shuffle=False,
        num_workers=0,
        collate_fn=unified_collate_fn,
        pin_memory=(device.type == "cuda")
    )

    # Model with CBAM Attention
    model = SiameseResNet18UNet(pretrained=True, attention_type="cbam", num_semantic_classes=0)

    # Warm-start from existing baseline checkpoint if available
    # warm_checkpoint = r"f:\natraj26227\experiments\levir_baseline\model.pt"
    warm_checkpoint = r"g:\natraj26227\experiments\levir_baseline\model.pt"
    if os.path.exists(warm_checkpoint):
        print(f"[Warm-Start] Loading baseline weights from: {warm_checkpoint}")
        try:
            model.load_state_dict(torch.load(warm_checkpoint, map_location="cpu"))
            print("[Warm-Start] Successfully loaded baseline weights.")
        except Exception as e:
            print(f"[Warm-Start] Notice: Could not load baseline weights ({e}), using ImageNet weights.")

    model.to(device)

    # exp_dir = r"f:\natraj26227\experiments\unified_5datasets_cbam"
    exp_dir = r"g:\natraj26227\experiments\unified_5datasets_cbam"
    config = {
        "model": "Siamese U-Net + ResNet-18 + CBAM Attention",
        "datasets": ["LEVIR-CD", "LEVIR-CD+", "WHU-CD", "S2Looking", "SYSU-CD"],
        "total_data_gb": 24.82,
        "patch_size": 256,
        "batch_size": 2,
        "grad_accum_steps": 4,
        "lr": 1e-4,
        "epochs": 10,
        "amp": True,
        "sampling": "Balanced Multi-Dataset",
        "hardware": "NVIDIA GeForce RTX 3050 Laptop GPU (4 GB VRAM)"
    }
    os.makedirs(exp_dir, exist_ok=True)
    with open(os.path.join(exp_dir, "config.json"), "w") as f:
        json.dump(config, f, indent=4)

    trainer = ChangeDetectionTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        experiment_dir=exp_dir,
        lr=1e-4,
        epochs=10,
        grad_accum_steps=4,
        early_stopping_patience=3,
        use_amp=True
    )

    best_metrics = trainer.fit()
    print("Unified Training Completed. Best Metrics:", best_metrics)

if __name__ == "__main__":
    main()

