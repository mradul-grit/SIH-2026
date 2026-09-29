import os
import sys
import numpy as np
from PIL import Image
import torch

# sys.path.insert(0, r"f:\natraj26227")
sys.path.insert(0, r"g:\natraj26227")

from project_code.models.siamese_resnet18 import SiameseResNet18UNet

def test_pair(name, t1_path, t2_path, label_path, model, device, threshold=0.5):
    t1_img = Image.open(t1_path).convert("RGB")
    t2_img = Image.open(t2_path).convert("RGB")
    gt_mask = np.array(Image.open(label_path).convert("L")) > 0

    orig_w, orig_h = t1_img.size

    # Test 1: Full resize to 256x256 (what app.py was doing)
    t1_resized = t1_img.resize((256, 256))
    t2_resized = t2_img.resize((256, 256))
    gt_resized = np.array(Image.fromarray(gt_mask.astype(np.uint8)*255).resize((256, 256), Image.NEAREST)) > 0

    arr1 = np.array(t1_resized).astype(np.float32) / 255.0
    arr2 = np.array(t2_resized).astype(np.float32) / 255.0

    t1_t = torch.from_numpy(arr1.transpose(2, 0, 1)).unsqueeze(0).float().to(device)
    t2_t = torch.from_numpy(arr2.transpose(2, 0, 1)).unsqueeze(0).float().to(device)

    with torch.no_grad():
        out = model(t1_t, t2_t)
        logits = out["change_logits"].squeeze().cpu().numpy()
        probs_resized = 1.0 / (1.0 + np.exp(-logits))
        pred_resized = probs_resized > threshold

    # Test 2: Native 256x256 crop without downsampling
    crop_x = min(orig_w - 256, max(0, (orig_w - 256)//2))
    crop_y = min(orig_h - 256, max(0, (orig_h - 256)//2))
    
    t1_crop = t1_img.crop((crop_x, crop_y, crop_x + 256, crop_y + 256))
    t2_crop = t2_img.crop((crop_x, crop_y, crop_x + 256, crop_y + 256))
    gt_crop = gt_mask[crop_y : crop_y + 256, crop_x : crop_x + 256]

    arr1_c = np.array(t1_crop).astype(np.float32) / 255.0
    arr2_c = np.array(t2_crop).astype(np.float32) / 255.0

    t1_tc = torch.from_numpy(arr1_c.transpose(2, 0, 1)).unsqueeze(0).float().to(device)
    t2_tc = torch.from_numpy(arr2_c.transpose(2, 0, 1)).unsqueeze(0).float().to(device)

    with torch.no_grad():
        out_c = model(t1_tc, t2_tc)
        logits_c = out_c["change_logits"].squeeze().cpu().numpy()
        probs_crop = 1.0 / (1.0 + np.exp(-logits_c))
        pred_crop = probs_crop > threshold

    def get_metrics(p, g):
        tp = np.sum(p & g)
        fp = np.sum(p & ~g)
        fn = np.sum(~p & g)
        tn = np.sum(~p & ~g)
        prec = tp / (tp + fp + 1e-7)
        rec = tp / (tp + fn + 1e-7)
        f1 = 2 * prec * rec / (prec + rec + 1e-7)
        iou = tp / (tp + fp + fn + 1e-7)
        return {"f1": f1, "iou": iou, "prec": prec, "rec": rec, "gt_pos": int(np.sum(g)), "pred_pos": int(np.sum(p))}

    m_resized = get_metrics(pred_resized, gt_resized)
    m_crop = get_metrics(pred_crop, gt_crop)

    print(f"\n--- Diagnostic on Pair: {name} (Orig size: {orig_w}x{orig_h}) ---")
    print(f"Probabilities Min/Mean/Max (Resized): {probs_resized.min():.3f} / {probs_resized.mean():.3f} / {probs_resized.max():.3f}")
    print(f"Probabilities Min/Mean/Max (Native Crop): {probs_crop.min():.3f} / {probs_crop.mean():.3f} / {probs_crop.max():.3f}")
    print(f"  [Resized 256x256]: GT Changed Pixels: {m_resized['gt_pos']} | Pred Changed Pixels: {m_resized['pred_pos']} | F1: {m_resized['f1']:.4f} | IoU: {m_resized['iou']:.4f} | Rec: {m_resized['rec']:.4f}")
    print(f"  [Native Crop 256]: GT Changed Pixels: {m_crop['gt_pos']} | Pred Changed Pixels: {m_crop['pred_pos']} | F1: {m_crop['f1']:.4f} | IoU: {m_crop['iou']:.4f} | Rec: {m_crop['rec']:.4f}")

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Running Ground Truth Diagnostic on:", device)

    # Test baseline vs unified
    checkpoints = [
        # ("LEVIR Baseline", r"f:\natraj26227\experiments\levir_baseline\model.pt"),
        # ("Unified 5-Dataset", r"f:\natraj26227\experiments\unified_5datasets_cbam\model.pt")
        ("LEVIR Baseline", r"g:\natraj26227\experiments\levir_baseline\model.pt"),
        ("Unified 5-Dataset", r"g:\natraj26227\experiments\unified_5datasets_cbam\model.pt")
    ]

    # Find sample pairs with known changes in LEVIR-CD test
    # test_a_dir = r"f:\natraj26227\datasets\LEVIR CD\test\A"
    # test_b_dir = r"f:\natraj26227\datasets\LEVIR CD\test\B"
    # test_l_dir = r"f:\natraj26227\datasets\LEVIR CD\test\label"
    test_a_dir = r"g:\natraj26227\datasets\LEVIR CD\test\A"
    test_b_dir = r"g:\natraj26227\datasets\LEVIR CD\test\B"
    test_l_dir = r"g:\natraj26227\datasets\LEVIR CD\test\label"

    # Pick 3 files that have real positive changes (> 1000 pixels)
    valid_pairs = []
    for f in sorted(os.listdir(test_l_dir)):
        p = os.path.join(test_l_dir, f)
        arr = np.array(Image.open(p).convert("L"))
        if np.sum(arr > 0) > 2000:
            valid_pairs.append(f)
            if len(valid_pairs) >= 3:
                break

    print("Found test pairs with real changes:", valid_pairs)

    for ckpt_name, ckpt_path in checkpoints:
        print(f"\n=======================================================")
        print(f"EVALUATING MODEL: {ckpt_name}")
        print(f"=======================================================")
        model = SiameseResNet18UNet(pretrained=False, attention_type="cbam", num_semantic_classes=0)
        model.load_state_dict(torch.load(ckpt_path, map_location=device))
        model.to(device)
        model.eval()

        for f in valid_pairs:
            t1_p = os.path.join(test_a_dir, f)
            t2_p = os.path.join(test_b_dir, f)
            l_p = os.path.join(test_l_dir, f)
            test_pair(f, t1_p, t2_p, l_p, model, device, threshold=0.35)

if __name__ == "__main__":
    main()
