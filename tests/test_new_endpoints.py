import urllib.request
import json
import urllib.parse

base_url = "http://127.0.0.1:8000"

# 1. Health check
print("[TEST] 1. Checking Health Endpoint...")
with urllib.request.urlopen(f"{base_url}/api/health") as res:
    print("Health Status:", json.loads(res.read()))

# 2. GeoJSON Export
print("\n[TEST] 2. Checking RFC 7946 GeoJSON Export...")
with urllib.request.urlopen(f"{base_url}/api/export-geojson/test_10?change_pct=9.72&confidence=0.938") as res:
    geojson_data = json.loads(res.read())
    print("GeoJSON Type:", geojson_data.get("type"))
    print("Feature Count:", len(geojson_data.get("features", [])))
    print("Properties:", geojson_data["features"][0]["properties"])
    assert geojson_data["type"] == "FeatureCollection"
    assert "provenance_hash_sha256" in geojson_data["features"][0]["properties"]
    print("--> GeoJSON Export: PASSED!")

# 3. Temporal Bisection Search
print("\n[TEST] 3. Checking O(log N) Temporal Bisection Search...")
req_data = json.dumps({
    "sequence_length": 16,
    "change_onset_index": 7,
    "change_threshold": 0.50
}).encode("utf-8")

req = urllib.request.Request(
    f"{base_url}/api/temporal-bisect",
    data=req_data,
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as res:
    bisect_data = json.loads(res.read())
    print("Bisection Result Status:", bisect_data.get("status"))
    print("Earliest Timestamp:", bisect_data.get("earliest_timestamp"))
    print("Earliest Index:", bisect_data.get("earliest_index"))
    print("Steps Evaluated:", bisect_data.get("steps_evaluated"))
    print("Theoretical Bound:", bisect_data.get("theoretical_o_log_n_bound"))
    assert bisect_data["earliest_index"] == 7
    assert bisect_data["steps_evaluated"] == 4
    print("--> Temporal Bisection: PASSED!")

# 4. Active Learning Feedback
print("\n[TEST] 4. Checking Active Learning Feedback...")
fb_data = json.dumps({
    "tile_id": "test_10",
    "query_text": "new construction near road",
    "action": "CONFIRM"
}).encode("utf-8")
req = urllib.request.Request(
    f"{base_url}/api/feedback",
    data=fb_data,
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as res:
    fb_res = json.loads(res.read())
    print("Feedback Response:", fb_res)
    assert fb_res["status"] == "feedback_incorporated"
    print("--> Active Learning: PASSED!")

print("\nALL API ENDPOINT VERIFICATIONS PASSED SUCCESSFULLY!")
