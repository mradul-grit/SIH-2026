import torch
import torch.nn as nn
import torch.nn.functional as F

class DiceLoss(nn.Module):
    """
    Soft Dice Loss for Binary Change Detection.
    Smooths boundary gradients and handles severe foreground/background imbalance.
    """
    def __init__(self, smooth: float = 1.0):
        super().__init__()
        self.smooth = smooth

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        probs = torch.sigmoid(logits)
        probs_flat = probs.view(-1)
        targets_flat = targets.view(-1)

        intersection = (probs_flat * targets_flat).sum()
        dice = (2.0 * intersection + self.smooth) / (probs_flat.sum() + targets_flat.sum() + self.smooth)
        return 1.0 - dice


class FocalLoss(nn.Module):
    """
    Focal Loss for addressing class imbalance.
    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
    """
    def __init__(self, alpha: float = 0.25, gamma: float = 2.0, reduction: str = "mean"):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
        p = torch.sigmoid(logits)
        p_t = p * targets + (1 - p) * (1 - targets)
        alpha_t = self.alpha * targets + (1 - self.alpha) * (1 - targets)
        focal_loss = alpha_t * ((1 - p_t) ** self.gamma) * bce

        if self.reduction == "mean":
            return focal_loss.mean()
        elif self.reduction == "sum":
            return focal_loss.sum()
        return focal_loss


class ChangeDetectionLoss(nn.Module):
    """
    Composite Change Detection Loss:
      0.5 * BCEWithLogitsLoss + 0.5 * DiceLoss
    Optional Focal Loss switch for severe imbalance.
    """
    def __init__(self, use_focal: bool = False, pos_weight: float = 1.0):
        super().__init__()
        self.use_focal = use_focal
        self.bce = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight])) if pos_weight != 1.0 else nn.BCEWithLogitsLoss()
        self.dice = DiceLoss()
        self.focal = FocalLoss() if use_focal else None

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        targets = targets.float()
        if logits.shape != targets.shape:
            # Handle possible (B, 1, H, W) vs (B, H, W)
            if logits.ndim == 4 and targets.ndim == 3:
                targets = targets.unsqueeze(1)
            elif logits.ndim == 4 and logits.shape[1] == 1 and targets.ndim == 4:
                pass

        if self.use_focal:
            l_bce = self.focal(logits, targets)
        else:
            l_bce = self.bce(logits, targets)
        l_dice = self.dice(logits, targets)

        return 0.5 * l_bce + 0.5 * l_dice


class MultiTaskChangeLoss(nn.Module):
    """
    Multi-Task Loss for Joint Binary Change Detection & Semantic Change Type Classification:
      Total Loss = Change Loss + 0.25 * Classification Loss
    """
    def __init__(self, cls_weight: float = 0.25, num_classes: int = 3):
        super().__init__()
        self.cls_weight = cls_weight
        self.change_loss = ChangeDetectionLoss()
        self.ce_loss = nn.CrossEntropyLoss(ignore_index=-1)

    def forward(
        self,
        change_logits: torch.Tensor,
        change_targets: torch.Tensor,
        cls_logits: torch.Tensor = None,
        cls_targets: torch.Tensor = None
    ) -> torch.Tensor:
        l_change = self.change_loss(change_logits, change_targets)
        if cls_logits is not None and cls_targets is not None:
            l_cls = self.ce_loss(cls_logits, cls_targets)
            return l_change + self.cls_weight * l_cls
        return l_change
