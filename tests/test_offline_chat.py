import os
import sys
import io
from pathlib import Path
from PIL import Image
import numpy as np

# sys.path.insert(0, r"f:\natraj26227")
sys.path.insert(0, r"g:\natraj26227")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from fastapi.testclient import TestClient
from project_code.api.app import app

def run_tests():
    client = TestClient(app)
    print("=================================================================")
    print("SIH-227: TESTING 100% OFFLINE MULTIMODAL CHAT ASSISTANT ENDPOINT")
    print("=================================================================")

    # -------------------------------------------------------------
    # TEST 1: Text-Only Query (Air-gap & System Consultation)
    # -------------------------------------------------------------
    print("\n[TEST 1] Sending text-only query: 'What model architecture do you use for defense?'")
    res = client.post(
        "/api/chat-query",
        data={"query": "What model architecture do you use for defense?", "threshold": 0.40}
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert data["status"] == "success"
    assert data["mode"] == "text_consultation"
    assert "Siamese ResNet-18" in data["answer_markdown"]
    print(f" -> PASS: Received answer ({data['latency_ms']} ms)")
    print(f" -> Markdown Snippet:\n{data['answer_markdown'][:200]}...\n")

    # -------------------------------------------------------------
    # TEST 2: Single Image Reconnaissance Query
    # -------------------------------------------------------------
    print("\n[TEST 2] Sending single satellite image query: 'Analyze land cover and detect structures'")
    # sample_path = Path("f:/natraj26227/datasets/LEVIR CD/test/A/test_10.png")
    sample_path = Path("g:/natraj26227/datasets/LEVIR CD/test/A/test_10.png")
    if sample_path.exists():
        img_recon = Image.open(sample_path).convert("RGB")
    else:
        # Fallback synthetic image
        img_recon = Image.fromarray((np.random.rand(256, 256, 3) * 255).astype(np.uint8))

    buf_recon = io.BytesIO()
    img_recon.save(buf_recon, format="PNG")
    buf_recon.seek(0)

    res = client.post(
        "/api/chat-query",
        data={"query": "Analyze land cover and detect structures in this target tile", "threshold": 0.40},
        files=[("files", ("recon.png", buf_recon.getvalue(), "image/png"))]
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert data["status"] == "success"
    assert data["mode"] == "single_image_characterization"
    assert "primary_class" in data["metrics"]
    assert len(data["suggested_followups"]) > 0
    print(f" -> PASS: Single image classified as '{data['metrics']['primary_class']}' ({data['latency_ms']} ms)")
    print(f" -> Tactical SITREP:\n{data['answer_markdown'][:250]}...\n")

    # -------------------------------------------------------------
    # TEST 3: Dual Image Bi-Temporal Change Detection Query
    # -------------------------------------------------------------
    print("\n[TEST 3] Sending dual satellite observations (T1 & T2): 'What changed between these two dates?'")
    # p1 = Path("f:/natraj26227/datasets/LEVIR CD/test/A/test_10.png")
    # p2 = Path("f:/natraj26227/datasets/LEVIR CD/test/B/test_10.png")
    p1 = Path("g:/natraj26227/datasets/LEVIR CD/test/A/test_10.png")
    p2 = Path("g:/natraj26227/datasets/LEVIR CD/test/B/test_10.png")

    if p1.exists() and p2.exists():
        img1 = Image.open(p1).convert("RGB")
        img2 = Image.open(p2).convert("RGB")
    else:
        arr1 = np.ones((256, 256, 3), dtype=np.uint8) * 80
        arr2 = arr1.copy()
        arr2[60:160, 60:160, :] = 220
        img1 = Image.fromarray(arr1)
        img2 = Image.fromarray(arr2)

    b1, b2 = io.BytesIO(), io.BytesIO()
    img1.save(b1, format="PNG")
    img2.save(b2, format="PNG")

    res = client.post(
        "/api/chat-query",
        data={
            "query": "Identify any unauthorized new building construction or ground clearance between T1 and T2",
            "threshold": 0.40,
            "model_type": "siamese_resnet18_cbam"
        },
        files=[
            ("files", ("t1.png", b1.getvalue(), "image/png")),
            ("files", ("t2.png", b2.getvalue(), "image/png"))
        ]
    )
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
    data = res.json()
    assert data["status"] == "success"
    assert data["mode"] == "bi_temporal_change"
    assert "change_percentage" in data["metrics"]
    assert "visuals" in data
    assert "overlay_base64" in data["visuals"]
    assert "mask_base64" in data["visuals"]
    print(f" -> PASS: Bi-temporal change SITREP generated successfully ({data['latency_ms']} ms)")
    print(f" -> Change detected: {data['metrics']['change_detected']} ({data['metrics']['change_percentage']}%)")
    print(f" -> Primary change type: {data['metrics']['primary_class']}")
    print(f" -> Number of discrete clusters: {data['metrics']['num_clusters']}")
    print(f" -> Visual overlays produced: T1, T2, Mask, Overlay")
    print(f" -> Follow-ups: {data['suggested_followups']}")
    print("\nALL OFFLINE MULTIMODAL CHAT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
