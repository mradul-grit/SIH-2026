import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict
from torchvision.models import resnet18, ResNet18_Weights
from .attention_modules import CBAM, SEBlock

class DecoderBlock(nn.Module):
    """U-Net Style Decoder Block with Skip-Connection Fusion & Optional Attention."""
    def __init__(
        self,
        in_channels: int,
        skip_channels: int,
        out_channels: int,
        use_attention: Optional[str] = None
    ):
        super().__init__()
        self.upsample = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True)
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels + skip_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )
        if use_attention == "cbam":
            self.attention = CBAM(out_channels)
        elif use_attention == "se":
            self.attention = SEBlock(out_channels)
        else:
            self.attention = nn.Identity()

    def forward(self, x: torch.Tensor, skip: torch.Tensor) -> torch.Tensor:
        x_up = self.upsample(x)
        # Handle small rounding discrepancies
        if x_up.shape[2:] != skip.shape[2:]:
            x_up = F.interpolate(x_up, size=skip.shape[2:], mode="bilinear", align_corners=True)
        cat = torch.cat([x_up, skip], dim=1)
        out = self.conv(cat)
        out = self.attention(out)
        return out


class SiameseResNet18UNet(nn.Module):
    """
    Primary Model: Siamese U-Net with ResNet-18 Backbone.
    
    Key Properties:
    - Shared weights for T1 and T2 encoder branches.
    - Difference Feature Fusion: Concat(F1, F2, |F1 - F2|) at multiple scales.
    - U-Net style multi-scale skip connections.
    - Modular Attention: None, 'se', or 'cbam'.
    - Optional Multi-Task Change Classification Head.
    - VRAM friendly for RTX 3050 4GB.
    """

    def __init__(
        self,
        pretrained: bool = True,
        attention_type: Optional[str] = None, # None, 'se', or 'cbam'
        num_classes: int = 1, # 1 for binary change mask logits
        num_semantic_classes: int = 0 # >0 enables secondary change-type head (e.g. 3 for S2Looking)
    ):
        super().__init__()
        self.attention_type = attention_type
        self.num_semantic_classes = num_semantic_classes

        # Shared ResNet-18 Backbone
        weights = ResNet18_Weights.DEFAULT if pretrained else None
        backbone = resnet18(weights=weights)

        self.initial = nn.Sequential(
            backbone.conv1,
            backbone.bn1,
            backbone.relu
        ) # 64 ch, stride 2 (128x128)
        self.maxpool = backbone.maxpool # 64 ch, stride 4 (64x64)

        self.layer1 = backbone.layer1 # 64 ch, stride 4 (64x64)
        self.layer2 = backbone.layer2 # 128 ch, stride 8 (32x32)
        self.layer3 = backbone.layer3 # 256 ch, stride 16 (16x16)
        self.layer4 = backbone.layer4 # 512 ch, stride 32 (8x8)

        # Multi-scale difference feature projectors: 3 * C -> C
        self.fuse_init = nn.Conv2d(64 * 3, 64, kernel_size=1, bias=False)
        self.fuse1 = nn.Conv2d(64 * 3, 64, kernel_size=1, bias=False)
        self.fuse2 = nn.Conv2d(128 * 3, 128, kernel_size=1, bias=False)
        self.fuse3 = nn.Conv2d(256 * 3, 256, kernel_size=1, bias=False)
        self.fuse4 = nn.Conv2d(512 * 3, 512, kernel_size=1, bias=False)

        # Bottleneck Attention
        if attention_type == "cbam":
            self.bottleneck_att = CBAM(512)
        elif attention_type == "se":
            self.bottleneck_att = SEBlock(512)
        else:
            self.bottleneck_att = nn.Identity()

        # U-Net Decoder
        self.dec4 = DecoderBlock(512, 256, 256, use_attention=attention_type)
        self.dec3 = DecoderBlock(256, 128, 128, use_attention=attention_type)
        self.dec2 = DecoderBlock(128, 64, 64, use_attention=attention_type)
        self.dec1 = DecoderBlock(64, 64, 32, use_attention=attention_type)

        # Final upsample to original resolution (256x256)
        self.final_up = nn.Upsample(scale_factor=2, mode="bilinear", align_corners=True)
        self.change_head = nn.Sequential(
            nn.Conv2d(32, 16, kernel_size=3, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            nn.Conv2d(16, num_classes, kernel_size=1)
        )

        # Optional Semantic Change Type Head
        if num_semantic_classes > 0:
            self.semantic_head = nn.Sequential(
                nn.Conv2d(32, 32, kernel_size=3, padding=1, bias=False),
                nn.BatchNorm2d(32),
                nn.ReLU(inplace=True),
                nn.Conv2d(32, num_semantic_classes, kernel_size=1)
            )
        else:
            self.semantic_head = None

    def _fuse_diff(self, f1: torch.Tensor, f2: torch.Tensor, projector: nn.Module) -> torch.Tensor:
        """Concatenated feature fusion: concat(F1, F2, |F1 - F2|)"""
        diff = torch.abs(f1 - f2)
        cat = torch.cat([f1, f2, diff], dim=1)
        return F.relu(projector(cat), inplace=True)

    def extract_features(self, x: torch.Tensor) -> Tuple[torch.Tensor, ...]:
        x0 = self.initial(x)         # 64, 128x128
        x1 = self.layer1(self.maxpool(x0)) # 64, 64x64
        x2 = self.layer2(x1)         # 128, 32x32
        x3 = self.layer3(x2)         # 256, 16x16
        x4 = self.layer4(x3)         # 512, 8x8
        return x0, x1, x2, x3, x4

    def forward(
        self,
        t1: torch.Tensor,
        t2: torch.Tensor
    ) -> Dict[str, torch.Tensor]:
        # Shared encoder passes
        t1_feats = self.extract_features(t1)
        t2_feats = self.extract_features(t2)

        # Multi-scale difference feature fusion
        f0 = self._fuse_diff(t1_feats[0], t2_feats[0], self.fuse_init)
        f1 = self._fuse_diff(t1_feats[1], t2_feats[1], self.fuse1)
        f2 = self._fuse_diff(t1_feats[2], t2_feats[2], self.fuse2)
        f3 = self._fuse_diff(t1_feats[3], t2_feats[3], self.fuse3)
        f4 = self._fuse_diff(t1_feats[4], t2_feats[4], self.fuse4)

        # Bottleneck
        b = self.bottleneck_att(f4)

        # Decoder with Skip Connections
        d4 = self.dec4(b, f3)
        d3 = self.dec3(d4, f2)
        d2 = self.dec2(d3, f1)
        d1 = self.dec1(d2, f0)

        # Final prediction heads
        d_out = self.final_up(d1)
        change_logits = self.change_head(d_out)

        out = {"change_logits": change_logits}
        if self.semantic_head is not None:
            out["semantic_logits"] = self.semantic_head(d_out)

        return out

    def freeze_encoder(self, freeze: bool = True):
        """Stage 1 training: freeze shared encoder weights."""
        layers = [self.initial, self.layer1, self.layer2, self.layer3, self.layer4]
        for layer in layers:
            for param in layer.parameters():
                param.requires_grad = not freeze

    def unfreeze_later_layers(self):
        """Stage 2 training: unfreeze later ResNet blocks (layer3, layer4)."""
        for param in self.layer3.parameters():
            param.requires_grad = True
        for param in self.layer4.parameters():
            param.requires_grad = True
