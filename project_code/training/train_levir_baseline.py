import os
import sys
import json
import random
import numpy as np
import torch
from torch.utils.data import DataLoader

# Project root
# sys.path.insert(0, r"f:\natraj26227")
sys.path.insert(0, r"g:\natraj26227")

from project_code.datasets.dataset_registry import get_dataset
from project_code.datasets.patch_extractor import LazyPatchDataset
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
    print("=== SIH-227 Phase 8: LEVIR-CD Baseline Training ===")

    # 1. Load LEVIR-CD official splits
    base_train = get_dataset("LEVIR-CD", split="train")
    base_val = get_dataset("LEVIR-CD", split="val")

    # 2. Wrap with 256x256 lazy patch extractor
    # Use subset for fast verification if needed
    train_patches = LazyPatchDataset(base_train, patch_size=256, stride=256, mode="train")
    val_patches = LazyPatchDataset(base_val, patch_size=256, stride=256, mode="val")

    print(f"Train scenes: {len(base_train)}, Patches: {len(train_patches)}")
    print(f"Val scenes: {len(base_val)}, Patches: {len(val_patches)}")

    train_loader = DataLoader(train_patches, batch_size=2, shuffle=True, num_workers=0, pin_memory=torch.cuda.is_available())
    val_loader = DataLoader(val_patches, batch_size=2, shuffle=False, num_workers=0, pin_memory=torch.cuda.is_available())

    # 3. Instantiate Primary Model: Siamese U-Net + ResNet-18
    model = SiameseResNet18UNet(pretrained=True, attention_type=None)

    # exp_dir = r"f:\natraj26227\experiments\levir_baseline"
    exp_dir = r"g:\natraj26227\experiments\levir_baseline"
    config = {
        "model": "Siamese U-Net + ResNet-18",
        "dataset": "LEVIR-CD",
        "patch_size": 256,
        "batch_size": 2,
        "grad_accum_steps": 4,
        "lr": 1e-4,
        "weight_decay": 1e-4,
        "epochs": 15,
        "amp": True,
        "hardware": "RTX 3050 4GB"
    }
    os.makedirs(exp_dir, exist_ok=True)
    with open(os.path.join(exp_dir, "config.json"), "w") as f:
        json.dump(config, f, indent=4)

    # 4. Train
    trainer = ChangeDetectionTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        experiment_dir=exp_dir,
        lr=1e-4,
        epochs=15,
        grad_accum_steps=4,
        use_amp=True
    )

    best_metrics = trainer.fit()
    print("Baseline Training Completed. Best Metrics:", best_metrics)

if __name__ == "__main__":
    main()
