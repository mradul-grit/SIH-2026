import io
import json
import urllib.request
import numpy as np
from PIL import Image

def test_building_change():
    # T1: pure field
    arr1 = np.ones((256, 256, 3), dtype=np.uint8) * 50
    arr1[:, :, 1] = 80 # greenish field

    # T2: add high-contrast bright building (100x100 pixels)
    arr2 = arr1.copy()
    arr2[60:160, 60:160, :] = 220 # bright building structure

    img1 = Image.fromarray(arr1)
    img2 = Image.fromarray(arr2)

    b1, b2 = io.BytesIO(), io.BytesIO()
    img1.save(b1, 'PNG')
    img2.save(b2, 'PNG')

    boundary = '----CustomBoundary12345'
    body = (
        f'--{boundary}\r\n'
        'Content-Disposition: form-data; name="file_t1"; filename="t1.png"\r\n'
        'Content-Type: image/png\r\n\r\n'
    ).encode('utf-8') + b1.getvalue() + (
        f'\r\n--{boundary}\r\n'
        'Content-Disposition: form-data; name="file_t2"; filename="t2.png"\r\n'
        'Content-Type: image/png\r\n\r\n'
    ).encode('utf-8') + b2.getvalue() + (
        f'\r\n--{boundary}\r\n'
        'Content-Disposition: form-data; name="threshold"\r\n\r\n'
        '0.30\r\n'
        f'--{boundary}--\r\n'
    ).encode('utf-8')

    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/change-detect',
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )

    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("=== LIVE CHANGE DETECTION VERIFICATION ===")
        print("Change Detected:", res["change_detected"])
        print("Change Pixels:", res["change_pixels"])
        print("Change Percentage:", res["change_percentage"], "%")
        print("Confidence Score:", res["confidence"])
        print("Inference Latency:", res["latency_ms"], "ms")
        print("Registration:", res["registration"]["status"])
        print("Overlay image generated:", len(res["images"]["overlay_base64"]) > 100)

if __name__ == "__main__":
    test_building_change()
