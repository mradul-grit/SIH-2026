import os
import sys
import numpy as np
from PIL import Image
import torch

# sys.path.insert(0, r"f:\natraj26227")
sys.path.insert(0, r"g:\natraj26227")

from project_code.models.siamese_resnet18 import SiameseResNet18UNet

def tiled_inference(img1, img2, model, device, patch_size=256, stride=256, threshold=0.40):
    w, h = img1.size
    arr1 = np.array(img1).astype(np.float32) / 255.0
    arr2 = np.array(img2).astype(np.float32) / 255.0

    prob_map = np.zeros((h, w), dtype=np.float32)
    count_map = np.zeros((h, w), dtype=np.float32)

    # Coordinates
    y_coords = list(range(0, h - patch_size + 1, stride))
    if y_coords[-1] + patch_size < h:
        y_coords.append(h - patch_size)

    x_coords = list(range(0, w - patch_size + 1, stride))
    if x_coords[-1] + patch_size < w:
        x_coords.append(w - patch_size)

    for y in y_coords:
        for x in x_coords:
            p1 = arr1[y : y + patch_size, x : x + patch_size, :]
            p2 = arr2[y : y + patch_size, x : x + patch_size, :]

            t1_t = torch.from_numpy(p1.transpose(2, 0, 1)).unsqueeze(0).float().to(device)
            t2_t = torch.from_numpy(p2.transpose(2, 0, 1)).unsqueeze(0).float().to(device)

            with torch.no_grad():
                out = model(t1_t, t2_t)
                logits = out["change_logits"].squeeze().cpu().numpy()
                probs = 1.0 / (1.0 + np.exp(-logits))

            prob_map[y : y + patch_size, x : x + patch_size] += probs
            count_map[y : y + patch_size, x : x + patch_size] += 1.0

    count_map[count_map == 0] = 1.0
    avg_probs = prob_map / count_map
    pred_mask = (avg_probs > threshold).astype(np.uint8)
    return pred_mask, avg_probs

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # ckpt_path = r"f:\natraj26227\experiments\unified_5datasets_cbam\model.pt"
    ckpt_path = r"g:\natraj26227\experiments\unified_5datasets_cbam\model.pt"

    model = SiameseResNet18UNet(pretrained=False, attention_type="cbam", num_semantic_classes=0)
    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    model.to(device)
    model.eval()

    test_files = ["test_10.png", "test_100.png", "test_14.png"]
    for f in test_files:
        # p1 = f"f:/natraj26227/datasets/LEVIR CD/test/A/{f}"
        # p2 = f"f:/natraj26227/datasets/LEVIR CD/test/B/{f}"
        # pl = f"f:/natraj26227/datasets/LEVIR CD/test/label/{f}"
        p1 = f"g:/natraj26227/datasets/LEVIR CD/test/A/{f}"
        p2 = f"g:/natraj26227/datasets/LEVIR CD/test/B/{f}"
        pl = f"g:/natraj26227/datasets/LEVIR CD/test/label/{f}"

        if not os.path.exists(pl):
            continue

        img1 = Image.open(p1).convert("RGB")
        img2 = Image.open(p2).convert("RGB")
        gt_mask = np.array(Image.open(pl).convert("L")) > 0

        # 1. Old App Method: Direct resize 1024 -> 256
        t1_small = img1.resize((256, 256))
        t2_small = img2.resize((256, 256))
        a1_s = np.array(t1_small).astype(np.float32) / 255.0
        a2_s = np.array(t2_small).astype(np.float32) / 255.0
        with torch.no_grad():
            out_s = model(
                torch.from_numpy(a1_s.transpose(2, 0, 1)).unsqueeze(0).float().to(device),
                torch.from_numpy(a2_s.transpose(2, 0, 1)).unsqueeze(0).float().to(device)
            )
            probs_s = 1.0 / (1.0 + np.exp(-out_s["change_logits"].squeeze().cpu().numpy()))
            pred_s_256 = probs_s > 0.35
            # Upscale back to 1024
            pred_s_full = np.array(Image.fromarray(pred_s_256.astype(np.uint8)*255).resize((1024, 1024), Image.NEAREST)) > 0

        # 2. New Tiled Method: Native Resolution Sliding Window (patch 256, stride 256)
        pred_tiled, probs_tiled = tiled_inference(img1, img2, model, device, patch_size=256, stride=256, threshold=0.35)

        def eval_m(pred, gt):
            tp = np.sum(pred & gt)
            fp = np.sum(pred & ~gt)
            fn = np.sum(~pred & gt)
            p = tp / (tp + fp + 1e-7)
            r = tp / (tp + fn + 1e-7)
            f1 = 2 * p * r / (p + r + 1e-7)
            iou = tp / (tp + fp + fn + 1e-7)
            return f1, iou, p, r, int(np.sum(gt)), int(np.sum(pred))

        f1_old, iou_old, p_old, r_old, gt_cnt, pred_old_cnt = eval_m(pred_s_full, gt_mask)
        f1_new, iou_new, p_new, r_new, _, pred_new_cnt = eval_m(pred_tiled, gt_mask)

        print(f"\n=======================================================")
        print(f"Full 1024x1024 Scene Evaluation: {f}")
        print(f"Ground Truth Change Pixels: {gt_cnt:,} ({gt_cnt/1048576*100:.2f}%)")
        print(f"  [Old Resize Method]: Pred Pixels: {pred_old_cnt:,} | F1: {f1_old:.4f} | IoU: {iou_old:.4f} | Recall: {r_old*100:.1f}%")
        print(f"  [New Tiled Method ]: Pred Pixels: {pred_new_cnt:,} | F1: {f1_new:.4f} | IoU: {iou_new:.4f} | Recall: {r_new*100:.1f}%")
        print(f"  --> F1 GAIN: +{(f1_new - f1_old)*100:.1f} percentage points! Recall GAIN: +{(r_new - r_old)*100:.1f}%!")

if __name__ == "__main__":
    main()
