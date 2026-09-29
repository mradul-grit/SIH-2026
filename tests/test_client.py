import io
import json
import urllib.request
from PIL import Image

def test_inference():
    # Create two 256x256 images: T1 empty background, T2 with a new building
    img1 = Image.new('RGB', (256, 256), color=(40, 60, 30))
    img2 = Image.new('RGB', (256, 256), color=(40, 60, 30))
    # Add new building at (80, 80)
    building = Image.new('RGB', (60, 60), color=(220, 220, 220))
    img2.paste(building, (80, 80))

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
        '0.50\r\n'
        f'--{boundary}--\r\n'
    ).encode('utf-8')

    req = urllib.request.Request(
        'http://127.0.0.1:8000/api/change-detect',
        data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
    )

    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print("=== LIVE INFERENCE RESULT ===")
        print("Change Detected:", res["change_detected"])
        print("Change Pixels:", res["change_pixels"])
        print("Change Percentage:", res["change_percentage"], "%")
        print("Confidence Score:", res["confidence"])
        print("Inference Latency:", res["latency_ms"], "ms")
        print("Registration Status:", res["registration"]["status"])
        print("Radiometric Quality:", res["radiometric_quality"]["quality_score"])

if __name__ == "__main__":
    test_inference()
