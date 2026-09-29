import os
import json
import csv
import time
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import torch
from torch.utils.data import DataLoader
from ..evaluation.metrics import compute_metrics, compute_metrics_from_counts
from ..models.losses import ChangeDetectionLoss, MultiTaskChangeLoss

class ChangeDetectionTrainer:
    """
    Hardware-Optimized Trainer for NVIDIA RTX 3050 (4 GB VRAM) and Intel i5-12450H.
    Features:
    - Automatic GPU detection with CPU fallback
    - Mixed Precision / AMP (float16) to conserve VRAM
    - Gradient accumulation for stable mini-batch optimization
    - CosineAnnealingLR scheduling
    - Validation-based early stopping
    - Experiment logging: config.json, metrics.json, model.pt, training_history.csv
    """

    def __init__(
        self,
        model: torch.nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        experiment_dir: str,
        lr: float = 1e-4,
        weight_decay: float = 1e-4,
        epochs: int = 30,
        grad_accum_steps: int = 4,
        use_amp: bool = True,
        loss_fn: Optional[torch.nn.Module] = None,
        early_stopping_patience: int = 7
    ):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = model.to(self.device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.experiment_dir = Path(experiment_dir)
        self.experiment_dir.mkdir(parents=True, exist_ok=True)

        self.epochs = epochs
        self.grad_accum_steps = grad_accum_steps
        self.use_amp = use_amp and (self.device.type == "cuda")
        self.scaler = torch.amp.GradScaler("cuda", enabled=self.use_amp)
        self.patience = early_stopping_patience

        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=weight_decay)
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(self.optimizer, T_max=epochs, eta_min=1e-6)
        self.loss_fn = loss_fn or ChangeDetectionLoss()

        self.history_csv = self.experiment_dir / "training_history.csv"
        self._init_csv()

    def _init_csv(self):
        with open(self.history_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["epoch", "train_loss", "val_loss", "val_f1", "val_iou", "val_precision", "val_recall", "val_fpr", "lr", "epoch_time_sec"])

    def train_epoch(self, epoch: int) -> float:
        self.model.train()
        total_loss = 0.0
        self.optimizer.zero_grad()
        t_start = time.time()

        for step, batch in enumerate(self.train_loader):
            t1 = batch["image_t1"].to(self.device)
            t2 = batch["image_t2"].to(self.device)
            mask = batch["change_mask"].to(self.device)

            with torch.amp.autocast("cuda", enabled=self.use_amp):
                out = self.model(t1, t2)
                logits = out["change_logits"]
                loss = self.loss_fn(logits, mask)
                loss = loss / self.grad_accum_steps

            self.scaler.scale(loss).backward()

            if (step + 1) % self.grad_accum_steps == 0 or (step + 1) == len(self.train_loader):
                self.scaler.step(self.optimizer)
                self.scaler.update()
                self.optimizer.zero_grad()

            step_loss = loss.item() * self.grad_accum_steps
            total_loss += step_loss

            if (step + 1) % 250 == 0 or (step + 1) == len(self.train_loader):
                elapsed = time.time() - t_start
                rate = (step + 1) / max(elapsed, 1e-3)
                vram_mb = torch.cuda.memory_reserved() / 1e6 if self.device.type == "cuda" else 0.0
                print(f"  [Epoch {epoch}/{self.epochs}] Step {step+1}/{len(self.train_loader)} ({rate:.1f} it/s) | Loss: {step_loss:.4f} | VRAM: {vram_mb:.0f}MB", flush=True)

        return total_loss / max(len(self.train_loader), 1)

    @torch.no_grad()
    def evaluate(self) -> Dict[str, float]:
        self.model.eval()
        total_loss = 0.0
        running_tp = 0
        running_fp = 0
        running_fn = 0
        running_tn = 0

        for batch in self.val_loader:
            t1 = batch["image_t1"].to(self.device)
            t2 = batch["image_t2"].to(self.device)
            mask = batch["change_mask"].to(self.device)

            with torch.amp.autocast("cuda", enabled=self.use_amp):
                out = self.model(t1, t2)
                logits = out["change_logits"]
                loss = self.loss_fn(logits, mask)

            total_loss += loss.item()
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
        metrics["val_loss"] = round(total_loss / max(len(self.val_loader), 1), 4)
        return metrics

    def fit(self) -> Dict[str, Any]:
        best_f1 = -1.0
        best_metrics = {}
        epochs_no_improve = 0

        print(f"[Trainer] Starting training on {self.device.type.upper()} ({'AMP enabled' if self.use_amp else 'FP32'}).")
        print(f"[Trainer] Experiment Directory: {self.experiment_dir}")

        for epoch in range(1, self.epochs + 1):
            t0 = time.time()
            train_loss = self.train_epoch(epoch)
            val_metrics = self.evaluate()
            self.scheduler.step()
            epoch_time = time.time() - t0

            cur_lr = self.optimizer.param_groups[0]["lr"]

            # Log to CSV
            with open(self.history_csv, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    epoch, round(train_loss, 4), val_metrics["val_loss"],
                    val_metrics["f1"], val_metrics["iou"], val_metrics["precision"],
                    val_metrics["recall"], val_metrics["fpr"], round(cur_lr, 7), round(epoch_time, 1)
                ])

            print(f"Epoch {epoch}/{self.epochs} | Train Loss: {train_loss:.4f} | Val F1: {val_metrics['f1']:.4f} | IoU: {val_metrics['iou']:.4f} | FPR: {val_metrics['fpr']:.4f} ({epoch_time:.1f}s)")

            # Checkpoint best model
            if val_metrics["f1"] > best_f1:
                best_f1 = val_metrics["f1"]
                best_metrics = {**val_metrics, "best_epoch": epoch}
                torch.save(self.model.state_dict(), self.experiment_dir / "model.pt")
                epochs_no_improve = 0
            else:
                epochs_no_improve += 1
                if epochs_no_improve >= self.patience:
                    print(f"[Trainer] Early stopping triggered after {epoch} epochs.")
                    break

        # Save metrics.json
        with open(self.experiment_dir / "metrics.json", "w", encoding="utf-8") as f:
            json.dump(best_metrics, f, indent=4)

        return best_metrics
