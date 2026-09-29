import io
import requests
from PIL import Image

img1 = Image.new("RGB", (256, 256), color=(40, 80, 40))
img2 = Image.new("RGB", (256, 256), color=(45, 85, 45))

buf1 = io.BytesIO()
img1.save(buf1, format="PNG")

buf2 = io.BytesIO()
img2.save(buf2, format="PNG")

for m in ["siamese_resnet18_cbam", "changeformer"]:
    buf1.seek(0)
    buf2.seek(0)
    files = {
        "file_t1": ("t1.png", buf1.getvalue(), "image/png"),
        "file_t2": ("t2.png", buf2.getvalue(), "image/png")
    }
    data = {"model_type": m, "threshold": 0.40}
    res = requests.post("http://127.0.0.1:8000/api/change-detect", files=files, data=data)
    assert res.status_code == 200, f"Error: {res.text}"
    rj = res.json()
    print(f"Tested: {m} -> Model used: {rj.get('model_used')} | Latency: {rj.get('latency_ms')} ms | Resolution: {rj.get('resolution')}")

print("\nDual Model Inference verification: PASSED!")
