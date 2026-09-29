import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict

class EfficientSelfAttention(nn.Module):
    """Memory-efficient spatial self-attention with reduction factor for 4GB VRAM."""
    def __init__(self, dim: int, num_heads: int = 4, sr_ratio: int = 2):
        super().__init__()
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.scale = self.head_dim ** -0.5

        self.q = nn.Linear(dim, dim, bias=False)
        self.kv = nn.Linear(dim, dim * 2, bias=False)
        self.proj = nn.Linear(dim, dim)

        self.sr_ratio = sr_ratio
        if sr_ratio > 1:
            self.sr = nn.Conv2d(dim, dim, kernel_size=sr_ratio, stride=sr_ratio)
            self.norm = nn.LayerNorm(dim)

    def forward(self, x: torch.Tensor, h: int, w: int) -> torch.Tensor:
        b, n, c = x.shape
        q = self.q(x).reshape(b, n, self.num_heads, self.head_dim).permute(0, 2, 1, 3)

        if self.sr_ratio > 1:
            x_ = x.permute(0, 2, 1).reshape(b, c, h, w)
            x_ = self.sr(x_).reshape(b, c, -1).permute(0, 2, 1)
            x_ = self.norm(x_)
            kv = self.kv(x_).reshape(b, -1, 2, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)
        else:
            kv = self.kv(x).reshape(b, -1, 2, self.num_heads, self.head_dim).permute(2, 0, 3, 1, 4)

        k, v = kv[0], kv[1]

        attn = (q @ k.transpose(-2, -1)) * self.scale
        attn = attn.softmax(dim=-1)

        out = (attn @ v).transpose(1, 2).reshape(b, n, c)
        return self.proj(out)


class TransformerBlock(nn.Module):
    def __init__(self, dim: int, num_heads: int = 4, sr_ratio: int = 2):
        super().__init__()
        self.norm1 = nn.LayerNorm(dim)
        self.attn = EfficientSelfAttention(dim, num_heads, sr_ratio)
        self.norm2 = nn.LayerNorm(dim)
        self.mlp = nn.Sequential(
            nn.Linear(dim, dim * 2),
            nn.GELU(),
            nn.Linear(dim * 2, dim)
        )

    def forward(self, x: torch.Tensor, h: int, w: int) -> torch.Tensor:
        x = x + self.attn(self.norm1(x), h, w)
        x = x + self.mlp(self.norm2(x))
        return x


class LightweightChangeFormer(nn.Module):
    """
    Lightweight ChangeFormer for RTX 3050 4GB VRAM Benchmarking.
    Uses patch embedding + lightweight multi-scale spatial-reduction transformer blocks + difference decoder.
    """
    def __init__(self, in_channels: int = 3, num_classes: int = 1):
        super().__init__()
        # Shared patch embedding
        self.patch_embed = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, stride=2, padding=1), # 128x128
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1), # 64x64
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True)
        )

        self.block1 = TransformerBlock(dim=64, num_heads=4, sr_ratio=4)
        self.downsample = nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1) # 32x32
        self.block2 = TransformerBlock(dim=128, num_heads=4, sr_ratio=2)

        # Difference Fusion
        self.fuse_64 = nn.Conv2d(64 * 3, 64, 1)
        self.fuse_128 = nn.Conv2d(128 * 3, 128, 1)

        # Decoder
        self.up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True)
        self.dec = nn.Sequential(
            nn.Conv2d(128 + 64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Upsample(scale_factor=4, mode="bilinear", align_corners=True),
            nn.Conv2d(64, 32, 3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, num_classes, 1)
        )

    def extract_feats(self, x: torch.Tensor):
        e1 = self.patch_embed(x) # (B, 64, 64, 64)
        b, c, h, w = e1.shape
        t1 = e1.flatten(2).permute(0, 2, 1)
        t1 = self.block1(t1, h, w).permute(0, 2, 1).reshape(b, c, h, w)

        e2 = self.downsample(t1) # (B, 128, 32, 32)
        b2, c2, h2, w2 = e2.shape
        t2 = e2.flatten(2).permute(0, 2, 1)
        t2 = self.block2(t2, h2, w2).permute(0, 2, 1).reshape(b2, c2, h2, w2)
        return t1, t2

    def forward(self, t1: torch.Tensor, t2: torch.Tensor) -> Dict[str, torch.Tensor]:
        f1_1, f1_2 = self.extract_feats(t1)
        f2_1, f2_2 = self.extract_feats(t2)

        diff1 = torch.abs(f1_1 - f2_1)
        diff2 = torch.abs(f1_2 - f2_2)

        fused1 = F.relu(self.fuse_64(torch.cat([f1_1, f2_1, diff1], dim=1)))
        fused2 = F.relu(self.fuse_128(torch.cat([f1_2, f2_2, diff2], dim=1)))

        u2 = self.up(fused2)
        if u2.shape[2:] != fused1.shape[2:]:
            u2 = F.interpolate(u2, size=fused1.shape[2:], mode="bilinear", align_corners=True)
        cat = torch.cat([u2, fused1], dim=1)
        logits = self.dec(cat)

        return {"change_logits": logits}
