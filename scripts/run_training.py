import os
import sys
import json
import random
import time
import numpy as np
import torch
from torch.utils.data import DataLoader, Subset

# sys.path.insert(0, r"f:\natraj26227")
sys.path.insert(0, r"g:\natraj26227")

from project_code.datasets.dataset_registry import get_dataset
from project_code.datasets.patch_extractor import LazyPatchDataset
from project_code.models.siamese_resnet18 import SiameseResNet18UNet
from project_code.training.trainer import ChangeDetectionTrainer

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

def main():
    set_seed(42)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"=== Running Live Training on {device} ({torch.cuda.get_device_name(0) if device.type=='cuda' else 'CPU'}) ===")

    # 1. Load LEVIR-CD dataset
    base_train = get_dataset("LEVIR-CD", split="train")
    base_val = get_dataset("LEVIR-CD", split="val")

    train_patches = LazyPatchDataset(base_train, patch_size=256, stride=512, mode="train")
    val_patches = LazyPatchDataset(base_val, patch_size=256, stride=512, mode="val")

    # Sample a focused subset (e.g., 300 train patches, 60 val patches) for fast, robust initial convergence
    train_subset = Subset(train_patches, range(min(300, len(train_patches))))
    val_subset = Subset(val_patches, range(min(60, len(val_patches))))

    print(f"Train subset: {len(train_subset)} patches | Val subset: {len(val_subset)} patches")

    train_loader = DataLoader(train_subset, batch_size=2, shuffle=True, pin_memory=(device.type == "cuda"))
    val_loader = DataLoader(val_subset, batch_size=2, shuffle=False, pin_memory=(device.type == "cuda"))

    # 2. Instantiate Siamese U-Net + ResNet-18 with CBAM Attention
    model = SiameseResNet18UNet(pretrained=True, attention_type="cbam")
    model.to(device)

    # exp_dir = r"f:\natraj26227\experiments\levir_baseline"
    exp_dir = r"g:\natraj26227\experiments\levir_baseline"
    os.makedirs(exp_dir, exist_ok=True)

    # 3. Train for 5 epochs with AMP
    trainer = ChangeDetectionTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        experiment_dir=exp_dir,
        lr=1e-4,
        epochs=5,
        grad_accum_steps=4,
        use_amp=True
    )

    metrics = trainer.fit()
    print("Training finished successfully! Checkpoint saved to:", os.path.join(exp_dir, "model.pt"))

    # Also copy best checkpoint to unified_5datasets_cbam directory so all API modules find it
    # unified_dir = r"f:\natraj26227\experiments\unified_5datasets_cbam"
    unified_dir = r"g:\natraj26227\experiments\unified_5datasets_cbam"
    os.makedirs(unified_dir, exist_ok=True)
    import shutil
    shutil.copy(os.path.join(exp_dir, "model.pt"), os.path.join(unified_dir, "model.pt"))
    print("Checkpoint copied to:", os.path.join(unified_dir, "model.pt"))

if __name__ == "__main__":
    main()
